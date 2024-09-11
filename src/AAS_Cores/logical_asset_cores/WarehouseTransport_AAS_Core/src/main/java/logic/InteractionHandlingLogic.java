package logic;

import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;
import utilities.InteractionUtils;

import java.time.Duration;

public class InteractionHandlingLogic extends Thread {

    @Override
    public void run() {

        // First, the Kafka consumer for the AAS Manager partition will be created
        KafkaConsumer kafkaConsumerPartitionManager = InteractionUtils.createInteractionKafkaConsumer();

        while (true) {
            final ConsumerRecords<String, String> consumerRecords =
                    kafkaConsumerPartitionManager.poll(Duration.ofMillis(10000));

            System.out.println("Consumer record:");
            System.out.println(consumerRecords.toString());

            consumerRecords.forEach(record -> {
                System.out.println("Mensaje recibido:");

                System.out.println("KEY: " + record.key());
                System.out.println("VALUE: " + record.value());
//                System.out.println("PARTITION:" + record.partition());
//                System.out.println("OFFSET:" + record.offset());
//
//                System.out.printf("Consumer Record:(%s, %s, %d, %d)\n",
//                        record.key(), record.value(),
//                        record.partition(), record.offset());

                // The next service request information if JSON format is in the value of the message
                JSONObject nextRequestJSON = transformStringToJSON(record.value());
                if (nextRequestJSON.containsKey("status")) {
                    AASCore.LOGGER.info("New status of the AAS Manager: " + nextRequestJSON.get("status"));
                    AASCore aas_core = AASCore.getInstance();
                    aas_core.setManagerStatus((String) nextRequestJSON.get("status"));
                    if (!aas_core.getManagerStatus().equals("Initializing"))
                        AASCore.LOGGER.info("AAS Manager has initialized, so the AAS Core can go to running state.");

                } else {
                    AASCore.LOGGER.info("The Manager has requested a service to the AAS Core");
                    // TODO pensar si este tipo de AAS Cores pueden tener peticiones de servicios
                }
            });
        }

    }

    private static JSONObject transformStringToJSON(String stringValue) {
//        System.out.println("Intentando pasar de string a JSON...");
        JSONObject nextRequestJSON;
        try {
            JSONParser jsonParser = new JSONParser();
            nextRequestJSON = (JSONObject) jsonParser.parse(stringValue);
        } catch (ParseException e) {
            throw new RuntimeException(e);
        }
        System.out.println(nextRequestJSON.toString());
        return nextRequestJSON;
    }

}
