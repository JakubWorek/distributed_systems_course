import sys
import os
import Ice
import asyncio
import Smarthome


class InvalidCommand(Exception):
    pass


class Device:
    def __init__(self, name, category, desc, ip, port, prx_type):
        self.name = name
        self.category = category
        self.desc = desc
        self.ip = ip
        self.port = port
        self.prx_type = prx_type
        self.nprx = None

    def connect(self, communicator):
        proxy_str = f"{self.category}/{self.name}:tcp -h {self.ip} -p {self.port} :udp -h {self.ip} -p {self.port}"
        base = communicator.stringToProxy(proxy_str)
        self.nprx = self.prx_type.checkedCast(base)
        if not self.nprx:
            raise ValueError("Invalid proxy")


def list_devices(devices):
    print("\nDevices:")
    for device in devices:
        print(f"{device.name} - {device.desc}")


def find_device(devices, name):
    return next((d for d in devices if d.name == name), None)


async def connect_all_devices(devices, communicator):
    for device in devices:
        try:
            device.connect(communicator)
        except Exception as e:
            print(f"Error connecting to {device.name}: {e}")


async def handle_command(devices, command_line):
    parts = command_line.strip().split()
    if not parts:
        raise InvalidCommand()

    dev_name, *args = parts
    device = find_device(devices, dev_name)
    if not device or not device.nprx:
        raise InvalidCommand()

    cmd = args[0] if args else None
    proxy = device.nprx

    match cmd:
        case "getId":
            print(proxy.getId())
        case "getMode":
            print(proxy.getMode())
        case "setMode":
            mode = args[1].lower()
            proxy.setMode(Smarthome.Mode.ON if mode == "on" else Smarthome.Mode.STANDBY)

        case "setTemperature":
            proxy.setTemperature(float(args[1]))
        case "getTemperature":
            print(proxy.getTemperature())
        case "getTemperatureRange":
            temp_range = proxy.getTemperatureRange()
            print(f"min: {temp_range.min}, max: {temp_range.max}")

        case "makeIce":
            proxy.makeIce(int(args[1]))
            print("Ice making started.")

        case "getProducts":
            for product in proxy.getProducts():
                print(product)
        case "getProduct":
            print(proxy.getProduct(int(args[1])))
        case "getExpiredProducts":
            for product in proxy.getExpiredProducts():
                print(product)
        case "removeProduct":
            proxy.removeProduct(int(args[1]))
        case "addProduct":
            product = Smarthome.Product(
                id=int(args[1]),
                name=args[2],
                amount=int(args[3]),
                unit=parse_unit(args[4]),
                expirationDate=Smarthome.Date(day=int(args[5]), month=int(args[6]), year=int(args[7]))
            )
            proxy.addProduct(product)

        case "getLocation":
            loc = proxy.getLocation()
            print(f"x: {loc.x}, y: {loc.y}")
        case "setResolution":
            proxy.setResolution(int(args[1]))
        case "getStorageLevel":
            print(proxy.getStorageLevel())
        case "getResolution":
            print(proxy.getResolution())

        case _:
            raise InvalidCommand()


def parse_unit(unit_str):
    unit_str = unit_str.lower()
    units = {
        "gram": Smarthome.Unit.GRAM,
        "kilogram": Smarthome.Unit.KILOGRAM,
        "litre": Smarthome.Unit.LITRE,
        "millilitre": Smarthome.Unit.MILLILITRE,
    }
    if unit_str not in units:
        raise InvalidCommand()
    return units[unit_str]


def command_loop(devices, communicator):
    while True:
        try:
            command_line = input(">>> ")
            if command_line == "exit":
                return
            elif command_line == "list":
                list_devices(devices)
            elif command_line == "reconnect":
                asyncio.run(connect_all_devices(devices, communicator))
            else:
                asyncio.run(handle_command(devices, command_line))

        except Smarthome.DevicesIsInStandbyMode:
            print("Switch to ON mode first.")
        except Smarthome.StorageFullError:
            print("Storage full error.")
        except Smarthome.ProductDoesNotExist:
            print("Product does not exist.")
        except Smarthome.InputTemperatureOutOfRange:
            print("Temperature input out of range.")
        except Smarthome.InputResolutionOutOfRange:
            print("Resolution input out of range.")
        except Smarthome.InvalidDate:
            print("Invalid date input.")
        except (InvalidCommand, IndexError, AttributeError, ValueError):
            print("Invalid command.")
        except Ice.ConnectionRefusedException:
            print("Connection refused.")
        except Exception as e:
            print(f"Unexpected error: {e}")


def main():
    server_ip = "127.0.0.1"
    kitchen_port = 40041
    monitoring_port = 40042

    devices = [
        Device("Camera1", "monitoring-devices", "camera 1", server_ip, monitoring_port, Smarthome.CameraPrx),
        Device("Camera2", "monitoring-devices", "camera 2", server_ip, monitoring_port, Smarthome.CameraPrx),
        Device("Fridge1", "kitchen-devices", "fridge", server_ip, kitchen_port, Smarthome.FridgePrx),
        Device("Fridge2", "kitchen-devices", "fridge with ice maker", server_ip, kitchen_port, Smarthome.FridgeWithIceMakerPrx),
        Device("Fridge3", "kitchen-devices", "fridge with product monitoring", server_ip, kitchen_port, Smarthome.FridgeWithProductsMonitoringPrx)
    ]

    communicator = None
    try:
        communicator = Ice.initialize()
        asyncio.run(connect_all_devices(devices, communicator))
        command_loop(devices, communicator)
    except Exception as e:
        print(f"Initialization error: {e}")
        sys.exit(1)
    finally:
        if communicator:
            communicator.destroy()


if __name__ == "__main__":
    main()