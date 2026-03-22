from ursinanetworking import *

# Создаем сервер на порту 25565 (как в Майне!)
server = UrsinaNetworkingServer("localhost", 25565)

@server.event
def onClientConnected(client):
    print(f"Игрок {client.id} подключился к BuildMine!")

@server.event
def onClientDisconnected(client):
    print(f"Игрок {client.id} покинул мир.")

while True:
    server.process_net_events()
