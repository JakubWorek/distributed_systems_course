import socket;

serverIP = "127.0.0.1"
serverPort = 9009
msg = "Ping Python Udp!"

if __name__ == '__main__':
    print('PYTHON UDP CLIENT')
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.sendto(bytes(msg, 'UTF-8'), (serverIP, serverPort))

    buff, address = client.recvfrom(1024)
    msg = str(buff, 'UTF-8')
    print("received msg: " + str(buff, 'UTF-8'))
