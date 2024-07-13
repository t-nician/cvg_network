import threading

from cvg.socket.server import ServerSocket

from cvg.socket.packet import Address, PacketType, PacketData

#print(socket.packet.PacketData(b"\x02"))

def server_thread():
    server = ServerSocket()

    @server.start()
    def on_packet(packet: PacketData, address: Address):
        return PacketData(b"go away!", PacketType.DENIED)

threading.Thread(target=server_thread).start()


