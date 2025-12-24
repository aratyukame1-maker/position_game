# -*- coding: utf-8 -*-
import random

# ==================================
# === 1. constants ===
# ==================================

GRID_SIZE = 14
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
COLOR_BLUE = (0, 0, 255)

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
        "target":0, 
        "cells_occupied":[False] * TOTAL_CELLS,
        "color":COLOR_RED
    },
    'BLUE':{
        "target":LAST_CELL_INDEX, 
        "cells_occupied":[False] * TOTAL_CELLS,
        "color":COLOR_BLUE
    }
}

players['RED']['cells_occupied'][0] = True
players['BLUE']['cells_occupied'][LAST_CELL_INDEX] = True

# player ID
current_player_id = 'RED'

is_rolling_phase = False

moves_left = 0

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
    global current_player_id,time_remaining
    current_player_id = 'BLUE' if current_player_id == 'RED' else 'RED'
    time_remaining = TIME_LIMIT

def roll_dice():
    global moves_left, is_rolling_phase
    random_face = random.randint(1, 6)
    moves_left = random_face 
    dice.image = DICE_FACES[random_face]
    is_rolling_phase = True

#==================================
#=== 5. event handlers ===
#==================================

def on_key_down(key):
    global moves_left,current_player_id,is_rolling_phase
    opponent_id = 'BLUE' if current_player_id == 'RED' else 'RED'

    my_data = players[current_player_id]    
    opponent_data = players[opponent_id]

    target_idx = my_data["target"]
    my_cells = my_data["cells_occupied"]
    opponent_cells = opponent_data["cells_occupied"]


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

    if next_cell != -1:
        if my_cells[next_cell] or opponent_cells[next_cell]:
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

        if players['RED']['cells_occupied'][i]:
            color = COLOR_RED
        elif players['BLUE']['cells_occupied'][i]:
            color = COLOR_BLUE

        screen.draw.filled_rect(rect, color)

        #if i == (target_RED if is_turn else target_BLUE):
        if i == player_data["target"]:
            screen.draw.rect(rect,'green')
        

# ==================================
# === 7. update function ===
# ==================================

def update(dt):
    global time_remaining, is_game_paused
    if is_game_paused:
        return
    
    if moves_left == 0 and not is_rolling_phase:
        return

    time_remaining -= dt

    if time_remaining <= 0:
        time_remaining = 0
        



