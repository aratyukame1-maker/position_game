import random

# =================================================================
# 1. CONSTANTS (Configuration)
# =================================================================
# Board settings
GRID_SIZE = 15   
CELL_SIZE = 50          
MARGIN = 30  
TOTAL_CELLS = GRID_SIZE * GRID_SIZE
LAST_CELL_INDEX = TOTAL_CELLS - 1
BOARD_SIZE = CELL_SIZE * GRID_SIZE
TOP_LEFT = 0
TOP_RIGHT = GRID_SIZE - 1
BOTTOM_LEFT = (GRID_SIZE - 1) * GRID_SIZE
BOTTOM_RIGHT = TOTAL_CELLS - 1

WIDTH =  BOARD_SIZE + MARGIN * 2 + 300 
HEIGHT = BOARD_SIZE + MARGIN * 2 

COLOR_BG = (50, 50, 50)
COLOR_LIGHT = (220, 220, 220)
COLOR_DARK = (180, 180, 180)

COLOR_RED = (255, 0, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_YELLOW = (255, 255, 0)
COLOR_GREEN = (0, 255, 0)

PLAYER_IDS = ['RED', 'BLUE', 'YELLOW', 'GREEN']

board_rects = []

DICE_FACES = [
    None,'diewhite_border1','diewhite_border2','diewhite_border3',
    'diewhite_border4','diewhite_border5','diewhite_border6'
]

# ==================================
# === 2. state ===
# ==================================

players = {
    'RED':{
        "target":TOP_LEFT, 
        "cells_occupied":[False] * TOTAL_CELLS,
        "color":COLOR_RED,
        "is_eliminated":False
    },
    'BLUE':{
        "target":BOTTOM_RIGHT, 
        "cells_occupied":[False] * TOTAL_CELLS,
        "color":COLOR_BLUE,
        "is_eliminated":False
    },
    'YELLOW':{
        "target":TOP_RIGHT, 
        "cells_occupied":[False] * TOTAL_CELLS,
        "color":COLOR_YELLOW,
        "is_eliminated":False
    },
    'GREEN':{
        "target":BOTTOM_LEFT, 
        "cells_occupied":[False] * TOTAL_CELLS,
        "color":COLOR_GREEN,
        "is_eliminated":False
    }

}

players['RED']['cells_occupied'][TOP_LEFT] = True
players['BLUE']['cells_occupied'][BOTTOM_RIGHT] = True
players['YELLOW']['cells_occupied'][TOP_RIGHT] = True
players['GREEN']['cells_occupied'][BOTTOM_LEFT] = True

current_player_index = 0
current_player_id = PLAYER_IDS[current_player_index]

is_rolling_phase = False

moves_left = 0

game_over = False
WINNER_ID = None

board_rects = []
dice = Actor(DICE_FACES[1])
dice.pos = (WIDTH - 150, HEIGHT // 2)

TIME_LIMIT = 30.0
time_remaining = TIME_LIMIT
is_game_paused = False

# ==================================
# === 3. initialization functions ===
# ==================================

def create_board():
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x = MARGIN + col * CELL_SIZE
            y = MARGIN + row * CELL_SIZE
            rect = Rect((x, y), (CELL_SIZE, CELL_SIZE))
            board_rects.append(rect)

create_board()

#==================================
#=== 4. game functions ===
#==================================

def switch_turn():
    global current_player_id,time_remaining,current_player_index,game_over,WINNER_ID,moves_left,is_rolling_phase
    if game_over:
        return
    
    found_next_player = False

    for _ in range(len(PLAYER_IDS)):
        current_player_index = (current_player_index + 1) % len(PLAYER_IDS)
        current_player_id = PLAYER_IDS[current_player_index]
        if not players[current_player_id]["is_eliminated"]:
            moves_left = 0
            is_rolling_phase = False
            time_remaining = TIME_LIMIT
            found_next_player = True
            return 
        
    if not found_next_player:
        check_game_over()
        
def check_game_over():
    global game_over, WINNER_ID
    eliminated_count = 0
    winner_id = None
    for player_id in PLAYER_IDS:
        if players[player_id]["is_eliminated"]:
            eliminated_count += 1
        else:
            winner_id = player_id
    if eliminated_count == len(PLAYER_IDS) - 1:
        game_over = True
        WINNER_ID = winner_id

def roll_dice():
    global moves_left, is_rolling_phase
    random_face = random.randint(1, 6)
    moves_left = random_face 
    dice.image = DICE_FACES[random_face]
    is_rolling_phase = True

#==================================
#=== 5. event handlers ===
#==================================

def is_cell_occupied_by_any_player(cell_index):
    for player_id in PLAYER_IDS:
        if player_id != current_player_id:
            if players[player_id]["cells_occupied"][cell_index]:
                return True
    return False

def on_key_down(key):
    global moves_left,current_player_id,is_rolling_phase,time_remaining

    my_data = players[current_player_id] 
    target_idx = my_data["target"]
    my_cells = my_data["cells_occupied"]


    if key == keys.SPACE and moves_left == 0:
        roll_dice()
        return
    
    if moves_left == 0:
        return


    row = target_idx // GRID_SIZE
    col = target_idx % GRID_SIZE

    next_cell = -1
    
    if key == keys.LEFT and col > 0:
        next_cell = target_idx - 1
    elif key == keys.RIGHT and col < GRID_SIZE - 1:
        next_cell = target_idx + 1
    elif key == keys.UP and row > 0:
        next_cell = target_idx - GRID_SIZE
    elif key == keys.DOWN and row < GRID_SIZE - 1:
        next_cell = target_idx + GRID_SIZE

    if next_cell == -1:
        time_remaining -= 1.0
        if time_remaining < 0:time_remaining = 0

    if next_cell != -1:
        if my_cells[next_cell] or is_cell_occupied_by_any_player(next_cell):
            time_remaining -= 2.0
            if time_remaining < 0:time_remaining = 0
            return
        
        my_cells[next_cell] = True
        my_data["target"] = next_cell
        moves_left -= 1
        if is_rolling_phase:
            is_rolling_phase = False

        if moves_left == 0:
            switch_turn()


def on_mouse_down(pos):
    global is_rolling_phase
    if not is_rolling_phase:
        return
    
    global current_player_id

    my_data = players[current_player_id]    
    my_cells = my_data["cells_occupied"]


    for i, rect in enumerate(board_rects):
        if rect.collidepoint(pos):
            if my_cells[i]:
                my_data["target"] = i
                return
            
# ==================================
# === 6. draw function ===
# ==================================

def draw():
    player_data = players[current_player_id]

    screen.clear()
    dice.draw()

    if moves_left == 0 and not is_rolling_phase:
        turn_color = player_data["color"]

        rect_width = dice.width
        rect_height = dice.height
        
        turn_indicator_rect = Rect(
            (dice.pos[0] - rect_width // 2, dice.pos[1] - rect_height // 2), 
            (rect_width, rect_height)
        )

        screen.draw.filled_rect(turn_indicator_rect, turn_color)  

    # time display
    BAR_HEIGHT = 20
    BAR_WIDTH = WIDTH - 2 * MARGIN

    time_ratio = time_remaining / TIME_LIMIT
    current_bar_width = BAR_WIDTH * time_ratio
    bar_color = 'green'
    if time_ratio < 0.33:
        bar_color = 'red'
    elif time_ratio < 0.66:
        bar_color = 'yellow'
    background_rect = Rect((MARGIN, HEIGHT  - BAR_HEIGHT -5), (BAR_WIDTH, BAR_HEIGHT))
    screen.draw.filled_rect(background_rect, (100, 100, 100))
    progress_rect = Rect((MARGIN, HEIGHT - BAR_HEIGHT -5), (current_bar_width, BAR_HEIGHT))
    screen.draw.filled_rect(progress_rect, bar_color)


        

    for i, rect in enumerate(board_rects):
        row = i // GRID_SIZE
        col = i % GRID_SIZE

        color = COLOR_DARK if (row + col) % 2 == 0 else COLOR_LIGHT

        for player_id in PLAYER_IDS:
            if players[player_id]["cells_occupied"][i]:
                if players[player_id]["is_eliminated"]:
                    color = (150,150,150)
                else:
                    color = players[player_id]["color"]
                break

        screen.draw.filled_rect(rect, color)

        #if i == (target_RED if is_turn else target_BLUE):
        if i == player_data["target"]:
            screen.draw.rect(rect,'black')
        

# ==================================
# === 7. update function ===
# ==================================

def update(dt):
    global time_remaining, is_game_paused,game_over
    if is_game_paused or game_over:
        return
    
    if moves_left == 0 and not is_rolling_phase:
        return

    time_remaining -= dt


    if time_remaining <= 0:
        time_remaining = 0

        players[current_player_id]["is_eliminated"] = True 
        print(f"{current_player_id} is eliminated due to time out!")

        check_game_over()
        if not game_over:
            switch_turn()
        



