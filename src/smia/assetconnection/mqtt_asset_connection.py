import asyncio
import json
import logging
import time
from typing import Optional
from urllib.parse import unquote, urlparse

import aiomqtt

from smia.logic.exceptions import AssetConnectionError

from smia.utilities.smia_info import AssetInterfacesInfo
from smia.assetconnection.asset_connection import AssetConnection

_logger = logging.getLogger(__name__)

# Upper bound for the last-known-value cache (avoids unbounded growth with wildcards)
MAX_CACHED_TOPICS = 500

class MQTTAssetConnection(AssetConnection):
    """
    This class implements the asset connection for MQTT protocol. It inherits from the valid official class defined by
    SMIA.

    Coroutine-safe: a single persistent ``aiomqtt.Client`` session is shared by all concurrent SPADE behaviours.
    Per-request data travels in local variables.
    """

    def __init__(self):
        super().__init__()
        self.architecture_style = AssetConnection.ArchitectureStyle.PUBSUB

        # Common data (configuration)
        self.interface_title = None
        self.base = None
        self.endpoint_metadata_elem = None
        self.security_scheme_elem = None
        self.default_content_type = 'application/json'

        # Data of the persistent MQTT session (shared by all requests)
        self.broker = None
        self.port = 1883
        self.use_tls = False

        # Operational parameters (change is necessary)
        self.default_subscribe_timeout = 60.0
        self.cache_ttl_seconds = 30.0   # Time that subscription values are retained
        self.keepalive = 60

        # Lifecycle of the persistent session
        # The dispatcher task only exists while there is something to listen for.
        self.mqtt_client: Optional[aiomqtt.Client] = None
        self._connected_event = asyncio.Event()
        self._dispatcher_task: Optional[asyncio.Task] = None
        self._dispatcher_client: Optional[aiomqtt.Client] = None
        self._connection_lock = asyncio.Lock()
        self._subscription_lock = asyncio.Lock()

        # Dispatcher state
        self._active_subscriptions: dict = {}
        # Pending waiters for fan-out
        self._waiters: dict = {}
        # Last known value cache
        self._last_values: dict = {}

    async def configure_connection_by_aas_model(self, interface_aas_elem):
        # The Interface element is first checked
        await self.check_interface_element(interface_aas_elem)

        # Let's retrieve the necessary data from the AAS model to configure the MQTT connection
        self.interface_title = interface_aas_elem.get_sm_element_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_INTERFACE_TITLE)
        # General information about the connection to the asset is defined in the SMC 'EndpointMetadata'
        self.endpoint_metadata_elem = interface_aas_elem.get_sm_element_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_ENDPOINT_METADATA)

        # The endpointMetadata element need to be checked
        await self.check_endpoint_metadata()

        self.base = self.endpoint_metadata_elem.get_sm_element_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_INTERFACE_BASE)
        content_type_elem = self.endpoint_metadata_elem.get_sm_element_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_INTERFACE_CONTENT_TYPE)
        if content_type_elem is not None and getattr(content_type_elem, 'value', None):
            self.default_content_type = str(content_type_elem.value).strip()

        security_definitions_elem = self.endpoint_metadata_elem.get_sm_element_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_INTERFACE_SECURITY_DEFINITIONS)
        if security_definitions_elem is not None:
            self.security_scheme_elem = security_definitions_elem.value
        # TODO: pensar como añadir el resto , p.e. tema de seguridad o autentificacion (bearer).
        #  De momento se ha dejado sin seguridad (nosec_sc)

        # The InteractionMetadata elements also need to be checked
        interaction_metadata_elem = interface_aas_elem.get_sm_element_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_INTERACTION_METADATA)
        for interaction_metadata_type in interaction_metadata_elem:
            # Interaction metadata can be properties, actions or events
            for interaction_element in interaction_metadata_type:
                await self.check_interaction_metadata(interaction_element)

        # We extract the broker and port from the base
        if self.base is not None and getattr(self.base, 'value', None):
            self.broker, self.port, self.use_tls = self._parse_broker_uri(str(self.base.value))

    async def check_asset_connection(self):
        """
        This method checks whether the persistent MQTT session is currently active.

        Returns:
            bool: True if the client is connected to the broker, False otherwise.
        """
        return self._connected_event.is_set() and self.mqtt_client is not None

    async def connect_with_asset(self):
        """
        This method ensures that the persistent MQTT session exists right now (pre-warm).
        It is idempotent: simultaneous or repeated calls never open more than one session.
        No background task is started; the session stays open until 'disconnect'.
        """
        await self._ensure_connected_client(self.default_subscribe_timeout)

    async def disconnect(self):
        """
        This method cleanly closes the persistent MQTT session, stopping the dispatcher
        (if running).
        """
        self._stop_dispatcher()
        async with self._connection_lock:
            client, self.mqtt_client = self.mqtt_client, None
            self._connected_event.clear()
            if client is not None:
                try:
                    await client.__aexit__(None, None, None)
                except Exception:
                    _logger.debug("Error while closing the MQTT client", exc_info=True)
        # Abort any behaviour still waiting for a message
        for topic_filter, futures in list(self._waiters.items()):
            for fut in futures:
                if not fut.done():
                    fut.set_exception(AssetConnectionError(
                        "MQTT connection closed while waiting on topic '{}'.".format(topic_filter),
                        "ConnectionClosed", "Asset connection disconnect"))
        self._waiters.clear()
        _logger.info("MQTT connection closed for broker %s:%s", self.broker, self.port)

    async def execute_asset_service(self, interaction_metadata, service_input_data=None):
        if interaction_metadata is None:
            raise AssetConnectionError("The skill cannot be executed by asset service because the given "
                                       "InteractionMetadata object is None", "invalid method parameter",
                                       "InteractionMetadata object is None")

        # All per-request data is extracted into local variables (coroutine-safe)
        topic, qos, retain, control_packet = await self.extract_general_interaction_metadata(
            interaction_metadata)

        request_body = None
        if control_packet == 'publish' and self._has_input_data(service_input_data):
            # Then, the data of the skill is added in the required field. To do that, the 'SkillParameterExposedThrough'
            # relationship should be obtained, which indicates where the parameter data should be added
            request_body = await self.add_asset_service_data(interaction_metadata, service_input_data)

        # At this point, the MQTT request is performed over the shared persistent session.
        mqtt_response = await self.send_mqtt_request(topic, control_packet, qos, retain,
                                                     request_body)
        if control_packet == 'subscribe':
            # The success is logged only after the payload has been transformed into a usable value
            try:
                response = await self._build_subscribe_response(interaction_metadata, mqtt_response)
            except AssetConnectionError:
                raise
            except Exception as e:
                raise AssetConnectionError("The subscribed MQTT message could not be processed.",
                                           e.__class__.__name__, str(e)) from e
            _logger.assetinfo("MQTT communication successfully completed.")
            return response
        if mqtt_response:
            _logger.assetinfo("MQTT communication successfully completed.")
            return True
        return None

    async def receive_msg_from_asset(self):
        """
        This method waits for the next message received on any of the currently active
        subscriptions and returns it.

        Returns:
            bytes: raw payload of the received message.
        """
        if not self._active_subscriptions:
            raise AssetConnectionError("There is no active MQTT subscription to receive messages from.",
                                       "NoActiveSubscription", "receive_msg_from_asset without subscribe")
        await self._ensure_connected_client(self.default_subscribe_timeout)
        loop = asyncio.get_running_loop()
        waiter = loop.create_future()
        waiters = self._waiters.setdefault('#', set())
        waiters.add(waiter)
        self._ensure_dispatcher()
        try:
            return await asyncio.wait_for(waiter, timeout=self.default_subscribe_timeout)
        except asyncio.TimeoutError as timeout_error:
            raise AssetConnectionError(
                "Timeout ({}s) waiting for an MQTT message on the active subscriptions.".format(
                    self.default_subscribe_timeout),"MQTTReceiveTimeout",
                "No message received in time") from timeout_error
        finally:
            waiters.discard(waiter)
            if not waiters:
                self._waiters.pop('#', None)
            self._maybe_stop_dispatcher()

    # ---------------------
    # MQTT specific methods
    # ---------------------
    async def extract_general_interaction_metadata(self, interaction_metadata):
        """
        This method extracts the general interaction information from the interaction metadata object. Since this is an
        MQTT Asset Connection, information about the topic, QoS, retain and control packet is obtained.

        Args:
             interaction_metadata (basyx.aas.model.SubmodelElementCollection): SubmodelElement of interactionMetadata.

        Returns:
            tuple: (topic, qos, retain, control_packet) of this interaction.
        """
        # The interaction_metada element will be an SMC of the MQTT interface.
        await self.check_interaction_metadata(interaction_metadata)

        # First, the full valid topic of the MQTT request is obtained.
        forms_elem = interaction_metadata.get_sm_element_by_semantic_id(AssetInterfacesInfo.SEMANTICID_INTERFACE_FORMS)

        topic = await self.get_topic(forms_elem)

        # Then, MQTT parameters are obtained
        qos, retain, control_packet = await self.get_mqtt_parameters(forms_elem)
        return topic, qos, retain, control_packet

    async def get_topic(self, forms_elem):
        """
        This method gets the complete request Topic from the forms element within the InteractionMetadata element.

        Args:
          forms_elem (basyx.aas.model.SubmodelElementCollection): SubmodelElement of forms within InteractionMetadata.

        Returns:
            str: complete request topic.
        """
        href_elem = forms_elem.get_sm_element_by_semantic_id(AssetInterfacesInfo.SEMANTICID_INTERFACE_HREF)
        if href_elem is None or not getattr(href_elem, 'value', None) \
                or not str(href_elem.value).strip():
            raise AssetConnectionError("The InteractionMetadata forms element does not define 'href'.",
                                       'Invalid interface SubmodelElement', 'MissingAttribute')
        topic, broker_override, _, _ = self._parse_mqtt_href(str(href_elem.value).strip())
        if broker_override is not None and broker_override != self.broker:
            raise AssetConnectionError(
                "The href of the interaction points to broker '{}', but this connection is configured "
                "for broker '{}'. A single MQTTAssetConnection handles a single broker.".format(
                    broker_override, self.broker),
                "MultiBrokerNotSupported", str(href_elem.value))
        return topic

    async def get_mqtt_parameters(self, forms_elem):
        """
        This method gets the MQTT specific parameters from the forms element within the InteractionMetadata element.

        Args:
            forms_elem (basyx.aas.model.SubmodelElementCollection): SubmodelElement of forms within InteractionMetadata.

        Returns:
            tuple: (qos, retain, control_packet) of this interaction.
        """
        retain_elem = forms_elem.get_sm_element_by_semantic_id(
            MQTTAssetInterfaceSemantics.SEMANTICID_MQTT_INTERFACE_RETAIN)
        if retain_elem is not None and retain_elem.value is not None:
            retain = str(retain_elem.value).lower() in ['true', '1']
        else:
            retain = False

        control_packet_elem = forms_elem.get_sm_element_by_semantic_id(
            MQTTAssetInterfaceSemantics.SEMANTICID_MQTT_INTERFACE_CONTROL_PACKET)
        if control_packet_elem is not None and control_packet_elem.value is not None \
                and str(control_packet_elem.value).strip():
            control_packet = str(control_packet_elem.value).strip().lower()
        else:
            control_packet = 'publish'

        qos_elem = forms_elem.get_sm_element_by_semantic_id(
            MQTTAssetInterfaceSemantics.SEMANTICID_MQTT_INTERFACE_QOS)
        if qos_elem is not None and qos_elem.value is not None:
            try:
                qos = int(str(qos_elem.value).strip())
                if qos not in (0, 1, 2):
                    _logger.warning("Invalid MQTT QoS value [%s], using QoS 0.", qos_elem.value)
                    qos = 0
            except ValueError:
                qos = 0
        else:
            qos = 0
        return qos, retain, control_packet

    async def add_asset_service_data(self, interaction_metadata, service_input_data):
        """
        This method adds the required data of the asset service, using the skill params information (exposure element
        and skill input data).

        Args:
            interaction_metadata (basyx.aas.model.SubmodelElementCollection): SubmodelElement of interactionMetadata.
            service_input_data (dict): dictionary containing the input data of the asset service.

        Returns:
            object: serialized payload of this request.
        """
        # TODO revisar si habria que añadir los parametros en el modelo AAS, de momento simplemente se añaden
        #  dependiendo el tipo
        return await self.serialize_data_by_content_type(interaction_metadata, service_input_data)

    async def serialize_data_by_content_type(self, interaction_metadata, service_data):
        """
        This method serializes the data for the given InteractionMetadata.

        Args:
            interaction_metadata(basyx.aas.model.SubmodelElementCollection): interactionMetadata Python object.
            service_data (dict): the data to be serialized in JSON format.

        Returns:
            str: service data in the content-type format.
        """
        if isinstance(service_data, (bytes, bytearray)):
            return bytes(service_data)
        if isinstance(service_data, str):
            return service_data

        content_type = await self.get_interaction_metadata_content_type(interaction_metadata)
        if content_type is None or getattr(content_type, 'value', None) is None:
            return json.dumps(service_data)

        mime_type = str(content_type.value).split(';')[0].strip().lower()
        if mime_type == 'application/json':
            return json.dumps(service_data)   # Data should be sent in string format
        elif mime_type == 'text/plain':
            if isinstance(service_data, dict) and len(service_data) == 1:
                return str(next(iter(service_data.values())))
            return json.dumps(service_data)
        elif mime_type == 'application/xml':
            _logger.warning("XML serialization is not supported for MQTT asset connection.")
            return json.dumps(service_data)  # Add the method to convert a JSON into XML
        else:
            return str(service_data)

    async def send_mqtt_request(self, topic, control_packet, qos, retain, payload):
        """
        This method performs the required MQTT interaction with the asset through the shared
        persistent session. All the required information travels as explicit arguments, so
        concurrent calls never overwrite each other.

        Args:
            topic (str): topic of the interaction.
            control_packet (str): 'publish', 'subscribe' or 'unsubscribe'.
            qos (int): QoS flag of the interaction (0, 1 or 2).
            retain (bool): retain flag of the interaction.
            payload: payload to publish (only used with 'publish').

        Returns:
            object: True for `publish`/`unsubscribe`; raw payload bytes for `subscribe`.
        """
        if not self.broker:
            raise AssetConnectionError("MQTT broker is not defined.", "BrokerNotDefined", "Missing Broker")

        if topic is None:
            raise AssetConnectionError("MQTT topic is not defined.", "TopicNotDefined", "Missing Topic")

        try:
            if control_packet in ['publish']:
                return await self._handle_publish(topic, qos, retain, payload,
                                                  self.default_subscribe_timeout)
            elif control_packet == 'subscribe':
                return await self._handle_subscribe(topic, qos, retain,
                                                    self.default_subscribe_timeout)
            elif control_packet == 'unsubscribe':
                return await self._handle_unsubscribe(topic, self.default_subscribe_timeout)
            else:
                _logger.warning("Control packet {} is not supported for execute_asset_"
                                "service.".format(control_packet))
                raise AssetConnectionError(
                    "Unsupported MQTT control packet '{}'.".format(control_packet),
                    "UnsupportedControlPacket", str(control_packet))
        except AssetConnectionError:
            raise
        except aiomqtt.MqttError as error:
            raise AssetConnectionError("The connection with the asset has raised an MQTT exception.",
                                       error.__class__.__name__, str(error)) from error
        except Exception as e:
            raise AssetConnectionError("The connection with the asset has raised an exception.",
                                       e.__class__.__name__, str(e)) from e

    async def _handle_publish(self, topic, qos, retain, payload, timeout):
        """Publishes the given payload on the given topic through the persistent session."""
        client = await self._ensure_connected_client(timeout)
        data = payload if payload is not None else ""
        await client.publish(topic, payload=data, qos=qos, retain=retain, timeout=timeout)
        _logger.debug("Published message on topic '%s' (QoS=%s, Retain=%s)",
                      topic, qos, retain)
        return True

    async def _handle_subscribe(self, topic, qos, retain, timeout):
        """
        Subscribes to the request topic (if not already subscribed) and waits for at least
        one message, applying fan-out: every concurrent waiter on the same topic filter
        receives its own copy of the payload.

        If the interaction declares `retain=True` and a last-known value is already cached
        for the exact topic, it is returned immediately; otherwise a new message is awaited.
        """
        client = await self._ensure_connected_client(timeout)

        # Fast path for state-like properties: a retained last-known value is returned at once.
        if retain and '+' not in topic and '#' not in topic:
            cached = self._last_values.get(topic)
            if cached is not None:
                cached_payload, cached_timestamp = cached
                if self.cache_ttl_seconds <= 0 \
                        or (time.monotonic() - cached_timestamp) <= self.cache_ttl_seconds:
                    _logger.debug("Returning cached last-known value for topic '%s'", topic)
                    return cached_payload

        loop = asyncio.get_running_loop()
        waiter = loop.create_future()
        # The waiter is registered before subscribing, so retained messages delivered
        # immediately after SUBACK can never be lost.
        waiters = self._waiters.setdefault(topic, set())
        waiters.add(waiter)

        refcounted = False
        try:
            async with self._subscription_lock:
                subscription = self._active_subscriptions.get(topic)
                if subscription is None:
                    await client.subscribe(topic, qos=qos, timeout=timeout)
                    self._active_subscriptions[topic] = {'qos': qos, 'refcount': 1}
                else:
                    subscription['refcount'] += 1
                    if qos > subscription['qos']:
                        await client.subscribe(topic, qos=qos, timeout=timeout)
                        subscription['qos'] = qos
                refcounted = True

            # Start the dispatcher on demand (only while there is something to listen for)
            self._ensure_dispatcher()
            return await asyncio.wait_for(waiter, timeout=timeout)
        except asyncio.TimeoutError as timeout_error:
            raise AssetConnectionError(
                "Timeout ({}s) waiting for MQTT message on topic '{}'.".format(timeout, topic),
                "MQTTSubscribeTimeout", "No message received in time") from timeout_error
        except asyncio.CancelledError:
            raise
        finally:
            # The waiter is always released, even on timeout or cancellation...
            waiters.discard(waiter)
            if not waiters:
                self._waiters.pop(topic, None)
            # ...and a subscribe that never got its message does not hold a subscription slot,
            # so a timed-out/cancelled caller cannot leak refcount entries.
            if refcounted and not self._waiter_succeeded(waiter):
                await self._release_subscription_slot(topic)

    async def _handle_unsubscribe(self, topic, timeout):
        """
        Releases one subscription slot on the request topic. The broker-level UNSUBSCRIBE
        is only sent when the last interested behaviour unsubscribes (refcount reaches 0),
        so concurrent subscribers are never affected. The last-known-value cache is kept
        to allow immediate retained reads on future subscribes. No connection is opened
        just to unsubscribe: if the session is down there is nothing broker-side to clean.
        """
        async with self._subscription_lock:
            subscription = self._active_subscriptions.get(topic)
            if subscription is None:
                # Nothing tracked: best-effort broker-level unsubscribe only if connected.
                client = self.mqtt_client if self._connected_event.is_set() else None
                if client is not None:
                    try:
                        await client.unsubscribe(topic, timeout=timeout)
                    except Exception:
                        _logger.debug("Best-effort unsubscribe from topic '%s' failed",
                                      topic, exc_info=True)
                return True
            subscription['refcount'] -= 1
            if subscription['refcount'] > 0:
                _logger.debug("Released one subscriber of topic '%s' (%d remaining)",
                              topic, subscription['refcount'])
                return True
            # Last subscriber: cancel the broker-level subscription.
            del self._active_subscriptions[topic]
            pending = self._waiters.pop(topic, set())
            for fut in pending:
                if not fut.done():
                    fut.set_exception(AssetConnectionError(
                        "Topic '{}' was unsubscribed while waiting for a message.".format(topic),
                        "TopicUnsubscribed", "Explicit unsubscribe"))
            client = self.mqtt_client if self._connected_event.is_set() else None
            if client is not None:
                try:
                    await client.unsubscribe(topic, timeout=timeout)
                except Exception:
                    _logger.debug("Unsubscribe from topic '%s' failed", topic, exc_info=True)
            self._maybe_stop_dispatcher()
            _logger.debug("Unsubscribed from topic '%s'", topic)
            return True

    # ----------------------------------
    # Persistent session internal methods
    # ----------------------------------
    async def _ensure_connected_client(self, timeout):
        """
        Returns the persistent client, opening the session on demand if it does not exist.
        Active subscriptions are re-subscribed on every (re)connect, so after a network drop
        the next operation transparently reconnects without the behaviours noticing it.
        """
        if self.mqtt_client is not None and self._connected_event.is_set():
            return self.mqtt_client
        async with self._connection_lock:
            if self.mqtt_client is None or not self._connected_event.is_set():
                try:
                    await asyncio.wait_for(self._open_client_locked(), timeout=timeout)
                except asyncio.TimeoutError as timeout_error:
                    raise AssetConnectionError(
                        "Timed out waiting for the MQTT connection with {}:{}.".format(self.broker,
                                                                                       self.port),
                        "MQTTConnectionTimeout", "The asset connection timed out") from timeout_error
            if self.mqtt_client is None:
                raise AssetConnectionError("The MQTT client is not available.", "ClientUnavailable",
                                           "Internal state error")
            # If there are live interests (subscriptions or pending waiters), the dispatcher
            # must be pumping: e.g. after a drop it died with the old session and the reconnect
            # above created a new one. Publish-only flows stay task-free (no subs, no waiters).
            if self._active_subscriptions or self._waiters:
                self._ensure_dispatcher()
            return self.mqtt_client

    async def _open_client_locked(self):
        """
        Opens the persistent MQTT session. The caller must hold '_connection_lock' and have
        checked that no live session exists.
        """
        if not self.broker:
            raise AssetConnectionError("MQTT broker is not defined.", "BrokerNotDefined", "Missing Broker")
        tls_params = aiomqtt.TLSParameters() if self.use_tls else None
        client = aiomqtt.Client(hostname=self.broker, port=self.port,
                                keepalive=self.keepalive, tls_params=tls_params)
        await client.__aenter__()
        self.mqtt_client = client
        self._connected_event.set()
        # Re-subscribe the topics that were active before a reconnect
        async with self._subscription_lock:
            for topic_filter, subscription in self._active_subscriptions.items():
                await client.subscribe(topic_filter, qos=subscription['qos'])
                _logger.debug("Subscribed/re-subscribed to topic '%s' (QoS %s)",
                              topic_filter, subscription['qos'])
        _logger.info("Connected to MQTT broker %s:%s", self.broker, self.port)

    def _ensure_dispatcher(self):
        """
        Starts the dispatcher task on demand if it is missing, done or bound to an old
        client. It is only needed while there are active subscriptions or pending waiters,
        so publish-only flows never create background tasks.
        """
        if self.mqtt_client is None:
            return
        task = self._dispatcher_task
        if task is not None and not task.done() and self._dispatcher_client is self.mqtt_client:
            return
        self._stop_dispatcher()
        self._dispatcher_client = self.mqtt_client
        self._dispatcher_task = asyncio.create_task(
            self._message_dispatcher(),
            name="SMIA-MQTT-Dispatcher-{}:{}".format(self.broker, self.port))

    def _stop_dispatcher(self):
        """Cancels the dispatcher task without waiting (it never holds locks, so it is safe)."""
        task, self._dispatcher_task = self._dispatcher_task, None
        self._dispatcher_client = None
        if task is not None and not task.done():
            task.cancel()

    def _maybe_stop_dispatcher(self):
        """Stops the dispatcher when nothing is left to listen for (no subs and no waiters)."""
        if not self._active_subscriptions and not self._waiters:
            self._stop_dispatcher()

    async def _message_dispatcher(self):
        """
        Internal dispatcher: reads the incoming message flow of the persistent client, updates
        the last-known-value cache and fans every message out to all the waiters whose topic
        filter matches (MQTT `+` and `#` wildcards supported). It ends when the session drops;
        the next operation reconnects on demand and restarts it if still needed.
        """
        client = self.mqtt_client
        if client is None:
            return
        try:
            async for message in client.messages:
                topic_str = str(message.topic)
                payload = message.payload
                if isinstance(payload, (bytearray, memoryview)):
                    payload = bytes(payload)
                elif not isinstance(payload, bytes):
                    payload = str(payload).encode('utf-8')
                self._store_last_value(topic_str, payload)
                # Fan-out: every pending waiter whose filter matches gets its own copy
                for topic_filter, futures in list(self._waiters.items()):
                    if self._topic_matches(message.topic, topic_filter):
                        for fut in list(futures):
                            if not fut.done():
                                fut.set_result(payload)
                        futures.clear()
                        if not futures:
                            self._waiters.pop(topic_filter, None)
        except asyncio.CancelledError:
            raise
        except aiomqtt.MqttError as mqtt_error:
            _logger.warning("MQTT connection with %s:%s lost (%s). Next operation will reconnect.",
                            self.broker, self.port, mqtt_error)
        finally:
            # Detach only if this dispatcher still owns the client (a reconnect may have already replaced it).
            async with self._connection_lock:
                if self.mqtt_client is client:
                    self.mqtt_client = None
                    self._connected_event.clear()
                    try:
                        await client.__aexit__(None, None, None)
                    except Exception:
                        _logger.debug("Error while closing the dropped MQTT client", exc_info=True)

    async def _build_subscribe_response(self, interaction_metadata, raw_response):
        """Decodes a raw subscribed payload and applies the AAS dataQuery/type transformations."""
        decoded = raw_response.decode('utf-8', errors='replace') \
            if isinstance(raw_response, (bytes, bytearray)) else str(raw_response)
        data_query_elem = interaction_metadata.get_sm_element_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_INTERFACE_INTERACTION_DATA_QUERY)
        data_type_elem = interaction_metadata.get_sm_element_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_INTERFACE_INTERACTION_TYPE)
        if (data_query_elem is None or not getattr(data_query_elem, 'value', None)
                or not str(data_query_elem.value).strip()) and data_type_elem is None:
            return decoded
        try:
            return await self.get_response_content(interaction_metadata, decoded)
        except AttributeError as attr_error:
            # The base helper requires 'contentType' in forms when a dataQuery is defined
            raise AssetConnectionError(
                "Cannot apply the dataQuery of the interaction because its content type is not defined.",
                "invalid interaction metadata", str(attr_error)) from attr_error

    # ----------------
    # Internal helpers
    # ----------------
    @staticmethod
    def _has_input_data(service_input_data):
        """Checks whether service input data carries any usable content."""
        if service_input_data is None:
            return False
        try:
            if isinstance(service_input_data, dict):
                return len(service_input_data) > 0
            return True
        except TypeError:
            return service_input_data is not None

    @staticmethod
    def _waiter_succeeded(waiter):
        """Checks whether a waiter future completed with a value (not an exception/cancellation)."""
        return waiter.done() and not waiter.cancelled() and waiter.exception() is None

    async def _release_subscription_slot(self, topic):
        """Rolls back one subscription slot (used when a subscribe never got its message)."""
        async with self._subscription_lock:
            subscription = self._active_subscriptions.get(topic)
            if subscription is None:
                return
            subscription['refcount'] -= 1
            if subscription['refcount'] <= 0:
                del self._active_subscriptions[topic]
                client = self.mqtt_client if self._connected_event.is_set() else None
                if client is not None:
                    try:
                        await client.unsubscribe(topic, timeout=self.default_subscribe_timeout)
                    except asyncio.CancelledError:
                        raise
                    except Exception:
                        # Best-effort rollback: the session may already be down, in which case
                        # there is nothing broker-side left to clean.
                        _logger.debug("Could not unsubscribe from topic '%s' during rollback", topic,
                                      exc_info=True)
                self._maybe_stop_dispatcher()

    def _store_last_value(self, topic, payload):
        """Stores the last-known value of an exact topic, bounding the cache size."""
        if topic in self._last_values:
            self._last_values.pop(topic)
        elif len(self._last_values) >= MAX_CACHED_TOPICS:
            self._last_values.pop(next(iter(self._last_values)))
        self._last_values[topic] = (payload, time.monotonic())

    @staticmethod
    def _topic_matches(topic_obj, topic_filter):
        """Checks whether a received topic matches a subscription filter (wildcards included)."""
        matches = getattr(topic_obj, 'matches', None)
        if callable(matches):
            try:
                return bool(matches(topic_filter))
            except Exception:
                pass
        return str(topic_obj) == topic_filter

    @staticmethod
    def _parse_broker_uri(uri_str):
        """
        Extracts (hostname, port, use_tls) from a broker URI.

        Returns:
            tuple: (hostname, port, use_tls).
        """
        parsed_url = urlparse(uri_str)
        if not parsed_url.netloc:
            parsed_url = urlparse("//{}".format(uri_str), scheme='mqtt')  # If 'netloc' is empty, the '//' is missing
        elif not parsed_url.scheme:
            parsed_url = parsed_url._replace(scheme='mqtt')     # If there is no scheme, e.g., '//broker.com:1883'

        use_tls = parsed_url.scheme.lower() == 'mqtts'
        if parsed_url.port:
            port = parsed_url.port
        elif use_tls:
            port = 8883
        else:
            port = 1883
        return parsed_url.hostname, port, use_tls

    @classmethod
    def _parse_mqtt_href(cls, href_val):
        """
        Parses the `forms.href` of an interaction.

        Returns:
            tuple: (topic, broker_override, port_override, tls_override).
        """
        # A literal '#' must travel percent-encoded; protect it in case the AAS forgot it
        safe_href = href_val.replace('#', '%23')
        parsed = urlparse(safe_href)

        broker_override = None
        port_override = None
        tls_override = False
        if parsed.scheme.lower() in ('mqtt', 'mqtts'):
            broker_override, port_override, tls_override = cls._parse_broker_uri(safe_href)
            raw_path = parsed.path
            if raw_path.startswith('/'):
                raw_path = raw_path[1:]  # Remove exactly the host/path separator slash
            topic = unquote(raw_path)
        else:
            raw_path = parsed.path
            if raw_path.startswith('.//'):
                raw_path = "/{}".format(raw_path[3:])
            topic = unquote(raw_path)

        if not topic:
            raise AssetConnectionError(
                "Resolved MQTT topic is empty from href '{}'.".format(href_val),
                "InvalidTopicFormat", "Empty topic after URI resolution")
        return topic, broker_override, port_override, tls_override


class MQTTAssetInterfaceSemantics:
    """
    This class contains the specific semanticIDs of MQTT interfaces.
    """

    SEMANTICID_MQTT_INTERFACE_RETAIN = 'https://www.w3.org/2019/wot/mqtt#hasRetainFlag'
    SEMANTICID_MQTT_INTERFACE_CONTROL_PACKET = 'https://www.w3.org/2019/wot/mqtt#ControlPacket'
    SEMANTICID_MQTT_INTERFACE_QOS = 'https://www.w3.org/2019/wot/mqtt#hasQoSFlag'
