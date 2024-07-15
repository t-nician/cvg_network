# Now we start implementing event.py into the socket implementation >:D

from cvg.socket import server

test_server = server.ServerSocket(key=b"hi")

test_server.event_pool.emit(server.PacketType.ACCESS)

test_server.start()