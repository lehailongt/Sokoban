from collections import deque
from constants import *
from node import Node
import time

class IDAStarSolver:
    def __init__(self, board):
        self.board = [row[:] for row in board]
        self.rows = len(self.board)
        self.cols = len(self.board[0]) if self.rows else 0
        # Tiền xử lý bản đồ để tìm ô chết và khoảng cách thực tế
        self.dead_squares, self.dist_to_goal = self._precompute_map_data()
        # Khởi tạo Node bắt đầu
        self.start_node = Node(self.board, 0, dead_squares=self.dead_squares, dist_to_goal=self.dist_to_goal)
        self.end_node = None
        self.time_up = 0
        self.visited = {}

    def _precompute_map_data(self):
        """Tính toán ô chết và khoảng cách thực tế (giống code mẫu)"""
        goals = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] in [GOAL, BOX_ON_GOAL, PLAYER_ON_GOAL]:
                    goals.append((r, c))

        dist_to_goal = {g: {g: 0} for g in goals}
        alive_squares = set()
        
        for g in goals:
            alive_squares.add(g)
            queue = deque([g])
            while queue:
                bx, by = queue.popleft()
                d = dist_to_goal[g][(bx, by)]
                for dx, dy in DIRECTIONS.values():
                    tx, ty = bx + dx, by + dy # vị trí thùng mới nếu kéo ngược
                    px, py = bx + 2*dx, by + 2*dy # vị trí người cần đứng để kéo ngược
                    if 0 <= tx < self.rows and 0 <= ty < self.cols and \
                       0 <= px < self.rows and 0 <= py < self.cols:
                        if self.board[tx][ty] != WALL and self.board[px][py] != WALL:
                            if (tx, ty) not in dist_to_goal[g]:
                                dist_to_goal[g][(tx, ty)] = d + 1
                                alive_squares.add((tx, ty))
                                queue.append((tx, ty))

        dead_squares = set()
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] != WALL and (r, c) not in alive_squares:
                    dead_squares.add((r, c))
        return dead_squares, dist_to_goal

    def _search(self, node, threshold, pruned_values, path_keys):
        """Hàm tìm kiếm đệ quy cho IDA*"""
        if node.f > threshold:
            pruned_values.append(node.f)
            return None
        
        if node.is_goal_node():
            return node

        # Pruning: nếu đã thăm trạng thái này với chi phí g thấp hơn hoặc bằng
        best_g = self.visited.get(node.node_key, INF)
        if best_g <= node.g:
            return None
        self.visited[node.node_key] = node.g

        for direction in DIRECTIONS:
            child = node.next(direction)
            if child and child.node_key not in path_keys:
                path_keys.add(child.node_key)
                found = self._search(child, threshold, pruned_values, path_keys)
                path_keys.remove(child.node_key)
                if found: return found
        return None

    def solve(self):
        """Giải bài toán bằng thuật toán IDA* chuẩn"""
        start_time = time.time()
        threshold = self.start_node.h
        
        while True:
            self.visited = {}
            pruned_values = []
            path_keys = {self.start_node.node_key}
            
            # Tìm kiếm với ngưỡng hiện tại
            found = self._search(self.start_node, threshold, pruned_values, path_keys)
            
            if found:
                self.end_node = found
                self.time_up = time.time() - start_time
                print(f"Thời gian chạy thuật toán IDA*: {self.time_up}")
                print(f"Số trạng thái đã duyệt: {len(self.visited)}")
                return
            
            if not pruned_values: # Không còn đường nào để đi
                break
                
            # Cập nhật ngưỡng mới là giá trị f nhỏ nhất bị cắt
            threshold = min(pruned_values)
            print(f"Tăng ngưỡng lên: {threshold}")
            
            # Tránh lặp vô tận nếu có lỗi logic
            if threshold > 1000: 
                break

    def get_solution(self):
        """Truy vết đường đi qua thuộc tính parent của Node"""
        if not self.end_node: return []
        path = []
        curr = self.end_node
        while curr:
            path.append(curr.state)
            curr = curr.parent
        path.reverse()
        return path
