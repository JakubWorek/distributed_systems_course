package sr.grpc.server;

import io.grpc.Grpc;
import io.grpc.InsecureServerCredentials;
import io.grpc.Server;
import java.io.IOException;
import java.util.concurrent.TimeUnit;
import io.grpc.protobuf.services.ProtoReflectionService;

public class grpcServer {

	private Server server;

	private void start() throws IOException {
		int port = 50051;
		server = Grpc.newServerBuilderForPort(port, InsecureServerCredentials.create())
				.addService(new CalculatorImpl())
				.addService(ProtoReflectionService.newInstance())
				.build()
				.start();
		System.out.println("Server started, listening on " + port);

		Runtime.getRuntime().addShutdownHook(new Thread(() -> {
			try {
				grpcServer.this.stop();
			} catch (InterruptedException e) {
				e.printStackTrace(System.err);
			}
		}));
	}

	private void stop() throws InterruptedException {
		if (server != null) {
			server.shutdown().awaitTermination(30, TimeUnit.SECONDS);
		}
	}

	private void blockUntilShutdown() throws InterruptedException {
		if (server != null) {
			server.awaitTermination();
		}
	}

	public static void main(String[] args) throws IOException, InterruptedException {
		final grpcServer server = new grpcServer();
		server.start();
		server.blockUntilShutdown();
	}
}
