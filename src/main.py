from cvg.socket.server import ServerSocket

from cvg.socket.packet import Address, PacketType, PacketData

#print(socket.packet.PacketData(b"\x02"))

print(Address(("test", "a")))

server = ServerSocket()

@server.start()
def on_packet(packet: PacketData, address: Address):
    pass