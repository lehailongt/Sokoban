from constants import *

class Node:
    def __init__(self, state, g, parent=None, dead_squares=None, dist_to_goal=None):
        self.state = state
        self.rows = len(self.state)
        self.cols = len(self.state[0])
        self.boxes = self.find_boxes()
        self.goals = self.find_goals()
        self.player_pos = self.find_player()
        self.node_key = self.get_state_key()
        self.parent = parent
        self.dead_squares = dead_squares if dead_squares is not None else set()
        self.dist_to_goal = dist_to_goal if dist_to_goal is not None else {}
        self.g = g
        self.h = self.heuristic()
        self.f = self.g + self.h if self.h != INF else INF
   
    # Nếu muốn chính xác hơn (bao gồm player) => Có thể trùng
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

    # Tối ưu phức tạp
    def heuristic(self):
        """Heuristic thực tế: Tổng khoảng cách ngắn nhất (né tường) từ mỗi thùng tới các đích."""
        if not self.boxes: 
            return 0
        total = 0
        for box in self.boxes:
            min_d = INF
            for g in self.goals:
                d = self.dist_to_goal.get(g, {}).get(box, INF)
                if d < min_d: 
                    min_d = d
            
            if min_d == INF: 
                return INF
            total += min_d
        return total
        
    def is_goal_node(self):
        """Kiểm tra xem đã thắng chưa"""
        for i in range(self.rows):
            for j in range(self.cols):
                if self.state[i][j] == BOX:
                    return False
        return True
        
    # def position_on_board(self, x, y):
    #     """Kiểm tra 1 tọa độ có nằm trong map trò chơi không"""
    #     if x >= 0 and x < self.rows and y >= 0 and y < self.cols:
    #         return True
    #     return False
    
    def is_deadlocked(self):
        """Kiểm tra ô chết (Dead squares)"""
        goal_set = set(self.goals)
        for box in self.boxes:
            if box not in goal_set and box in self.dead_squares:
                return True
        return False

    def next(self, direction):
        """Tìm trạng thái tiếp theo với hướng di chuyển 1 bước"""
        px, py = self.player_pos
        dx, dy = DIRECTIONS[direction]
        nx, ny = px + dx, py + dy
        
        if not (0 <= nx < self.rows and 0 <= ny < self.cols):
            return None
        
        if self.state[nx][ny] == WALL:
            return None
        
        board = [row[:] for row in self.state]

        if board[nx][ny] in [BOX, BOX_ON_GOAL]:
            nnx, nny = nx + dx, ny + dy
            if not (0 <= nnx < self.rows and 0 <= nny < self.cols) or board[nnx][nny] in [WALL, BOX, BOX_ON_GOAL]:
                return None
            
            board[px][py] = GOAL if board[px][py] == PLAYER_ON_GOAL else FLOOR
            board[nx][ny] = PLAYER_ON_GOAL if board[nx][ny] == BOX_ON_GOAL else PLAYER
            board[nnx][nny] = BOX_ON_GOAL if board[nnx][nny] in [GOAL, PLAYER_ON_GOAL] else BOX
            
            child = Node(board, self.g + 1, parent=self, dead_squares=self.dead_squares, dist_to_goal=self.dist_to_goal)
            if child.is_deadlocked():
                return None
            return child
        else:
            board[px][py] = GOAL if board[px][py] == PLAYER_ON_GOAL else FLOOR
            board[nx][ny] = PLAYER_ON_GOAL if board[nx][ny] == GOAL else PLAYER
            return Node(board, self.g + 1, parent=self, dead_squares=self.dead_squares, dist_to_goal=self.dist_to_goal)
        
