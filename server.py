from ursinanetworking import *
#--Welcome to server.py editor!--

#Created server on port 25565
server = UrsinaNetworkingServer("localhost", 25565)
#Events of server in console
@server.event
def onClientConnected(client):
    print(f"Player {client.id} join a BuildMine!") #If goin - print of client id join in your server.

@server.event
def onClientDisconnected(client):
    print(f"Player {client.id} left the game.") #if left - print of client id left your server.

while True:
    server.process_net_events() #Loop for Events
