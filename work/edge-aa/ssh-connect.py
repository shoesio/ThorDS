import os
import select
import socket

# One connection per SSH attempt: parallel abandoned connections trigger sshd penalties.
with socket.create_connection(("192.168.0.143", 22), timeout=12) as connection:
    connection.settimeout(None)
    while True:
        ready, _, _ = select.select([connection, 0], [], [])
        if connection in ready:
            data = connection.recv(65536)
            if not data:
                break
            view = memoryview(data)
            while view:
                view = view[os.write(1, view):]
        if 0 in ready:
            data = os.read(0, 65536)
            if not data:
                break
            connection.sendall(data)
