import com.rabbitmq.client.AMQP;
import com.rabbitmq.client.BuiltinExchangeType;
import com.rabbitmq.client.Channel;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;
import com.rabbitmq.client.Consumer;
import com.rabbitmq.client.DefaultConsumer;
import com.rabbitmq.client.Envelope;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

public class Z2_Consumer {

    public static void main(String[] argv) throws Exception {

        System.out.println("Z2 CONSUMER");

        ConnectionFactory factory = new ConnectionFactory();
        factory.setHost("localhost");
        Connection connection = factory.newConnection();
        Channel channel = connection.createChannel();

        // --- User input for Exchange Type and Routing Key ---
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

        String queueName = channel.queueDeclare().getQueue();
        System.out.print("Enter binding key for this consumer: ");
        String bindingKey = br.readLine();
        channel.queueBind(queueName, EXCHANGE_NAME, bindingKey);
        System.out.println("Created queue '" + queueName + "' and bound with key '" + bindingKey + "'");


        Consumer consumer = new DefaultConsumer(channel) {
            @Override
            public void handleDelivery(String consumerTag, Envelope envelope, AMQP.BasicProperties properties, byte[] body) throws IOException {
                String message = new String(body, "UTF-8");
                System.out.println("Received: '" + message + "' with routing key '" + envelope.getRoutingKey() + "'");
            }
        };

        System.out.println("Waiting for messages...");
        channel.basicConsume(queueName, true, consumer);
    }
}