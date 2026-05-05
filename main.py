import sys, pygame, time
from constants import *
from IDA_star import IDAStarSolver
from sokoban_game import SokobanGame
from ultils import *

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
            elif cell == PLAYER:
                screen.blit(images['player'], (x, y))
            elif cell == PLAYER_ON_GOAL:
                screen.blit(images['player_on_goal'], (x, y))
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
    draw_text(f"Level {level_number + 1} / {len(LEVELS)}", HEIGHT - 120, WHITE, BLACK)

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

def draw_text(content, y, color_text, background):
    text = font.render(content, True, color_text)
    text_x = (WIDTH - text.get_width()) // 2
    text_y = y
    text_width = text.get_width()
    text_height = text.get_height()
    rect = (text_x, text_y, text_width, text_height)
    # Tạo màu background 
    pygame.draw.rect(screen, background, rect)
    # Vẽ thông tin nội dung hiện thị
    screen.blit(text, rect)
    update_screen()

def draw_player_win(step_count):
    draw_text(f"Player is winner....", HEIGHT - 200, WHITE, BLACK)
    draw_text(f"STEP COUNT: {step_count}", HEIGHT - 170, WHITE, BLACK)

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

def update_level_number(new_level_number):
    global level_number
    level_number = new_level_number
    draw_text(f"Level {level_number + 1} / {len(LEVELS)}", HEIGHT - 120, WHITE, BLACK)
    draw_map(parse_level(level_number))

def exit_game():
    pygame.quit()
    sys.exit()

def main():

    global level_number, algorithm
    running = True
    draw_init_screen()
    print("draw_init_screen") 

    while running:
        # Xử lý sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_game()
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
                    exit_game()
                elif event.key == pygame.K_p: # P
                    pygame.event.clear()

                    draw_text("Can You Win???", 70, WHITE, BLACK)
                    draw_text(f"Press E to exit game", 100, WHITE, BLACK)

                    board = parse_level(level_number)
                    draw_map(board)
                    game = SokobanGame(board)
                    playing = True
                    while playing:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                exit_game()
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
                        # Hiển thị thông báo lỗi lên màn hình game
                        draw_text("NO SOLUTION FOUND!", HEIGHT // 2 + 80, (255, 0, 0), BLACK)
                        update_screen()
                        time.sleep(2) # Giữ thông báo trong 2 giây
                        draw_init_screen()
                        continue
                    
                    solution = solver.get_solution()
                    draw_solution(solution)
                    pygame.event.clear()
                    # Đợi 1 phím bất kì được nhấn
                    while not any(pygame.key.get_pressed()): pygame.event.pump()
                    draw_init_screen()

        update_screen()
         
    exit_game()

if __name__ == "__main__":
    main()