import socket

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(('192.168.0.27', 9964))
    while True:
        cmd = input()
        s.sendall(data)
        if not s:
            break