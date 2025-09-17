package sr.ice.server;

import com.zeroc.Ice.Communicator;
import com.zeroc.Ice.Identity;
import com.zeroc.Ice.ObjectAdapter;
import com.zeroc.Ice.Util;

import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

import sr.ice.server.devices.DeviceImp;

public class Server {
	private final String IP;

	private final int port;

	private final Communicator communicator;

	private final ObjectAdapter adapter;

	private final String categoryName;

	private final List<DeviceImp> devices = new ArrayList<>();


	Server(String IP, int port, List<DeviceImp> devices, String category, String adapterName) {
		this.IP = IP;
		this.port = port;
		this.devices.addAll(devices);
		this.categoryName = category;

		communicator = Util.initialize();

		String connectionEndpoints = "tcp -h " + IP + " -p " + port + " : udp -h " + IP + " -p " + port;
		adapter = communicator.createObjectAdapterWithEndpoints(adapterName, connectionEndpoints);

		initDevices();
	}


	private void initDevices() {
		for (DeviceImp device : devices) {
			adapter.add(device, new Identity(device.getId(), categoryName));
		}
	}


	private void listDevices() {
		for (DeviceImp device : devices) {
			System.out.println(device.getId());
		}
	}


	public void start() {
		adapter.activate();

		System.out.println("Server is running on " + IP + ":" + port);

		while (true) {
			Scanner scanner = new Scanner(System.in);
			String command = scanner.nextLine();

			if (command.equals("help")) {
				System.out.println("Available commands: list, exit");
			}
			else if (command.equals("list")) {
				listDevices();
			}
			else if (command.equals("exit")) {
				adapter.deactivate();
				communicator.shutdown();
				communicator.destroy();
				System.exit(0);
			}
		}
	}
}