import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.util.Arrays;

public class JavaUdpServer {
    public static void main(String[] args) {
        System.out.println("JAVA UDP SERVER");

        int portNumber = 9008;
        try (DatagramSocket socket = new DatagramSocket(portNumber)) {
            byte[] receiveBuffer = new byte[1024];
            byte[] sendBuffer;

            while (true) {
                // Receive ping request from the client
                Arrays.fill(receiveBuffer, (byte) 0);
                DatagramPacket receivePacket =
                        new DatagramPacket(receiveBuffer, receiveBuffer.length);
                socket.receive(receivePacket);
                String msg = new String(receivePacket.getData());
                System.out.println("received msg: " + msg);

                InetAddress clientAddress = receivePacket.getAddress();
                int clientPortNumber = receivePacket.getPort();

                // Send ping response to the client
                sendBuffer = "Pong client".getBytes();
                DatagramPacket packetSent = new DatagramPacket(
                        sendBuffer,
                        sendBuffer.length,
                        clientAddress,
                        clientPortNumber
                );
                socket.send(packetSent);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
