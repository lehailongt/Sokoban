from constants import *
import pygame, sys


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sokoban - Game xếp thùng")


def load_image(name, color):
    path = os.path.join("images", name)
    if os.path.exists(path):
        return pygame.transform.scale(pygame.image.load(path), (TILE, TILE))
    surf = pygame.Surface((TILE, TILE))
    surf.fill(color)
    return surf

# Load hình ảnh
def load_image(filename, default_color):
    try:
        img = pygame.image.load(f"images/{filename}").convert_alpha()
        return pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    except:
        # Nếu không có ảnh, tạo surface màu thay thế
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill(default_color)
        return surf

# Load tất cả ảnh
images = {
    'wall': load_image("wall.png", COLORS['wall']),
    'player': load_image("player.png", COLORS['player']),
    'box': load_image("box.png", COLORS['box']),
    'goal': load_image("goal.png", COLORS['goal']),
    'floor': load_image("floor.png", COLORS['floor']),
    'complete': load_image("complete.png", COLORS['complete']),
}

# Level mẫu (0: trống, 1: tường, 2: người, 3: thùng, 4: đích, 5: thùng+đích)
levels = [
    [
        "111111",
        "100001",
        "103021",
        "104001",
        "100001",
        "111111"
    ],
    [
        "111111111",
        "100000001",
        "100004001",
        "102003001",
        "100000001",
        "111111111"
    ],
    [
        "1111111111",
        "1000000001",
        "1000040001",
        "1000030001",
        "1000020001",
        "1000000001",
        "1111111111"
    ]
]

class Sokoban:
    def __init__(self, level_data):
        self.level = []
        self.rows = len(level_data)
        self.cols = len(level_data[0])
        self.player_pos = None
        self.boxes = []
        self.goals = []
        self.walls = []
        self.completed = []  # các thùng đã hoàn thành

        for r, row in enumerate(level_data):
            line = []
            for c, ch in enumerate(row):
                if ch == '1':  # tường
                    self.walls.append((r, c))
                elif ch == '2':  # người
                    self.player_pos = (r, c)
                elif ch == '3':  # thùng
                    self.boxes.append((r, c))
                elif ch == '4':  # đích
                    self.goals.append((r, c))
                elif ch == '5':  # thùng trên đích
                    self.boxes.append((r, c))
                    self.goals.append((r, c))
                    self.completed.append((r, c))

    def draw(self, screen):
        screen.fill((0, 0, 0))
        for r in range(self.rows):
            for c in range(self.cols):
                x, y = c * TILE_SIZE, r * TILE_SIZE
                # Vẽ nền
                screen.blit(images['floor'], (x, y))

                # Vẽ đích
                if (r, c) in self.goals:
                    screen.blit(images['goal'], (x, y))

                # Vẽ tường
                if (r, c) in self.walls:
                    screen.blit(images['wall'], (x, y))

                # Vẽ thùng (ưu tiên hơn đích)
                if (r, c) in self.boxes:
                    if (r, c) in self.goals:
                        screen.blit(images['complete'], (x, y))
                    else:
                        screen.blit(images['box'], (x, y))

                # Vẽ người (cuối cùng)
                if (r, c) == self.player_pos:
                    screen.blit(images['player'], (x, y))

        # Thông báo chiến thắng
        if self.check_win():
            font = pygame.font.Font(None, 74)
            text = font.render("YOU WIN!", True, (255, 255, 0))
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 50))

    def move(self, dx, dy):
        px, py = self.player_pos
        nx, ny = px + dx, py + dy

        # Kiểm tra tường
        if (nx, ny) in self.walls:
            return False

        # Kiểm tra thùng
        if (nx, ny) in self.boxes:
            nnx, nny = nx + dx, ny + dy
            # Không thể đẩy vào tường hoặc thùng khác
            if (nnx, nny) in self.walls or (nnx, nny) in self.boxes:
                return False

            # Đẩy thùng
            self.boxes.remove((nx, ny))
            self.boxes.append((nnx, nny))
            # Cập nhật vị trí người
            self.player_pos = (nx, ny)
            return True

        # Di chuyển bình thường
        self.player_pos = (nx, ny)
        return True

    def check_win(self):
        # Thắng khi tất cả các đích đều có thùng
        for goal in self.goals:
            if goal not in self.boxes:
                return False
        return True

def main():
    clock = pygame.time.Clock()
    current_level = 0
    game = Sokoban(levels[current_level])

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    game.move(-1, 0)
                elif event.key == pygame.K_DOWN:
                    game.move(1, 0)
                elif event.key == pygame.K_LEFT:
                    game.move(0, -1)
                elif event.key == pygame.K_RIGHT:
                    game.move(0, 1)
                elif event.key == pygame.K_r:  # Reset level
                    game = Sokoban(levels[current_level])
                elif event.key == pygame.K_n:  # Next level
                    if current_level + 1 < len(levels):
                        current_level += 1
                        game = Sokoban(levels[current_level])

                # Kiểm tra thắng để sang level tiếp theo
                if game.check_win():
                    if current_level + 1 < len(levels):
                        current_level += 1
                        game = Sokoban(levels[current_level])
                    else:
                        print("Chúc mừng! Bạn đã hoàn thành game!")

        game.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
