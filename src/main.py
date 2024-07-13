from cvg import socket

#print(socket.packet.PacketData(b"\x02"))

server = socket.server.ServerSocket()

@server.start()
def on_packet(packet, address):
    pass