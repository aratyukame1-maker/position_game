# Imports
import random
import pgzrun
from pgzero.builtins import Actor, Rect

if False:
    screen: any = None
    keys: any = None

# Constants
GRID_SIZE = 13
CELL_SIZE = 40    
MARGIN = 30  
TOTAL_CELLS = GRID_SIZE ** 2

"""Calculate window size based on grid and UI space"""
WIDTH = GRID_SIZE * CELL_SIZE + MARGIN * 2 + 300 
HEIGHT = GRID_SIZE * CELL_SIZE + MARGIN * 2 + 50

COLORS = {
    'BG': (50, 50, 50),
    'EMPTY_A': (220, 220, 220),'EMPTY_B': (180, 180, 180),
    'RED': (255, 0, 0),'BLUE': (0, 0, 255),
    'HIGHLIGHT': (0, 255, 0),
}

TIME_LIMIT = 30.0

DICE_FACES = [
    None,'diewhite_border1','diewhite_border2','diewhite_border3',
    'diewhite_border4','diewhite_border5','diewhite_border6'
]

# Classes
class GameState:
    """Manages the overall game state."""
    def __init__(self):
        self.turn_index = 0
        self.moves_left = 0
        self.time_remaining = TIME_LIMIT
        self.is_rolling_phase = False # True when player is selecting a start point after roll
    
class Player:
    """Represents a player and their occupied territory."""
    def __init__(self,name,color,start_idx):
        self.name = name
        self.color = color
        self.target = start_idx
        self.cells_occupied = [False] * TOTAL_CELLS
        self.cells_occupied[start_idx] = True

    def move(self, index):
        """Mark a cell as occupied and update position."""
        self.cells_occupied[index] = True
        self.current_pos = index

    def draw_occupied(self):
        """Draw all occupied cells for this player."""
        for i, occupied in enumerate(self.cells_occupied):
            if occupied:
                screen.draw.filled_rect(board_rects[i], self.color)

    def draw_target_highlight(self):
        """Highlight the target cell."""
        screen.draw.rect(board_rects[self.target], COLORS['HIGHLIGHT'])


# Initialization
state = GameState()
red_player = Player('RED', COLORS['RED'], 0)
blue_player = Player('BLUE', COLORS['BLUE'], TOTAL_CELLS - 1)
players = [red_player, blue_player]

board_rects = [
    Rect((MARGIN + (i % GRID_SIZE) * CELL_SIZE, MARGIN + (i // GRID_SIZE) * CELL_SIZE), 
         (CELL_SIZE - 2, CELL_SIZE - 2))
    for i in range(TOTAL_CELLS)
]

# Initialize dice Actor
dice = Actor(DICE_FACES[1])
dice.pos = (WIDTH - 150, HEIGHT // 2 - MARGIN)

# Logic & Helpers
def get_current_player():return players[state.turn_index]
def get_opponent():return players[(state.turn_index + 1) % 2]

def switch_turn():
    """Reset turn state and switch to the next player."""
    state.turn_index = (state.turn_index + 1) % 2
    state.moves_left = 0
    state.is_rolling_phase = False
    state.time_remaining = TIME_LIMIT

def roll_dice():
    """Roll the dice and set the number of moves available."""
    roll = random.randint(1, 6)
    state.moves_left = roll
    dice.image = DICE_FACES[roll]
    state.is_rolling_phase = True

# Input Handlers
def on_mouse_down(pos):
    """Handle cell selection for the starting point of a move."""
    if not state.is_rolling_phase:return
    
    p = get_current_player()
    for i, rect in enumerate(board_rects):
        if rect.collidepoint(pos):
            if p.cells_occupied[i]:
                p.target = i

def on_key_down(key):
    """Handle dice rolling and player movement."""

    # Phase 1: Roll the dice
    if state.moves_left == 0:
        if key == keys.SPACE:roll_dice()
        return
    
    # Phase 2: Move the player
    p = get_current_player()
    opp = get_opponent()
    
    row, col = divmod(p.target, GRID_SIZE)
    move_map = {keys.UP: (-1,0), keys.DOWN: (1,0), keys.LEFT: (0,-1), keys.RIGHT: (0,1)}

    if key in move_map:
        dr, dc = move_map[key]
        nr, nc = row + dr, col + dc
        
        # Check boundaries
        if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
            n_idx = nr * GRID_SIZE + nc
            # Check if cell is not occupied by any player
            if not p.cells_occupied[n_idx] and not opp.cells_occupied[n_idx]:
                p.cells_occupied[n_idx] = True
                p.target = n_idx
                state.moves_left -= 1
                state.is_rolling_phase = False
                
                # Switch turn if all moves are used
                if state.moves_left == 0:
                    switch_turn()
    
# Game Loop
def update(dt):
    """Update game timer."""
    if state.is_rolling_phase or state.moves_left > 0:
        state.time_remaining -= dt
        if state.time_remaining <= 0:
            switch_turn()

def draw():
    screen.fill(COLORS['BG'])
    p = get_current_player()

    # Draw the game board
    for i, rect in enumerate(board_rects):
        r, c = divmod(i, GRID_SIZE)
        # Checkerboard pattern for empty cells
        color = COLORS['EMPTY_A'] if (r + c) % 2 == 0 else COLORS['EMPTY_B']
        screen.draw.filled_rect(rect, color)

    for p in players:
        p.draw_occupied()

    get_current_player().draw_target_highlight()
    dice.draw()

    # Draw player color indicator around dice when it's time to roll
    if state.moves_left == 0:
        indicator_rect = Rect((dice.x - dice.width//2, dice.y - dice.height//2), 
                              (dice.width, dice.height))
        screen.draw.filled_rect(indicator_rect, p.color)

    draw_ui()

def draw_ui():
    """Render the time limit progress bar."""
    BAR_WIDTH = WIDTH - (MARGIN * 2)
    time_ratio = state.time_remaining / TIME_LIMIT
    
    # Change bar color based on remaining time
    bar_color = "green"
    if time_ratio < 0.3: bar_color = "red"
    elif time_ratio < 0.6: bar_color = "yellow"
    
    # Draw progress bar background and foreground
    bg_rect = Rect((MARGIN, HEIGHT - 35), (BAR_WIDTH, 20))
    screen.draw.filled_rect(bg_rect, (80, 80, 80))
    progress_rect = Rect((MARGIN, HEIGHT - 35), (BAR_WIDTH * max(0, time_ratio), 20))
    screen.draw.filled_rect(progress_rect, bar_color)

pgzrun.go()
