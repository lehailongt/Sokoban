from constants import *

class SokobanGame:
    def __init__(self, board):
        self.board = board
        self.rows = len(self.board)
        self.cols = len(self.board[0])
        self.goals = self.find_goals()
        self.player_pos = self.find_player()
        self.step_count = 0

    def find_player(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] in [PLAYER, PLAYER_ON_GOAL]:
                    return (i, j)
        return (0, 0)
    
    def find_boxes(self):
        boxes = []
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] in [BOX, BOX_ON_GOAL]:
                    boxes.append((i, j))
        return boxes
    
    def find_goals(self):
        goals = []
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] in [GOAL, BOX_ON_GOAL, PLAYER_ON_GOAL]:
                    goals.append((i, j))
        return goals

    def check_win(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] == BOX:
                    return False
        return True
    
    def position_on_board(self, x, y):
        """Kiểm tra 1 tọa độ có nằm trong map trò chơi không"""
        if x > 1 and x < self.rows and y > 1 or y < self.cols:
            return True
        return False
    
    def move(self, direction):
        px, py = self.player_pos
        dx, dy = DIRECTIONS[direction]
        nx, ny = px + dx, py + dy
        
        # Kiểm tra biên
        if not self.position_on_board(nx, ny):
            return False
        
        # Kiểm tra tường
        if self.board[nx][ny] == WALL:
            return False
        
        # Kiểm tra thùng
        if self.board[nx][ny] in [BOX, BOX_ON_GOAL]:
            nnx, nny = nx + dx, ny + dy


            # 2 thùng cạnh nhau hoặc sát tường
            if self.board[nnx][nny] in [WALL, BOX, BOX_ON_GOAL]:
                return False
            
            # Đẩy thùng
            # Xóa vị trí cũ của người
            if self.board[px][py] == PLAYER_ON_GOAL:
                self.board[px][py] = GOAL
            else:
                self.board[px][py] = FLOOR
            
            # Di chuyển thùng
            if self.board[nnx][nny] == GOAL:
                self.board[nnx][nny] = BOX_ON_GOAL
            else:
                self.board[nnx][nny] = BOX
            
            # Di chuyển người
            if self.board[nx][ny] == BOX_ON_GOAL:
                self.board[nx][ny] = PLAYER_ON_GOAL
            else:
                self.board[nx][ny] = PLAYER
            
        # Di chuyển bình thường
        else:
            if self.board[px][py] == PLAYER_ON_GOAL:
                self.board[px][py] = GOAL
            else:
                self.board[px][py] = FLOOR
            
            if self.board[nx][ny] == GOAL:
                self.board[nx][ny] = PLAYER_ON_GOAL
            else:
                self.board[nx][ny] = PLAYER
            
        self.player_pos = (nx, ny)
        self.step_count += 1
        return True
    