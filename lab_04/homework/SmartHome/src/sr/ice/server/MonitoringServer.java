package sr.ice.server;

import java.util.ArrayList;
import java.util.List;
import sr.ice.server.devices.DeviceImp;
import sr.ice.server.devices.cameras.CameraImp;

public class MonitoringServer {
    public static void main(String[] args) {
        String serverIp = "127.0.0.1";
        int port = 40042;

        String category = "monitoring-devices";
        String adapter = "monitoring-adapter";

        List<DeviceImp> devices = new ArrayList<>();
        CameraImp camera1 = new CameraImp("Camera1");
        CameraImp camera2 = new CameraImp("Camera2");

        devices.add(camera1);
        devices.add(camera2);

        Server server = new Server(serverIp, port, devices, category, adapter);
        server.start();
    }
}