from collections import deque
from constants import *
from node import Node
import time

class IDAStarSolver:
    def __init__(self, board):
        self.board = [row[:] for row in board]
        self.rows = len(self.board)
        self.cols = len(self.board[0]) if self.rows else 0
        # Tiền xử lý bản đồ để tìm ô chết và bảng khoảng cách thực tế
        self.dead_squares, self.dist_to_goal = self._precompute_map_data()
        self.start_node = Node(self.board, 0, dead_squares=self.dead_squares, dist_to_goal=self.dist_to_goal)
        self.end_node = None
        self.time_up = 0
        self.visited = {}

    def _in_bounds(self, x, y):
        return 0 <= x < self.rows and 0 <= y < self.cols

    def _precompute_map_data(self):
        """Tính toán ô chết và khoảng cách thực tế (loang ngược từ đích)."""
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
                    tx, ty = bx + dx, by + dy # Vị trí thùng
                    px, py = bx + 2*dx, by + 2*dy # Vị trí người để kéo thùng ngược lại
                    if self._in_bounds(tx, ty) and self._in_bounds(px, py):
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

    def _reachable_positions(self, board, start_pos):
        """Flood-fill tìm tất cả các ô người chơi có thể đi bộ tới."""
        queue = deque([start_pos])
        reachable = {start_pos}
        while queue:
            x, y = queue.popleft()
            for dx, dy in DIRECTIONS.values():
                nx, ny = x + dx, y + dy
                if self._in_bounds(nx, ny) and (nx, ny) not in reachable and board[nx][ny] not in [WALL, BOX, BOX_ON_GOAL]:
                    reachable.add((nx, ny))
                    queue.append((nx, ny))
        return reachable

    def _find_walk_path(self, board, start_pos, target_pos):
        """BFS tìm đường đi bộ giữa 2 vị trí."""
        if start_pos == target_pos: return []
        queue = deque([(start_pos, [])])
        visited = {start_pos}
        while queue:
            (x, y), path = queue.popleft()
            for dx, dy in DIRECTIONS.values():
                nx, ny = x + dx, y + dy
                if self._in_bounds(nx, ny) and (nx, ny) not in visited and board[nx][ny] not in [WALL, BOX, BOX_ON_GOAL]:
                    new_path = path + [(nx, ny)]
                    if (nx, ny) == target_pos: return new_path
                    visited.add((nx, ny))
                    queue.append(((nx, ny), new_path))
        return []

    def _generate_children(self, node):
        """Sinh con theo kiểu Macro-step: Mỗi con là một lần đẩy thùng thành công."""
        reachable = self._reachable_positions(node.state, node.player_pos)
        children = []
        px, py = node.player_pos

        for bx, by in node.boxes:
            for dx, dy in DIRECTIONS.values():
                player_spot = (bx - dx, by - dy)
                target_spot = (bx + dx, by + dy)

                if player_spot in reachable and self._in_bounds(target_spot[0], target_spot[1]) and \
                   node.state[target_spot[0]][target_spot[1]] not in [WALL, BOX, BOX_ON_GOAL]:
                    
                    new_board = [row[:] for row in node.state]
                    new_board[px][py] = GOAL if new_board[px][py] == PLAYER_ON_GOAL else FLOOR
                    new_board[bx][by] = PLAYER_ON_GOAL if new_board[bx][by] == BOX_ON_GOAL else PLAYER
                    new_board[target_spot[0]][target_spot[1]] = BOX_ON_GOAL if node.state[target_spot[0]][target_spot[1]] == GOAL else BOX
                    
                    # Chi phí g + 1 (tối ưu số lần đẩy)
                    child = Node(new_board, node.g + 1, parent=node, dead_squares=self.dead_squares, dist_to_goal=self.dist_to_goal)
                    if not child.is_deadlocked():
                        children.append(child)
        return children

    def _search(self, node, threshold, pruned_values, path_keys):
        if node.f > threshold:
            pruned_values.append(node.f)
            return None
        
        if node.is_goal_node():
            return node

        best_g = self.visited.get(node.node_key, INF)
        if best_g <= node.g: return None
        self.visited[node.node_key] = node.g

        for child in self._generate_children(node):
            if child.node_key not in path_keys:
                path_keys.add(child.node_key)
                found = self._search(child, threshold, pruned_values, path_keys)
                path_keys.remove(child.node_key)
                if found: return found
        return None

    def solve(self):
        """Giải bài toán bằng IDA* tối ưu số lần đẩy."""
        start_time = time.time()
        threshold = self.start_node.h
        self.visited = {} # Khởi tạo bộ nhớ 1 lần duy nhất
        
        while True:
            pruned_values = []
            path_keys = {self.start_node.node_key}
            
            found = self._search(self.start_node, threshold, pruned_values, path_keys)
            
            if found:
                self.end_node = found
                self.time_up = time.time() - start_time
                print(f"Thời gian chạy (Push-optimal): {self.time_up}")
                print(f"Số trạng thái: {len(self.visited)}")
                return
            
            if not pruned_values: break
            threshold = min(pruned_values)
            print(f"Tăng ngưỡng lên: {threshold}")

    def get_solution(self):
        """Trả về danh sách board bao gồm cả các bước đi bộ bù vào giữa các lần đẩy."""
        if not self.end_node: return []
        
        nodes = []
        curr = self.end_node
        while curr:
            nodes.append(curr)
            curr = curr.parent
        nodes.reverse()

        state_list = [nodes[0].state]

        for i in range(len(nodes) - 1):
            p, c = nodes[i], nodes[i+1]
            
            # Tìm thùng bị đẩy
            p_boxes = set(p.find_boxes()); c_boxes = set(c.find_boxes())
            box_from = list(p_boxes - c_boxes)[0]
            box_to = list(c_boxes - p_boxes)[0]
            dx, dy = box_to[0] - box_from[0], box_to[1] - box_from[1]
            player_goal_spot = (box_from[0] - dx, box_from[1] - dy)

            # Sinh các bước đi bộ
            walk_path = self._find_walk_path(p.state, p.player_pos, player_goal_spot)
            curr_px, curr_py = p.player_pos
            for wx, wy in walk_path:
                new_board = [row[:] for row in state_list[-1]]
                new_board[curr_px][curr_py] = GOAL if new_board[curr_px][curr_py] == PLAYER_ON_GOAL else FLOOR
                new_board[wx][wy] = PLAYER_ON_GOAL if new_board[wx][wy] == GOAL else PLAYER
                state_list.append(new_board)
                curr_px, curr_py = wx, wy
            
            # Thêm state đẩy thùng
            state_list.append(c.state)

        return state_list
