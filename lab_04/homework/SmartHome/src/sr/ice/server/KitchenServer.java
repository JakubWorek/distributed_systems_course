package sr.ice.server;

import sr.ice.server.devices.DeviceImp;
import sr.ice.server.devices.fridges.FridgeImp;
import sr.ice.server.devices.fridges.FridgeWithIceMakerImp;
import sr.ice.server.devices.fridges.FridgeWithProductsMonitoringImp;

import java.util.ArrayList;
import java.util.List;

public class KitchenServer {

    public static void main(String[] args) {
        String serverIp = "127.0.0.1";
        int port = 40041;
        String adapter = "kitchen-adapter";

        String category = "kitchen-devices";

        List<DeviceImp> devices = new ArrayList<>();
        FridgeImp fridge = new FridgeImp("Fridge1");
        FridgeWithIceMakerImp fridgeWithIceMaker = new FridgeWithIceMakerImp("Fridge2");
        FridgeWithProductsMonitoringImp fridgeWithProductsMonitoring = new FridgeWithProductsMonitoringImp("Fridge3");

        devices.add(fridge);
        devices.add(fridgeWithIceMaker);
        devices.add(fridgeWithProductsMonitoring);

        Server server = new Server(serverIp, port, devices, category, adapter);
        server.start();
    }
}
