from constants import *

class Node:
    def __init__(self, state, g):
        self.state = state
        self.rows = len(self.state)
        self.cols = len(self.state[0])
        self.boxes = self.find_boxes()
        self.goals = self.find_goals()
        self.player_pos = self.find_player()
        self.node_key = self.get_state_key()
        self.pre_node_key = None
        self.g = g
        self.h = self.heuristic()
        self.f = self.g + self.h
   
    # Nếu muốn chính xác hơn (bao gồm player)
    def get_state_key(self):
        """Tạo key duy nhất cho trạng thái"""
        return (tuple(sorted(self.boxes)), self.player_pos)
        # [(x1,y1), (x2,y2), ..., (playerx, playery)] -> ((x1,y1), (x2,y2), ..., (playerx, playery))
   
    def find_boxes(self):
        boxes = []
        for i in range(self.rows):
            for j in range(self.cols):
                if self.state[i][j] in [BOX, BOX_ON_GOAL]:
                    boxes.append((i, j))
        return boxes
    
    def find_goals(self):
        goals = []
        for i in range(self.rows):
            for j in range(self.cols):
                if self.state[i][j] in [GOAL, BOX_ON_GOAL, PLAYER_ON_GOAL]:
                    goals.append((i, j))
        return goals
    
    def find_player(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.state[i][j] in [PLAYER, PLAYER_ON_GOAL]:
                    return (i, j)
        return (0, 0)

    def heuristic(self):
        """Hàm heuristic: tổng khoảng cách Manhattan từ mỗi thùng đến đích gần nhất"""

        total_distance = 0
        for bx, by in self.boxes:
            min_dis = INF
            for gx, gy in self.goals:
                min_dis = min(min_dis, abs(bx - gx) + abs(by - gy))
            total_distance += min_dis
                
        return total_distance
        
    def is_goal_node(self):
        """Kiểm tra xem đã thắng chưa"""
        for i in range(self.rows):
            for j in range(self.cols):
                if self.state[i][j] == BOX:
                    return False
        return True
        
    def position_on_board(self, x, y):
        """Kiểm tra 1 tọa độ có nằm trong map trò chơi không"""
        if x > 1 and x < self.rows and y > 1 or y < self.cols:
            return True
        return False
    
    def next(self, direction):
        """Tìm trạng thái tiếp theo với hướng di chuyển"""
        px, py = self.find_player()
        dx, dy = DIRECTIONS[direction]
        nx, ny = px + dx, py + dy
        
        # Kiểm tra biên
        if not self.position_on_board(nx, ny):
            return None
        
        board = [row[:] for row in self.state]

        # Kiểm tra tường
        if board[nx][ny] == WALL:
            return None
        
        # Di chuyển đẩy thùng
        if board[nx][ny] in [BOX, BOX_ON_GOAL]:
            nnx, nny = nx + dx, ny + dy
           
            # Thùng sát biên
            if not self.position_on_board(nnx, nny):
                return None
           
            # 2 thùng cạnh nhau
            if board[nnx][nny] in [WALL, BOX, BOX_ON_GOAL]:
                return None
            
            # Đẩy thùng
            # Xóa vị trí cũ của người
            if board[px][py] == PLAYER_ON_GOAL:
                board[px][py] = GOAL
            else:
                board[px][py] = FLOOR
            
            # Di chuyển thùng
            if board[nnx][nny] == GOAL:
                board[nnx][nny] = BOX_ON_GOAL
            else:
                board[nnx][nny] = BOX
            
            # Di chuyển người
            if board[nx][ny] == BOX_ON_GOAL:
                board[nx][ny] = PLAYER_ON_GOAL
            else:
                board[nx][ny] = PLAYER

        # Di chuyển bình thường
        else:
            if board[px][py] == PLAYER_ON_GOAL:
                board[px][py] = GOAL
            else:
                board[px][py] = FLOOR
            
            if board[nx][ny] == GOAL:
                board[nx][ny] = PLAYER_ON_GOAL
            else:
                board[nx][ny] = PLAYER
            
        node = Node(board, self.g + 1)
        node.pre_node_key = self.node_key
        return node
        
