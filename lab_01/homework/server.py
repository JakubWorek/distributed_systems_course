import datetime
import socket
import queue
from concurrent.futures import ThreadPoolExecutor

class Server:
    def __init__(self):
        self.server_port = 5660
        self.server_ip = '127.0.0.1'
        self.clients = []
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.client_queue = queue.Queue()
        self.executor = ThreadPoolExecutor(max_workers=5)

    def start_server(self):
        try:
            print(f'Server listening on port {self.server_port}')
            self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.tcp_socket.bind((self.server_ip, self.server_port))
            self.tcp_socket.listen(3)
            self.udp_socket.bind((self.server_ip, self.server_port))

            self.executor.submit(self._connect_with_tcp_client)
            self.executor.submit(self._handle_udp_message)

            for _ in range(3):
                self.executor.submit(self._worker_thread)

        except OSError:
            print("Adres już w użyciu! Zakończ poprzednie połączenia.")
            return

    def _broadcast_tcp(self, message, address):
        print(f"[TCP][{address}][{datetime.datetime.now()}] Wysyłanie wiadomości do wszystkich")
        for client in self.clients:
            if client[2] != address:
                client[0].send(message)

    def _broadcast_udp(self, message, address):
        print(f"[UDP][{address}][{datetime.datetime.now()}] Wysyłanie wiadomości do wszystkich")
        for client in self.clients:
            if client[2] != address:
                self.udp_socket.sendto(message, client[2])

    def _handle_tcp_message(self, client):
        while True:
            try:
                message = client[0].recv(1024)
                if not message:
                    raise Exception("Klient zakończył połączenie.")

                print(f"[TCP][{client[2]}][{datetime.datetime.now()}] Otrzymano wiadomość od {client[1]}")
                self._broadcast_tcp(message, client[2])

            except Exception:
                self._disconnect_client(client)
                return

    def _handle_udp_message(self):
        while True:
            message, address = self.udp_socket.recvfrom(1024)
            nickname = next((client[1] for client in self.clients if client[2] == address), None)
            print(f"[UDP][{address}][{datetime.datetime.now()}] Otrzymano wiadomość od {nickname}")
            self._broadcast_udp(message, address)

    def _disconnect_client(self, client):
        client[0].close()
        self.clients.remove(client)
        nickname = client[1]
        print(f"[{datetime.datetime.now()}] {nickname} opuścił czat")
        self._broadcast_tcp(f"{nickname} opuścił czat.".encode('utf-8'), client[2])

    def _connect_with_tcp_client(self):
        while True:
            client, address = self.tcp_socket.accept()
            print(f"[{datetime.datetime.now()}] {address} połączony!")

            nickname = client.recv(1024).decode('utf-8')

            if any(nick == nickname for _, nick, _ in self.clients):
                client.send("NICK_TAKEN".encode('utf-8'))
                print(f"[{datetime.datetime.now()}] Nick {nickname} jest już zajęty!")
                client.close() 
                continue

            print(f"Ustawiono nick: {nickname}")
            client.send('NICK'.encode('utf-8'))

            self.clients.append((client, nickname, address))
            self._broadcast_tcp(f"{nickname} dołączył do czatu.".encode('utf-8'), address)
            client.send("Połączono z serwerem!".encode('utf-8'))

            self.client_queue.put((client, nickname, address))

    def _worker_thread(self):
        while True:
            client = self.client_queue.get()
            if client:
                self._handle_tcp_message(client)
                self.client_queue.task_done()

    def close_connections(self):
        for client in self.clients:
            client[0].send("SERVER_SHUTDOWN".encode('utf-8'))
            client[0].close()
        self.executor.shutdown(wait=True)

if __name__ == '__main__':
    server = Server()
    server.start_server()
