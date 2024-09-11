package src.functionalities;

import org.json.simple.JSONObject;

import java.util.Random;

public class AssetRelatedServices {

    public static double getAssetBattery() {
        Random r = new Random();
        float rangeMin = 0.0F;
        float rangeMax = 100.0F;
        return rangeMin + (rangeMax - rangeMin) * r.nextDouble();
    }

    public static String getAssetModel() {
        return "KUKA KR3 R540";
    }

    public static String getAssetSpecifications() {
        return "assembly robot";
    }

    public static String getNegotiationValue(JSONObject serviceData) {
        switch ((String) ((JSONObject) serviceData.get("serviceParams")).get("criteria")) {
            case "battery":
                System.out.println("The criteria is the battery, so the value must be obtained");
                return String.valueOf(getAssetBattery());
            case "memory":
                System.out.println("The criteria is the memory, the free memory value must be obtained");
                // TODO
                return null;
            default:
                System.out.println("Criteria not available");
                return null;
        }
    }
}
