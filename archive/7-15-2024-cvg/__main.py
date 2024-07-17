import time
import threading

from cvg.socket.server import ServerSocket
from cvg.socket.client import ClientSocket

from cvg.socket.packet import Address, PacketType, PacketData

def server_thread():
    server = ServerSocket(key=b"secretkey")

    @server.start(PacketType.COMMAND)
    def on_packet(packet: PacketData, address: Address):
        if packet.payload.lower() == b"hello":
            return PacketData(b"nope!", PacketType.DENIED)
        return b"go away!"

threading.Thread(target=server_thread).start()

time.sleep(2)

client = ClientSocket(server_key=b"secretkey")

client.login()

print(client.command(b"hello", b"\x03"))
print(client.command(b"true", b"\x33"))