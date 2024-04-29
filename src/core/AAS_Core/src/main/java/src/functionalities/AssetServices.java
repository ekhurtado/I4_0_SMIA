package src.functionalities;

import java.util.Random;

public class AssetServices {

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

}
