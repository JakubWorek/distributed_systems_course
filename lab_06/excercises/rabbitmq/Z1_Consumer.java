import com.rabbitmq.client.AMQP;
import com.rabbitmq.client.Channel;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;
import com.rabbitmq.client.Consumer;
import com.rabbitmq.client.DefaultConsumer;
import com.rabbitmq.client.Envelope;
import java.io.IOException;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;

public class Z1_Consumer {

    public static void main(String[] argv) throws Exception {

        // info
        System.out.println("Z1 CONSUMER");

        // connection & channel
        ConnectionFactory factory = new ConnectionFactory();
        factory.setHost("localhost");
        Connection connection = factory.newConnection();
        Channel channel = connection.createChannel();

        // queue
        String QUEUE_NAME = "queue1";
        channel.queueDeclare(QUEUE_NAME, false, false, false, null);
        channel.basicQos(1);

        // consumer (handle msg)
        Consumer consumer = new DefaultConsumer(channel) {
            @Override
            public void handleDelivery(String consumerTag, Envelope envelope, AMQP.BasicProperties properties, byte[] body) throws IOException {
                String message = new String(body, "UTF-8");
                System.out.println("Received: " + message);

                // zad1a
//                // Simulate consumer restart
//                if (message.equals("restart")) {
//                    throw new RuntimeException("Consumer restart");
//                } else {
//                    try {
//                        // Simulate message processing
//                        System.out.println("Processing message...");
//                        Thread.sleep(2000); // 2 seconds
//                        System.out.println("Message processed");
//                    } catch (InterruptedException e) {
//                        e.printStackTrace();
//                    }
//                }
                // zad1b
                try {
                    System.out.println("Sleeping for " + message + " seconds...");
                    Thread.sleep(Integer.parseInt(message));
                } catch (InterruptedException e) {
                    throw new RuntimeException(e);
                }
                channel.basicAck(envelope.getDeliveryTag(), false);
            }
        };

        // start listening
        System.out.println("Waiting for messages...");
        // acknowledge messages automatically
//        channel.basicConsume(QUEUE_NAME, true, consumer);
        // acknowledge messages manually
        channel.basicConsume(QUEUE_NAME, false, consumer);

        Thread.sleep(100);

        // zad 1a
        // Read time to sleep in seconds
        BufferedReader br =
                new BufferedReader(new InputStreamReader(System.in));
        System.out.println("Enter time in seconds: ");
        String message = br.readLine();

        // Wait and then close
        int timeToSleep = Integer.parseInt(message);
        Thread.sleep(timeToSleep * 1000L);

        // close
//        channel.close();
//        connection.close();
    }
}
