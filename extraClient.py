import socket

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(('192.168.0.27', 9964))
    print('Connected')
    while True:
        cmd = input()
        s.sendall(cmd.encode('utf-8'))
        data = s.recv(1024)
        if not data:
            break