import random

# ==================================
# === 1. constants ===
# ==================================

GRID_SIZE = 15
CELL_SIZE = 50          
MARGIN = 30  
TOTAL_CELLS = GRID_SIZE * GRID_SIZE
LAST_CELL_INDEX = TOTAL_CELLS - 1
BOARD_SIZE = CELL_SIZE * GRID_SIZE

WIDTH =  BOARD_SIZE + MARGIN * 2 + 300 
HEIGHT = BOARD_SIZE + MARGIN * 2 

COLOR_BG = (50, 50, 50)
COLOR_LIGHT = (220, 220, 220)
COLOR_DARK = (180, 180, 180)

COLOR_RED = (255, 0, 0)
COLOR_CYAN   = (0, 255, 255)
COLOR_PURPLE = (160, 32, 240)
COLOR_LIME   = (50, 255, 50)

COLOR_12 = (128, 128, 128)
COLOR_13 = (200, 0, 150)
COLOR_14 = (255, 165, 0)
COLOR_14 = (255, 165, 0)
COLOR_23 = (100, 100, 255)
COLOR_24 = (150, 255, 150)
COLOR_34 = (100, 150, 100)


COLOR_MAP = {
    frozenset(['RED']): COLOR_RED,
    frozenset(['GREEN']): COLOR_CYAN,   
    frozenset(['BLUE']): COLOR_PURPLE,
    frozenset(['YELLOW']): COLOR_LIME,
    frozenset(['RED', 'GREEN']): COLOR_12,
    frozenset(['RED', 'BLUE']): COLOR_13,
    frozenset(['RED', 'YELLOW']): COLOR_14,
    frozenset(['GREEN', 'BLUE']): COLOR_23,
    frozenset(['GREEN', 'YELLOW']): COLOR_24,
    frozenset(['BLUE', 'YELLOW']): COLOR_34,
}

PLAYER_IDS = ['RED', 'GREEN', 'BLUE', 'YELLOW']

TOP_LEFT = 0
TOP_RIGHT = GRID_SIZE - 1
BOTTOM_LEFT = (GRID_SIZE - 1) * GRID_SIZE
BOTTOM_RIGHT = TOTAL_CELLS - 1

DICE_FACES = [
    None,'diewhite_border1','diewhite_border2','diewhite_border3',
    'diewhite_border4','diewhite_border5','diewhite_border6'
]

# ==================================
# === 2. state ===
# ==================================

players = {
    'RED':{"target":TOP_LEFT, "cells_occupied":[False] * TOTAL_CELLS, "color":COLOR_RED, "is_eliminated":False},
    'GREEN':{"target":BOTTOM_LEFT, "cells_occupied":[False] * TOTAL_CELLS, "color":COLOR_CYAN, "is_eliminated":False}, # ここ
    'BLUE':{"target":TOP_RIGHT, "cells_occupied":[False] * TOTAL_CELLS, "color":COLOR_PURPLE, "is_eliminated":False}, # ここ
    'YELLOW':{"target":BOTTOM_RIGHT, "cells_occupied":[False] * TOTAL_CELLS, "color":COLOR_LIME, "is_eliminated":False} # ここ
}

for p_id, pos in zip(PLAYER_IDS, [TOP_LEFT, BOTTOM_LEFT, TOP_RIGHT, BOTTOM_RIGHT]):
    players[p_id]['cells_occupied'][pos] = True

current_player_index = 0
current_player_id = PLAYER_IDS[current_player_index]
moves_left = 0
is_rolling_phase = False
game_over = False
WINNER_ID = None

TIME_LIMIT = 30.0
time_remaining = TIME_LIMIT

board_rects = []
for row in range(GRID_SIZE):
    for col in range(GRID_SIZE):
        board_rects.append(Rect((MARGIN + col * CELL_SIZE, MARGIN + row * CELL_SIZE), (CELL_SIZE, CELL_SIZE)))

dice = Actor(DICE_FACES[1])
dice.pos = (WIDTH - 150, HEIGHT // 2)

# ==================================
# === 3. initialization functions ===
# ==================================

def get_occupants(cell_index):
    return [p_id for p_id in PLAYER_IDS if players[p_id]['cells_occupied'][cell_index]]

def switch_turn():
    global current_player_id, current_player_index, time_remaining, moves_left, is_rolling_phase
    if game_over: return

    for _ in range(len(PLAYER_IDS)):
        current_player_index = (current_player_index + 1) % len(PLAYER_IDS)
        next_id = PLAYER_IDS[current_player_index]
        if not players[next_id]['is_eliminated']:
            current_player_id = next_id  
            moves_left = 0
            is_rolling_phase = False
            time_remaining = TIME_LIMIT
            return
    check_game_over()

def check_game_over():
    global game_over, WINNER_ID
    active = [p for p in PLAYER_IDS if not players[p]['is_eliminated']]
    if len(active) <= 1:
        game_over = True
        if active:
            WINNER_ID = active[0]

def roll_dice():
    global moves_left, is_rolling_phase
    random_face = random.randint(1, 6)
    moves_left = random_face 
    dice.image = DICE_FACES[random_face]
    is_rolling_phase = True

# ==================================
# === 4. game functions ===
# ==================================

def on_key_down(key):
    global moves_left,current_player_id,is_rolling_phase,time_remaining
    if game_over:return

    if key == keys.SPACE and moves_left == 0:
        roll_dice()
        return
    
    if moves_left == 0:return

    my_data = players[current_player_id]
    target_idx = my_data["target"]
    my_cells = my_data["cells_occupied"]
    row, col = target_idx // GRID_SIZE, target_idx % GRID_SIZE
    next_idx = -1

    

    if key == keys.LEFT and col > 0:next_idx = target_idx - 1
    elif key == keys.RIGHT and col < GRID_SIZE - 1:next_idx = target_idx + 1
    elif key == keys.UP and row > 0:next_idx = target_idx - GRID_SIZE
    elif key == keys.DOWN and row < GRID_SIZE - 1:next_idx = target_idx + GRID_SIZE

    if next_idx != -1:
        occupants = get_occupants(next_idx)

        if current_player_id in occupants:
            my_data["target"] = next_idx
            moves_left -= 1

        elif len(occupants) < 2:
            my_data["cells_occupied"][next_idx] = True
            my_data["target"] = next_idx
            moves_left -= 1

        else:
            time_remaining -= 1.0
            return
        
        if is_rolling_phase: is_rolling_phase = False
        if moves_left == 0:switch_turn()

def on_mouse_down(pos):
    global is_rolling_phase,current_player_id
    if not is_rolling_phase:
        return
    my_data = players[current_player_id]
    for i, rect in enumerate(board_rects):
        if rect.collidepoint(pos) and my_data["cells_occupied"][i]:
            my_data["target"] = i
            return
        
# ==================================
# === 5. draw function ===
# ==================================
        
def draw():
    screen.clear()

    for i, rect in enumerate(board_rects):
        row, col = i // GRID_SIZE, i % GRID_SIZE
        occupants = get_occupants(i)

        if not occupants:
            color = COLOR_DARK if (row + col) % 2 == 0 else COLOR_LIGHT
        else:
            color = COLOR_MAP.get(frozenset(occupants), (150, 150, 150))

        screen.draw.filled_rect(rect, color)

        if i == players[current_player_id]["target"]:
            screen.draw.rect(rect, 'black')

    dice.draw()
    if moves_left == 0 and not is_rolling_phase:
        # 手番インジケーター
        indicator_rect = Rect((dice.x - 40, dice.y - 40), (80, 80))
        screen.draw.filled_rect(indicator_rect, players[current_player_id]["color"])

    BAR_WIDTH = WIDTH - 2 * MARGIN
    time_ratio = max(0, time_remaining / TIME_LIMIT)
    screen.draw.filled_rect(Rect((MARGIN, HEIGHT - 25), (BAR_WIDTH, 15)), (100, 100, 100))
    bar_color = 'green' if time_ratio > 0.5 else 'yellow' if time_ratio > 0.2 else 'red'
    screen.draw.filled_rect(Rect((MARGIN, HEIGHT - 25), (BAR_WIDTH * time_ratio, 15)), bar_color)

    if game_over:
        screen.draw.text(f"WINNER: {WINNER_ID}", center=(WIDTH//2, HEIGHT//2), fontsize=100, color='white', shadow=(2,2))

# ==================================
# ===6.update function===
# ==================================

def update(dt):
    global time_remaining, game_over, moves_left, is_rolling_phase
    if game_over: return

    if moves_left > 0 or is_rolling_phase:
        time_remaining -= dt
        if time_remaining <= 0:
            players[current_player_id]["is_eliminated"] = True
            check_game_over()
            if not game_over: switch_turn()