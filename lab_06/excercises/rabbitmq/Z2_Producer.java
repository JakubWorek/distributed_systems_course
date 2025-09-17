import com.rabbitmq.client.BuiltinExchangeType;
import com.rabbitmq.client.Channel;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;
import java.io.BufferedReader;
import java.io.InputStreamReader;

public class Z2_Producer {

    public static void main(String[] argv) throws Exception {

        System.out.println("Z2 PRODUCER");

        ConnectionFactory factory = new ConnectionFactory();
        factory.setHost("localhost");
        Connection connection = factory.newConnection();
        Channel channel = connection.createChannel();

        // --- User input for Exchange Type ---
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        System.out.print("Enter Exchange Name (e.g., direct_exchange, topic_exchange): ");
        String EXCHANGE_NAME = br.readLine();
        System.out.print("Enter Exchange Type (DIRECT or TOPIC): ");
        String exchangeTypeStr = br.readLine().toUpperCase();
        BuiltinExchangeType EXCHANGE_TYPE;

        switch (exchangeTypeStr) {
            case "DIRECT":
                EXCHANGE_TYPE = BuiltinExchangeType.DIRECT;
                break;
            case "TOPIC":
                EXCHANGE_TYPE = BuiltinExchangeType.TOPIC;
                break;
            default:
                System.err.println("Invalid Exchange Type. Using DIRECT by default.");
                EXCHANGE_TYPE = BuiltinExchangeType.DIRECT;
                break;
        }

        channel.exchangeDeclare(EXCHANGE_NAME, EXCHANGE_TYPE);
        System.out.println("Declared Exchange: " + EXCHANGE_NAME + " of type " + EXCHANGE_TYPE);

        while (true) {
            System.out.print("Enter routing key (or 'exit' to quit): ");
            String routingKey = br.readLine();

            if ("exit".equals(routingKey)) {
                break;
            }

            System.out.print("Enter message: ");
            String message = br.readLine();

            channel.basicPublish(EXCHANGE_NAME, routingKey, null, message.getBytes("UTF-8"));
            System.out.println("Sent: '" + message + "' with routing key '" + routingKey + "' to exchange '" + EXCHANGE_NAME + "'");
        }

        channel.close();
        connection.close();
    }
}