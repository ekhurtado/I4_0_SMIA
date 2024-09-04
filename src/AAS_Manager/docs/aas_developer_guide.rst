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

      * Partition 0: related to the AAS Manager. The AAS Manager will publish its service requests to this partition, and read the responses, so that

        * the AAS Manager is a publisher
        * the AAS Core is a subscriber

      * Partition 1: related to the AAS Core. In this case, the AAS Core will publish its service requests to this partition, and read the responses, so that

        * the AAS Manager is a subscriber
        * the AAS Core is a publisher

This information has to been taken into account for the development of the AAS Core.

Implementation of the AAS Manager-Core interactions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Thus, one task during the development of the AAS Core source code is to specify the subscriber and the publisher in the topic of the AAS using the official Kafka libraries. The developer can use any programming language, so in this case, only Kafka Python libraries are shown. Depending on the programming model selected to structure the code (synchronous or asynchronous), the related Python library has to be selected. In this example, both are presented.

.. tab:: Synchronous (kafka)

    .. code:: python

        from kafka import KafkaConsumer, TopicPartition, KafkaProducer

        # KAFKA CONSUMER (to receive service request from AAS Manager or read the responses of Core's requests)
        kafka_consumer_partition_core = KafkaConsumer( bootstrap_servers=[KAFKA_SERVER_IP + ':9092'],
                                              client_id='component-i40-core',
                                              value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                                              )
        kafka_consumer_partition_core.assign([TopicPartition(kafka_topic_name, 0)])

        # KAFKA PRODUCER (to send service requests to AAS Manager)
        kafka_producer = KafkaProducer(bootstrap_servers=[KAFKA_SERVER_IP + ':9092'],
                                           client_id='component-i40-core',
                                           value_serializer=lambda x: json.dumps(x).encode('utf-8'),
                                           key_serializer=str.encode
                                           )

        result = kafka_producer.send(KAFKA_TOPIC, value=svc_request_json, key='core-service-request',
                                         partition=1)

.. tab:: Asynchronous (aiokafka)

    .. code:: python

        from aiokafka import AIOKafkaConsumer, TopicPartition, AIOKafkaProducer

        # KAFKA CONSUMER (to receive service request from AAS Manager or read the responses of Core's requests)
        kafka_consumer_partition_core = AIOKafkaConsumer( bootstrap_servers=[KAFKA_SERVER_IP + ':9092'],
                                              client_id='component-i40-core',
                                              value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                                              )
        kafka_consumer_partition_core.assign([TopicPartition(kafka_topic_name, 0)])

        # KAFKA PRODUCER (to send service requests to AAS Manager)
        kafka_producer = AIOKafkaProducer(bootstrap_servers=[KAFKA_SERVER_IP + ':9092'],
                                           client_id='component-i40-core',
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
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The source code of the AAS Core can be developed in the way that the developer considers more efficient. However, this AAS developer guide tend to offer some tips that may be interesting.

.. tip:: Tip 1: Use multiple threads

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


Some tests with code blocks
---------------------------


TODO: TO BE FINALISED (THIS IS A TEST PAGE OF CODE ADDITION)

Code blocks and examples are an essential part of technical project
documentation. Sphinx provides syntax highlighting for these
out-of-the-box, through Pygments.

.. tab:: Option 1

    .. code::

       Code blocks in Markdown can be created in various ways.

           Indenting content by 4 spaces.
           This will not have any syntax highlighting.


       Wrapping text with triple backticks also works.
       This will have default syntax highlighting (highlighting a few words and "strings").

    .. code:: python

       python
       print("And with the triple backticks syntax, you can have syntax highlighting.")


       none
       print("Or disable all syntax highlighting.")


       There's a lot of power hidden underneath the triple backticks in MyST Markdown,
       as seen in <https://myst-parser.readthedocs.io/en/latest/syntax/roles-and-directives.html>.

.. tab:: Option 2

    .. code::

       Code blocks in reStructuredText can be created in various ways::

           Indenting content by 4 spaces, after a line ends with "::".
           This will have default syntax highlighting (highlighting a few words and "strings").

    .. code::

       You can also use the code directive, or an alias: code-block, sourcecode.
       This will have default syntax highlighting (highlighting a few words and "strings").

    .. code:: python

       print("And with the directive syntax, you can have syntax highlighting.")

    .. code:: none

       print("Or disable all syntax highlighting.")


There's a lot more forms of "blocks" in reStructuredText that can be used, as
seen in https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#literal-blocks.

With the "sphinx-design" extension we can also add dropdowns:

.. dropdown:: Dropdown title

    Dropdown content


Event dropdowns with an icon:

.. dropdown:: Dropdown with icon
    :octicon:`code-square;1em;sd-text-info`

    Dropdown content


Test for a subsection
~~~~~~~~~~~~~~~~~~~~~
