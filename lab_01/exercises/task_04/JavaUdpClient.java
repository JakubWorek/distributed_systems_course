import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.util.Arrays;

public class JavaUdpClient {
    public static void main(String[] args) {
        System.out.println("JAVA UDP CLIENT");

        int portNumber = 9009;
        try (DatagramSocket socket = new DatagramSocket()) {
            InetAddress address = InetAddress.getByName("localhost");
            byte[] sendBuffer = "Ping Java".getBytes();

            DatagramPacket sendPacket = new DatagramPacket(
                    sendBuffer,
                    sendBuffer.length,
                    address,
                    portNumber
            );
            socket.send(sendPacket);

            byte[] receiveBuffer = new byte[1024];
            Arrays.fill(receiveBuffer, (byte) 0);
            DatagramPacket receivePacket =
                    new DatagramPacket(receiveBuffer, receiveBuffer.length);
            socket.receive(receivePacket);
            String msg = new String(receivePacket.getData());
            System.out.println("received msg: " + msg.trim());
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
