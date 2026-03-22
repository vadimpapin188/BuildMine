from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursinanetworking import *
import json
import math

app = Ursina()
#----------------Welcome to BuildMine editor!----------------

# --- Its settings of world and window. ---
window.title = "BuildMine 1.0.5 - Official Release"
window.exit_button.visible = False
scene.fog_color = color.rgb(170, 190, 220)
scene.fog_density = (15, 65)

# ---  Dictionary of Blocks and their properties ---
BLOCKS = [
    {'name': 'Grass', 'tex': 'my_grass'},
    {'name': 'Dirt', 'tex': 'my_dirt'}, 
    {'name': 'Brick', 'tex': 'my_brick'},
    {'name': 'Teleport', 'tex': 'my_teleport'}
]
current_slot = 0
voxels = []
player = None
client = None
flying = False

# --- Lodic of blocks ---
class Voxel(Button):
    def __init__(self, position=(0,0,0), texture='my_grass'):
        super().__init__(
            parent=scene, position=position, model='cube', origin_y=0.5,
            texture=texture, color=color.white, collider='box'
        )
        if self.texture: self.texture.filtering = False
        voxels.append(self)

    def input(self, key):
        if self.hovered and player and not pause_menu.enabled:
            if key == 'left mouse down':
                new_v = Voxel(position=self.position + mouse.normal, texture=BLOCKS[current_slot]['tex'])
                hand.position = Vec3(0.4, -0.4, 0.8)
                if client: client.send_message("place_block", {"pos": new_v.position, "tex": new_v.texture.name})
            if key == 'right mouse down':
                if self in voxels: voxels.remove(self)
                destroy(self)

# --- Its logic of saving worlds. How it working on end this code ---
def save_world():
    data = [{"pos": (v.x, v.y, v.z), "tex": v.texture.name} for v in voxels]
    with open('world_save.json', 'w') as f:
        json.dump(data, f)
    print("World saved (local)!")

def load_world():
    try:
        with open('world_save.json', 'r') as f:
            data = json.load(f)
            for item in data: Voxel(position=item['pos'], texture=item['tex'])
        print("World loading!!")
    except:
        for z in range(15):
            for x in range(15): Voxel(position=(x,0,z), texture='my_dirt')

# --- UI ---
hotbar = Entity(parent=camera.ui, model='quad', scale=(0.4, 0.08), position=(0, -0.45), color=color.black66)
selector = Entity(parent=hotbar, model='quad', scale=(0.25, 1.2), color=color.white, z=-0.1, x=-0.375)
hand = Entity(parent=camera.ui, model='cube', scale=(0.2, 0.4, 0.6), rotation=(35,-30,10), position=(0.6, -0.6, 1), enabled=False)

def update_ui():
    selector.x = -0.375 + (current_slot * 0.25)
    hand.texture = BLOCKS[current_slot]['tex']

# Escape (Menu of Pause)
pause_menu = Entity(parent=camera.ui, model='quad', color=color.black66, scale=(2, 2), enabled=False)
Button(text="Resume", scale=(0.3, 0.05), y=0.1, parent=pause_menu).on_click = lambda: resume()
Button(text="Save World", scale=(0.3, 0.05), y=0, parent=pause_menu).on_click = save_world
Button(text="Exit", scale=(0.3, 0.05), y=-0.1, parent=pause_menu).on_click = application.quit

def resume():
    pause_menu.enabled = False
    mouse.locked = True
    player.enabled = True

# --- Home  ---
main_menu = Entity(parent=camera.ui)
Entity(parent=main_menu, model='quad', texture='my_grass', scale=(2,2), z=1)
Text(text="BUILDMINE", parent=main_menu, y=0.3, scale=5, origin=(0,0), color=color.yellow)
ip_input = InputField(default_value='localhost', y=0.05, parent=main_menu)
Text(text="Server IP:", parent=main_menu, y=0.1, x=-0.05)

def start_game():
    global player, client
    try: client = UrsinaNetworkingClient(ip_input.text, 25565)
    except: print("Offline Mode")
    
    main_menu.enabled = False
    mouse.locked = True
    player = FirstPersonController()
    player.cursor.model = 'quad'; player.cursor.scale = 0.012
    hand.enabled = True
    load_world()
    update_ui()

Button(text="JOIN SERVER / START", color=color.green, y=-0.1, scale=(0.3, 0.08), parent=main_menu).on_click = start_game

# --- Updates ---
def update():
    global flying
    if player and not pause_menu.enabled:
        if client: client.process_net_events()
        
        # Респаун и полет
        if player.y < -30: player.position = (0, 10, 0)
        
        if flying:
            player.gravity = 0
            if held_keys['space']: player.y += 10 * time.dt
            if held_keys['left shift'] or held_keys['x']: player.y -= 10 * time.dt
        else:
            player.gravity = 1

        hand.position = lerp(hand.position, Vec3(0.6, -0.6, 1), time.dt * 12)

def input(key):
    global current_slot, flying
    if key == 'escape' and player:
        pause_menu.enabled = not pause_menu.enabled
        mouse.locked = not pause_menu.enabled
        player.enabled = not pause_menu.enabled
    
    if key == 'f' and player:
        flying = not flying
        if flying: player.grounded = True
        
    if key == 'k': save_world()

    if player and not pause_menu.enabled:
        if key in ('1', '2', '3', '4'):
            current_slot = int(key) - 1
            update_ui()
        if key == 'scroll up': current_slot = (current_slot + 1) % 4; update_ui()
        if key == 'scroll down': current_slot = (current_slot - 1) % 4; update_ui()

app.run()
#----How working save of worlds?-----
#Your world - its JSON file. He saved of x and y (Coords) of blocks and how blocks is there are some and where they are.-
