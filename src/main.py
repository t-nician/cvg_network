# Now we start implementing event.py into the socket implementation >:D

from cvg.socket import server

test_server = server.ServerSocket(key=b"hi")

test_server.event_pool.emit(
    server.PacketType.ACCESS,
    server.PacketData(b"", server.PacketType.ACCESS),
    server.socket(server.AF_INET, server.SOCK_STREAM),
    server.Address(("127.0.0.1", 5000))
)

test_server.start()