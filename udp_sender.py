import socket
import time

# Completati cu adresa IP a platformei ESP32
PEER_IP = "192.168.89.30"
PEER_PORT = 10001

MESSAGE0 = b"GPIO4=0"
MESSAGE1 = b"GPIO4=1"
i = 0

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
while 1:
    try:
        i = i + 1
        if i%2 == 0:
            TO_SEND = MESSAGE0
        else:
            TO_SEND = MESSAGE1
        sock.sendto(TO_SEND, (PEER_IP, PEER_PORT))
        print("Am trimis mesajul: ", TO_SEND)
        time.sleep(2)
    except KeyboardInterrupt:
        break