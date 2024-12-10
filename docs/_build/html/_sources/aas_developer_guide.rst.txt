AAS Developer Guide
===================

This guide is a comprehensive resource for developing the :term:`AAS`. In this approach, the AAS is composed by the :term:`AAS Manager` and the :term:`AAS Core`. Therefore, this guide is divided into two parts. The guide is intended for both new and experienced contributors.

Development of the AAS Manager
------------------------------

The AAS Manager only needs to be parameterised, as it is provided by the platform and it is the common part of all AASs. To parameterise it, it has to perform thee definition of the overall AAS in form of an XML document.

The definition of the AAS must follow the official AAS meta-model, presented by Plattform Industrie 4.0 in cooperation with IDTA and ZVEI. This meta-model specifies that an environment has to be defined where all AAS, sub-models and concept descriptions will be placed. So, the AAS definition will have three main elements:

.. code-block:: xml
    :caption: Main groups in the AAS definition in the form of an XML document.

    <aas:environment xmlns:aas="https://admin-shell.io/aas/3/0">
        <aas:assetAdministrationShells>
            <aas:assetAdministrationShell>
                <!-- AAS Manager definition -->
            </aas:assetAdministrationShell>
            <aas:assetAdministrationShell>
                <!-- AAS Core definition -->
            </aas:assetAdministrationShell>
        <aas:assetAdministrationShells>
        <aas:submodels>
            <aas:submodel>
                <!-- Submodel definition -->
            </aas:submodel>
        </aas:submodels>
        <aas:conceptDescriptions>
            <aas:conceptDescription>
                <!-- concept description definition -->
            </aas:conceptDescription>
        </aas:conceptDescriptions>
    </aas:environment>

TODO: TO BE FINALISED (waiting for the final proposal of the AAS definition)

Development of the AAS Core
---------------------------

The AAS Core is the specific part of the AAS, and it is developed by the user, so this guide will especially detail how the interaction between the Manager and the Core works and some tips for the development of the AAS Core source code.

During the development of the AAS Core there are some important points that should be considered:

* The type of the asset (logical or physical). In case it is physical, what is its communication capacity.
* How the interaction with the AAS Manager works. The interaction between Manager and Core is established by this approach, which will be detailed in this section.
* The AAS Core has to handle multiple service requests that can be received simultaneously.
* The AAS Core will be containerized.

Let's start with the AAS Manager-Core interactions.

AAS Manager-Core interactions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This approach uses Kafka as the message brokering channel, because it allows the communication between two entities that are in separate Docker containers. `Apache Kafka <https://kafka.apache.org/>`_ is an open source distributed event streaming platform. As the interactions between the AAS Manager and Core will be asynchronous, it can closely resemble an event-based communication, these events being requests for services.

Topics in Kafka are the fundamental unit of data organisation in Kafka, and can have one or more producers and zero or more consumers. Each topic is divided into one or more partitions. Each partition is an ordered and immutable sequence of messages. Partitions allow parallel distribution of data and improve performance and scalability. Each partition has a unique offset number that identifies each message within it. Kafka manages all topics and partitions and guarantees that any consumer of a given topic-partition will always read events from that partition in exactly the same order in which they were written. To support fault tolerance, topics must have a replication factor greater than one (usually set to between 2 and 3).

This approach proposes to set a topic for each AAS, and this topic will be as follows:

    * Topic name: *AAS_id*

      * Partition 0: related to the AAS Manager. The AAS Manager will publish both its service requests and also the responses to previous AAS Core requests, so that

        * the AAS Manager is a publisher
        * the AAS Core is a subscriber

      * Partition 1: related to the AAS Core. In this case, The AAS Core will publish both its service requests and also the responses to previous AAS Manager requests, so that

        * the AAS Manager is a subscriber
        * the AAS Core is a publisher

This information has to been taken into account for the development of the AAS Core.


Handling AAS Manager-Core interactions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The interaction between the AAS Manager and the Core is conducted asynchronously. At some point, one of them will request a service from the other entity, but without knowing when exactly it will be able to make this request. Therefore, for each service request, both will store the information of the request. Later, when a response arrives, it will be necessary to determine which request is linked to that response.

As it is presented in the previous subsection, both are only publishing to their partition and subscribed to the other entity's partition. With this subscription the entity receives the messages created by the other, that can be of three types:

    * **Status information**: information about the status of the entity (i.e. the current state of the finite state machine).
    * **Service request**: the other entity has made a request for a service that the current entity has to realize.
    * **Response to a previous service request**: the other entity is sending the information about a service that has been previously requested by the current entity.

Therefore, it is necessary to classify what type of message the Kafka subscriber has received each time. To do this, the ``key`` of the Kafka message will be used. This key will determine the nature of the message and the entity that publishes it.

.. important::

   The structure of the message key is as follows: *<entity>-<message type>*. The message type can be:

        * status
        * service-request
        * service-response

.. dropdown:: Examples of some message keys for the AAS Manager
       :octicon:`check-circle;1em;sd-text-primary`

       manager-status

       manager-service-request

       manager-service-response

.. dropdown:: Examples of some message keys for the AAS Core
       :octicon:`check-circle;1em;sd-text-primary`

       core-status

       core-service-request

       core-service-response


In addition to classifying the messages, each service response must be mapped to its corresponding request. To do this, all interaction messages have a mandatory attribute: ``interaction_id``. This is a numeric attribute (Integer) that is created by the service requester and is used to identify each request and response, so each request-response pair must have a unique global *interaction_id* as identifier.


Implementation of the AAS Manager-Core interactions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Thus, one task during the development of the AAS Core source code is to specify the subscriber and the publisher in the topic of the AAS using the official Kafka libraries. The developer can use any programming language, so in this case, only Kafka Python libraries are shown. Depending on the programming model selected to structure the code (synchronous or asynchronous), the related Python library has to be selected. In this example, both are presented.

.. tab:: Synchronous (kafka)

    .. code:: python

        from kafka import KafkaConsumer, TopicPartition, KafkaProducer

        # KAFKA CONSUMER (to receive service request from AAS Manager or read the responses of Core's requests)
        kafka_consumer_partition_core = KafkaConsumer( bootstrap_servers=[KAFKA_SERVER_IP + ':9092'],
                                              client_id='i4-0-smia-core',
                                              value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                                              )
        kafka_consumer_partition_core.assign([TopicPartition(kafka_topic_name, 0)])

        # KAFKA PRODUCER (to send service requests to AAS Manager)
        kafka_producer = KafkaProducer(bootstrap_servers=[KAFKA_SERVER_IP + ':9092'],
                                           client_id='i4-0-smia-core',
                                           value_serializer=lambda x: json.dumps(x).encode('utf-8'),
                                           key_serializer=str.encode
                                           )

        result = kafka_producer.send(KAFKA_TOPIC, value=svc_request_json, key='core-service-request', partition=1)

.. tab:: Asynchronous (aiokafka)

    .. code:: python

        from aiokafka import AIOKafkaConsumer, TopicPartition, AIOKafkaProducer

        # KAFKA CONSUMER (to receive service request from AAS Manager or read the responses of Core's requests)
        kafka_consumer_partition_core = AIOKafkaConsumer( bootstrap_servers=[KAFKA_SERVER_IP + ':9092'],
                                              client_id='i4-0-smia-core',
                                              value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                                              )
        kafka_consumer_partition_core.assign([TopicPartition(kafka_topic_name, 0)])

        # KAFKA PRODUCER (to send service requests to AAS Manager)
        kafka_producer = AIOKafkaProducer(bootstrap_servers=[KAFKA_SERVER_IP + ':9092'],
                                           client_id='i4-0-smia-core',
                                           value_serializer=lambda x: json.dumps(x).encode('utf-8'),
                                           key_serializer=str.encode
                                           )

        await kafka_producer.start()
        try:
            await kafka_producer.send_and_wait(KAFKA_TOPIC, value=msg_data,
                                               key='core-service-request',
                                               partition=1)
        finally:
            await kafka_producer.stop()

.. important::

   As can be seen with the serializer/deserializer used, the interaction messages between the AAS Manager and the AAS Core are in UTF-8 format. This should be considered during publishing and subscribing to Kafka topics, as the AAS Manager (provided by I4.0 SMIA) works this way.


General structure of the AAS Core source code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The source code of the AAS Core can be developed in the way that the developer considers more efficient. However, this AAS developer guide tend to offer some tips that may be interesting.

.. tip::

   **Tip 1: Use multiple threads**

   If the asset that the AAS is representing is of a physical type, it is common for it to receive messages from the asset, so the program will at some point have to be waiting for messages from different sources: the physical asset controller and the AAS Manager.

   To not block the main thread of the program, this guide advises to create parallel threads for each communication channel. In this case, if the AAS Core needs to communicate with AAS Manager and with the asset, two threads should be defined (an example is in the following dropdown).

   .. dropdown:: Example of multiple threads in Python
       :octicon:`code-square;1em;sd-text-info`

       .. code:: python

           from threading import Thread

           def main():
                thread_aas_manager = Thread(target=aas_manager_method, args=())
                thread_asset = Thread(target=asset_method, args=())

                thread_aas_manager.start()
                thread_asset.start()

           if __name__ == '__main__':
                main()


.. tip::

   **Tip 2: Use a storage object for service requests**

   The AAS Manager may request many services in a short period of time, and those services may involve a physical asset, which usually cannot perform the task instantaneously. Therefore, this guide advises to use some kind of storage object, for example a dictionary or an array, to have accessible all service requests that have not yet been performed.

   Thus, when a request arrives, its information is stored in this object, and when the service is finished, it can remove that information and use it for the creation of the response message.


.. tip::

   **Tip 3: Store global information in a unique class**

   There is information that is constant and used a lot during the main AAS Core thread, for example: the partition for Manager or Core in the Kafka topic, the path to the configuration file, etc...

   This guide advises to add this information in the same class, so that it can be easily accessed by any other class, and it reduces the probability of making a mistake, since the information is written only once.


TODO
----

FALTAN COMENTAR VARIAS COSAS:

* Sincronizacion inicial del Manager-Core (no arranca el funcionamiento normal del Core hasta que los dos no hayan finalizado su estado Boot)
* Al comienzo es posible que se arranquen en diferente momento, asi que el primer consumidor hay que configurarlo para que reciba mensajes desde el comiento (offset a 'earliest')
* El Core solo puede solicitar servicios al Manager si este se encuentra en estado Running
* Como leer el ConfigMap para obtener informacion como el topico de Kafka, la definicion del AAS en XML...
* Importancia del thread e interactionID (como leerlos si recibimos una peticion de servicio del Manager y como generarlos si el AAS Core tiene que comenzar una conversacion, es decir, ser el primero en solicitar un servicio)
* Como hay que publicar los mensajes en Kakfa para la interacciones (p.e. en el key poner 'core-service-request' o 'core-service-response', el topico y particion bien, etc.)

