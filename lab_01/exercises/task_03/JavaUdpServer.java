import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.Arrays;

public class JavaUdpServer {
    public static void main(String[] args) {
        System.out.println("JAVA UDP SERVER");

        int portNumber = 9008;
        try (DatagramSocket socket = new DatagramSocket(portNumber)) {
            byte[] receiveBuffer = new byte[1024];
            byte[] sendBuffer;

            while (true) {
                // Receive request from the client
                Arrays.fill(receiveBuffer, (byte) 0);
                DatagramPacket receivePacket =
                        new DatagramPacket(receiveBuffer, receiveBuffer.length);
                socket.receive(receivePacket);
                int number = ByteBuffer.wrap(receiveBuffer).order(ByteOrder.LITTLE_ENDIAN).getInt();
                System.out.printf("received msg: %d\n", number);

                // Increment the number
                number++;

                // Send response to the client
                InetAddress clientAddress = receivePacket.getAddress();
                int clientPortNumber = receivePacket.getPort();
                sendBuffer = ByteBuffer.allocate(4).order(ByteOrder.LITTLE_ENDIAN).putInt(number).array();
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
