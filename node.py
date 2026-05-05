from constants import *

class Node:
    def __init__(self, state, g, parent=None, dead_squares=None, dist_to_goal=None):
        self.state = state
        self.rows = len(self.state)
        self.cols = len(self.state[0])
        self.boxes = self.find_boxes()
        self.goals = self.find_goals()
        self.player_pos = self.find_player()
        self.parent = parent
        self.dead_squares = dead_squares if dead_squares is not None else set()
        self.dist_to_goal = dist_to_goal if dist_to_goal is not None else {}
        self.node_key = self.get_state_key()
        self.g = g
        self.h = self.heuristic()
        self.f = self.g + self.h if self.h != INF else INF
   
    def get_state_key(self):
        """Tạo key duy nhất cho trạng thái. Dùng vị trí người chơi chuẩn hóa."""
        from collections import deque
        reachable = set()
        queue = deque([self.player_pos])
        reachable.add(self.player_pos)
        
        while queue:
            x, y = queue.popleft()
            for dx, dy in DIRECTIONS.values():
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.rows and 0 <= ny < self.cols:
                    if (nx, ny) not in reachable and self.state[nx][ny] not in [WALL, BOX, BOX_ON_GOAL]:
                        reachable.add((nx, ny))
                        queue.append((nx, ny))
                        
        normalized_player_pos = min(reachable)
        return (tuple(sorted(self.boxes)), normalized_player_pos)
   
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
        """Heuristic thực tế: Tổng khoảng cách ngắn nhất (né tường) từ mỗi thùng tới các đích."""
        if not self.boxes: return 0
        total = 0
        for box in self.boxes:
            min_d = INF
            for g in self.goals:
                d = self.dist_to_goal.get(g, {}).get(box, INF)
                if d < min_d: min_d = d
            
            if min_d == INF: return INF
            total += min_d
        return total
        
    def is_goal_node(self):
        """Kiểm tra xem đã thắng chưa"""
        for i in range(self.rows):
            for j in range(self.cols):
                if self.state[i][j] == BOX:
                    return False
        return True
    
    def is_deadlocked(self):
        """Kiểm tra ô chết (Dead squares)"""
        goal_set = set(self.goals)
        for box in self.boxes:
            if box not in goal_set and box in self.dead_squares:
                return True
        return False
