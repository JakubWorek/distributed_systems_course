import select
import socket
import struct
import threading
import uuid

class Client:
    def __init__(self):
        self.client_id = str(uuid.uuid4())
        self.server_port = 5660
        self.multi_port = 5661
        self.server_ip = "127.0.0.1"
        self.nickname = None
        self.sending_mode = 'tcp'
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.multi_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    def set_nickname(self):
        self.nickname = input("Ustaw nick: ")

    def start_client(self):
        print('Klient wystartował!')
        self.tcp_socket.connect((self.server_ip, self.server_port))

        _, tcp_port = self.tcp_socket.getsockname()

        self.udp_socket.bind((self.server_ip, tcp_port))

        self.multi_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.multi_socket.bind(('', self.multi_port))
        multi_req = struct.pack("4sl", socket.inet_aton('224.1.1.1'), socket.INADDR_ANY)
        self.multi_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, multi_req)

        while self.nickname is None:
            self.set_nickname()
            self.tcp_socket.send(self.nickname.encode('utf-8'))
            response = self.tcp_socket.recv(1024).decode('utf-8')
            if response == "NICK_TAKEN":
                print("Nick jest już zajęty, wybierz inny.")
                self.nickname = None
                self.tcp_socket.close()
                self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.tcp_socket.connect((self.server_ip, self.server_port))
            else:
                break

        connecting_thread = threading.Thread(target=self._receive_message)
        connecting_thread.start()

        sending_thread = threading.Thread(target=self._write_message)
        sending_thread.start()

    def _receive_message(self):
        while True:
            ready_sockets, _, _ = select.select([self.tcp_socket, self.udp_socket, self.multi_socket], [], [])

            for sock in ready_sockets:
                try:
                    if sock is self.tcp_socket:
                        self._receive_tcp()
                    elif sock is self.udp_socket:
                        self._receive_udp()
                    elif sock is self.multi_socket:
                        self._receive_multicast()

                except (ConnectionResetError, ConnectionAbortedError, Exception):
                    print("Wystąpił błąd przy próbie odczytu wiadomości!")
                    exit(1)

    def _receive_tcp(self):
        message = self.tcp_socket.recv(1024).decode('utf-8')
        if message == "NICK":
            self.tcp_socket.send(self.nickname.encode('utf-8'))
        elif message == "NICK_TAKEN":
            print("Nick jest już zajęty, wybierz inny.")
        elif message == "SERVER_SHUTDOWN":
            print("Serwer zamknął połączenie.")
            raise Exception("Serwer zamknął połączenie.")
        else:
            message = "[TCP] " + message
            print(message)

    def _receive_udp(self):
        message = "[UDP] " + self.udp_socket.recv(1024).decode('utf-8')
        print(message)

    def _receive_multicast(self):
        message, addr = self.multi_socket.recvfrom(1024)
        decoded_message = message.decode('utf-8')
        client_id, actual_message = decoded_message.split(":", 1)
        if client_id == self.nickname:
            return
        print(f"[MULTI] {decoded_message}")

    def get_ascii_art(self):
        return """
   ____
 /\\' .\\    _____
/: \\___\\ / .  / \\
\\' / . / /____/ ..\\
 \\/___/  \\'  '\\  /
           \\'__'\\/
        """

    def _write_message(self):
        while True:
            input_message = input('')

            if input_message == 'U':
                self.sending_mode = 'udp'
                ascii_art = self.get_ascii_art()
                message = f"{self.nickname}:\n {ascii_art}"
                self.udp_socket.sendto(message.encode('utf-8'), (self.server_ip, self.server_port))
                self.sending_mode = 'tcp'
                continue
            elif input_message == 'T':
                self.sending_mode = 'tcp'
                continue
            elif input_message == 'M':
                self.sending_mode = 'multicast'
                continue

            message = f"{self.nickname}: {input_message}"
            if self.sending_mode == 'tcp':
                self.tcp_socket.send(message.encode('utf-8'))
            elif self.sending_mode == 'multicast':
                self.multi_socket.sendto(message.encode('utf-8'), ('224.1.1.1', self.multi_port))


if __name__ == '__main__':
    client = Client()
    client.start_client()