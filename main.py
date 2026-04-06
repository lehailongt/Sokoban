import sys, pygame, time
from constants import *
from IDA_star import IDAStarSolver
from sokoban_game import SokobanGame

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sokoban - Game xếp thùng với IDA*")

# Font
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

# Biến toàn cục
clock = pygame.time.Clock()
level_number = 0
algorithm = "IDA* Algorithm"


def load_image(filename, default_color):
    """Load ảnh từ file"""
    try:
        path = f"images/{filename}"
        image = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(image, (CELL_SIZE, CELL_SIZE))
    except:
        # Tạo surface màu thay thế
        surface = pygame.Surface((CELL_SIZE, CELL_SIZE))
        surface.fill(default_color)
        pygame.draw.rect(surface, (255, 255, 255), surface.get_rect(), 2)
        return surface

# Load hình ảnh
images = {
    'wall': load_image('wall.png', COLORS['wall']),
    'floor': load_image('floor.png', COLORS['floor']),
    'player': load_image('player.png', COLORS['player']),
    'player_on_goal': load_image('player_on_goal.png', COLORS['player_on_goal']),
    'box': load_image('box.png', COLORS['box']),
    'box_on_goal': load_image('box_on_goal.png', COLORS['box_on_goal']),
    'goal': load_image('goal.png', COLORS['goal']),
    'background': load_image('background.jpg', COLORS['background']),
    'other': load_image('', COLORS['other'])
}

def parse_level(level_number):
    """Chuyển map kí tự: mảng text -> mảng 2 chiều từng kí tự"""
    level_data = LEVELS[level_number]
    
    board = [list(row) for row in level_data]
    return board

def update_screen():
    pygame.display.flip()
    clock.tick(60)

def wait_time():
    """Chờ mà không làm đơ game"""
    pygame.time.delay(STEP_TIME)  # delay trực tiếp
    pygame.event.pump()  # Xử lý sự kiện sau delay

def draw_map(board):
    board_width = len(board[0]) * CELL_SIZE
    board_height = len(board) * CELL_SIZE
    offset_x = (WIDTH - board_width) // 2
    offset_y = (HEIGHT - board_height) // 2

    # Xóa map cũ (FUll khối cả chiều dài witdh)
    rect = pygame.Rect(0, offset_y, WIDTH, board_height)
    pygame.draw.rect(screen, BLACK, rect)
    
    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            x = offset_x + j * CELL_SIZE
            y = offset_y + i * CELL_SIZE

            if cell == WALL:
                screen.blit(images['wall'], (x, y))
            elif cell == FLOOR:
                screen.blit(images['floor'], (x, y))
            elif cell in BOX:
                screen.blit(images['box'], (x, y))
            elif cell == BOX_ON_GOAL:
                screen.blit(images['box_on_goal'], (x, y))
            elif cell in [PLAYER, PLAYER_ON_GOAL]:
                screen.blit(images['player'], (x, y))
            elif cell == GOAL:
                screen.blit(images['goal'], (x, y))
            else:
                screen.blit(images['other'], (x, y))
    update_screen()

def draw_init_screen():
    """Vẽ màn hình ban đầu chạy chương trình"""
    # Vẽ backgroud
    screen.fill(BLACK)

    # Vẽ title
    title = font.render("SOKOBAN GAME", True, GRAY)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

    # Vẽ map hiện thị
    board = parse_level(level_number)
    draw_map(board)
    
    # Vẽ level
    draw_level_number()

    # Vẽ thông tin algorithm
    algorithm_text = font.render(f"Algorithm: {algorithm}", True, WHITE)
    screen.blit(algorithm_text, (WIDTH // 2 - algorithm_text.get_width() // 2, HEIGHT - 80))
    
    # Hướng dẫn
    help_text = small_font.render("LEFT/RIGHT: Change Level | ENTER: Start | R: Reset | Q: Quit | P: Play", True, WHITE)
    screen.blit(help_text, (WIDTH // 2 - help_text.get_width() // 2, HEIGHT - 40))
    update_screen()

def draw_loading_screen():
    """Vẽ màn hình loading"""
    loading_text = font.render("LOADING...", True, (255, 255, 0))
    screen.blit(loading_text, (WIDTH // 2 - loading_text.get_width() // 2, HEIGHT // 2))
    
    solving_text = small_font.render("Solving with IDA* algorithm...", True, (200, 200, 200))
    screen.blit(solving_text, (WIDTH // 2 - solving_text.get_width() // 2, HEIGHT // 2 + 40))
    update_screen()

def draw_level_number():
    level_text = font.render(f"Level {level_number + 1} / {len(LEVELS)}", True, WHITE)
    text_x = (WIDTH - level_text.get_width()) // 2
    text_y = HEIGHT - 120
    text_width = level_text.get_width()
    text_height = level_text.get_height()
    rect = (text_x, text_y, text_width, text_height)
    # Xóa thông tin level cũ
    pygame.draw.rect(screen, BLACK, rect)
    # Vẽ thông tin level mới
    screen.blit(level_text, rect)
    update_screen()

def draw_text(content, y, color):
    text = font.render(content, True, color)
    text_x = (WIDTH - text.get_width()) // 2
    text_y = y
    text_width = text.get_width()
    text_height = text.get_height()
    rect = (text_x, text_y, text_width, text_height)
    # Xóa thông tin level cũ
    pygame.draw.rect(screen, BLACK, rect)
    # Vẽ thông tin level mới
    screen.blit(text, rect)
    update_screen()

def draw_player_win(step_count):
    draw_text(f"Player is winner....", HEIGHT - 200, WHITE)
    draw_text(f"STEP COUNT: {step_count}", HEIGHT - 180, WHITE)

def draw_solution(solution):
    step_count = len(solution) - 1
    step_count_text = font.render(f"STEP COUNT: {step_count}", True, WHITE)
    text_x = (WIDTH - step_count_text.get_width()) // 2
    text_y = 70
    text_width = step_count_text.get_width()
    text_height = step_count_text.get_height()
    rect = (text_x, text_y, text_width, text_height)
    # Vẽ thông tin level mới
    screen.blit(step_count_text, rect)
    update_screen()
    for board in solution:
        draw_map(board)
        wait_time()
    # Xóa thông tin STEP cũ
    pygame.draw.rect(screen, BLACK, rect)

def update_level_number(new_level_number):
    global level_number
    level_number = new_level_number
    draw_level_number()
    draw_map(parse_level(level_number))

def main():

    global level_number, algorithm
    running = True
    draw_init_screen()
    print("draw_init_screen") 

    while running:
        # Xử lý sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    if level_number < len(LEVELS) - 1:
                        update_level_number(level_number + 1)
                elif event.key == pygame.K_LEFT:
                    if level_number > 0:
                        update_level_number(level_number - 1)
                elif event.key == pygame.K_r: # R
                    level_number = 0
                    draw_init_screen()
                elif event.key == pygame.K_q: # q
                    running = False
                elif event.key == pygame.K_p: # P
                    print("PLAYER>>>>>>>>")
                    pygame.event.clear()
                    draw_text("Can You Win???", 70, WHITE)
                    board = parse_level(level_number)
                    game = SokobanGame(board)
                    playing = True
                    while playing:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                            elif event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_RIGHT:
                                    game.move('right')
                                elif event.key == pygame.K_LEFT:
                                    game.move('left')
                                elif event.key == pygame.K_UP:
                                    game.move('up')
                                elif event.key == pygame.K_DOWN:
                                    game.move('down')
                                elif event.key == pygame.K_e:
                                    playing = False
                                draw_map(game.board)
                            if game.check_win():
                                draw_player_win(game.step_count)
                                pygame.event.clear()
                    draw_init_screen()
                        
                elif event.key == pygame.K_RETURN: # Enter
                    draw_loading_screen()

                    board = parse_level(level_number)
                    solver = IDAStarSolver(board)
                    solver.solve()
                    if solver.end_node == None:
                        print("No Solution")
                        continue
                    
                    solution = solver.get_solution()
                    draw_solution(solution)
                    pygame.event.clear()
            
            update_screen()  

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()