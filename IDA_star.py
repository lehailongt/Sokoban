from collections import deque
import time

from constants import *
from node import Node


class IDAStarSolver:
    def __init__(self, board):
        self.board = [row[:] for row in board]
        self.rows = len(self.board)
        self.cols = len(self.board[0]) if self.rows else 0
        self.visited = {}
        self.end_node = None
        self.time_up = 0
        # Tính toán dead_squares và khoảng cách thực tế đến từng đích
        self.dead_squares, self.dist_to_goal = self._precompute_map_data()
        # Khởi tạo Node bắt đầu
        self.start_node = Node(self.board, 0, dead_squares=self.dead_squares, dist_to_goal=self.dist_to_goal)

    def _in_bounds(self, x, y):
        return 0 <= x < self.rows and 0 <= y < self.cols

    def _reachable_positions(self, board, start_pos):
        # Flood-fill / BFS để tính tất cả vị trí mà người chơi có thể đi tới
        # mà không cần đẩy thùng. Dùng để sinh các push hợp lệ (push-based).
        queue = deque([start_pos])
        reachable = {start_pos}

        while queue:
            x, y = queue.popleft()

            for dx, dy in DIRECTIONS.values():
                nx, ny = x + dx, y + dy
                if not self._in_bounds(nx, ny):
                    continue
                if (nx, ny) in reachable:
                    continue
                if board[nx][ny] in [WALL, BOX, BOX_ON_GOAL]:
                    continue

                reachable.add((nx, ny))
                queue.append((nx, ny))

        return reachable

    def _precompute_map_data(self):
        """
        Tính toán các ô chết (dead squares) và khoảng cách thực tế đến từng đích.
        Dùng BFS loang ngược từ các ô đích.
        """
        goals = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] in [GOAL, BOX_ON_GOAL, PLAYER_ON_GOAL]:
                    goals.append((r, c))

        # dist_to_goal[goal][pos] = khoảng cách ngắn nhất để đẩy thùng từ pos đến goal
        dist_to_goal = {g: {g: 0} for g in goals}
        # alive_squares: Tập hợp các ô mà thùng đứng đó có thể đẩy về ĐÍCH NÀO ĐÓ
        alive_squares = set()
        
        for g in goals:
            alive_squares.add(g)
            queue = deque([g])
            
            while queue:
                bx, by = queue.popleft()
                curr_dist = dist_to_goal[g][(bx, by)]

                for dx, dy in DIRECTIONS.values():
                    target_box_pos = (bx + dx, by + dy)
                    player_pos = (bx + 2 * dx, by + 2 * dy)

                    if self._in_bounds(target_box_pos[0], target_box_pos[1]) and \
                       self._in_bounds(player_pos[0], player_pos[1]):
                        
                        if self.board[target_box_pos[0]][target_box_pos[1]] != WALL and \
                           self.board[player_pos[0]][player_pos[1]] != WALL:
                            
                            if target_box_pos not in dist_to_goal[g]:
                                dist_to_goal[g][target_box_pos] = curr_dist + 1
                                alive_squares.add(target_box_pos)
                                queue.append(target_box_pos)

        # Những ô không phải tường mà không thể kéo thùng từ đích tới được => Ô chết
        dead_squares = set()
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] != WALL and (r, c) not in alive_squares:
                    dead_squares.add((r, c))
        
        return dead_squares, dist_to_goal

    def _find_walk_path(self, board, start_pos, target_pos):
        """Sửa lỗi tốc biến: Tìm đường đi bộ (BFS) ngắn nhất từ start_pos đến target_pos mà không đẩy thùng"""
        if start_pos == target_pos:
            return []

        queue = deque([(start_pos, [])])
        visited = {start_pos}

        while queue:
            (x, y), path = queue.popleft()

            for dx, dy in DIRECTIONS.values():
                nx, ny = x + dx, y + dy
                if not self._in_bounds(nx, ny):
                    continue
                if (nx, ny) in visited:
                    continue
                if board[nx][ny] in [WALL, BOX, BOX_ON_GOAL]:
                    continue

                new_path = path + [(nx, ny)]
                if (nx, ny) == target_pos:
                    return new_path

                visited.add((nx, ny))
                queue.append(((nx, ny), new_path))
        return []

    def _generate_children(self, node):
        """
        Sinh các nút con bằng cách đi thử 4 hướng (Lên, Xuống, Trái, Phải).
        Mỗi bước đi (kể cả đi bộ hay đẩy thùng) đều được tính là 1 đơn vị chi phí (g + 1).
        """
        children = []
        px, py = node.player_pos

        for dx, dy in DIRECTIONS.values():
            nx, ny = px + dx, py + dy

            # Kiểm tra xem ô tiếp theo có nằm trong bản đồ không
            if not self._in_bounds(nx, ny):
                continue
            
            cell = node.state[nx][ny]
            # Nếu gặp tường thì bỏ qua
            if cell == WALL:
                continue

            if cell in [BOX, BOX_ON_GOAL]:
                # TRƯỜNG HỢP GẶP THÙNG: Kiểm tra xem có đẩy được không
                tx, ty = nx + dx, ny + dy
                # Nếu ô phía sau thùng là tường hoặc một cái thùng khác thì không đẩy được
                if not self._in_bounds(tx, ty) or node.state[tx][ty] in [WALL, BOX, BOX_ON_GOAL]:
                    continue
                
                # Tạo bản đồ mới sau khi đẩy thùng
                new_board = [row[:] for row in node.state]
                # Người rời vị trí cũ
                new_board[px][py] = GOAL if new_board[px][py] == PLAYER_ON_GOAL else FLOOR
                # Người đứng vào vị trí cũ của thùng
                new_board[nx][ny] = PLAYER_ON_GOAL if new_board[nx][ny] == BOX_ON_GOAL else PLAYER
                # Thùng văng sang ô mới
                new_board[tx][ty] = BOX_ON_GOAL if new_board[tx][ty] in [GOAL, PLAYER_ON_GOAL] else BOX
                
                # Tạo Node con với chi phí tăng thêm 1 bước
                child = Node(new_board, node.g + 1, parent=node, dead_squares=self.dead_squares, dist_to_goal=self.dist_to_goal)
                # Kiểm tra xem việc đẩy này có tạo ra deadlock không
                if child.is_deadlocked():
                    continue
                children.append(child)
            else:
                # TRƯỜNG HỢP Ô TRỐNG HOẶC ĐÍCH: Chỉ di chuyển người
                new_board = [row[:] for row in node.state]
                new_board[px][py] = GOAL if new_board[px][py] == PLAYER_ON_GOAL else FLOOR
                new_board[nx][ny] = PLAYER_ON_GOAL if new_board[nx][ny] == GOAL else PLAYER
                
                # Tạo Node con với chi phí tăng thêm 1 bước (đi bộ)
                child = Node(new_board, node.g + 1, parent=node, dead_squares=self.dead_squares, dist_to_goal=self.dist_to_goal)
                children.append(child)

        return children

    def _search(self, node, threshold, pruned_values, path_keys):
        # Nếu node.f > threshold thì không mở rộng nút đó; ghi lại f của nó
        # để dùng cho ngưỡng tiếp theo (lấy min của các giá trị bị cắt).
        # Đây là ý tưởng cốt lõi của IDA*: tăng dần theo giới hạn trên f = g + h.
        if node.f > threshold:
            pruned_values.append(node.f)
            return None

        if node.is_goal_node():
            return node

        best_g = self.visited.get(node.node_key)
        if best_g is not None and best_g <= node.g:
            return None

        self.visited[node.node_key] = node.g

        for child in self._generate_children(node):
            if child.node_key in path_keys:
                continue

            path_keys.add(child.node_key)
            found = self._search(child, threshold, pruned_values, path_keys)
            path_keys.remove(child.node_key)

            if found is not None:
                return found

        return None

    def solve(self):
        """Giải bài toán bằng IDA* push-based."""
        start_time = time.time()
        threshold = self.start_node.h

        if threshold == INF:
            self.end_node = None
            self.time_up = time.time() - start_time
            return

        # Lặp tăng dần trên ngưỡng `threshold` (giới hạn f). Sau mỗi lượt DFS,
        # nếu chưa tìm thấy lời giải thì đặt `threshold = min(pruned_values)` và lặp lại.
        while True:
            self.visited = {}
            pruned_values = []
            path_keys = {self.start_node.node_key}

            found = self._search(self.start_node, threshold, pruned_values, path_keys)
            if found is not None:
                self.end_node = found
                self.time_up = time.time() - start_time
                print(f"Thời gian chạy thuật toán IDA*: {self.time_up}")
                print(f"Số trạng thái đã duyệt {len(self.visited)}")
                return

            # Nếu không có node nào bị cắt (pruned) mà vẫn chưa tìm được lời giải
            # thì không còn nút nào để mở rộng ở ngưỡng cao hơn -> không có lời giải.
            if not pruned_values:
                self.end_node = None
                self.time_up = time.time() - start_time
                print("No Solution")
                return

            # Ngược lại, tăng ngưỡng lên giá trị nhỏ nhất trong các f bị cắt.
            threshold = min(pruned_values)
            print(f"Tăng ngưỡng lên: {threshold}")

    def get_solution(self):
        """
        Truy vết từ Node kết quả về Node bắt đầu để lấy danh sách các trạng thái bàn cờ.
        Vì mỗi bước đi bây giờ là 1 Node riêng biệt, ta chỉ cần thu thập state của từng Node.
        """
        if self.end_node is None:
            return []

        state_list = []
        node = self.end_node
        while node is not None:
            state_list.append(node.state)
            node = node.parent
        
        # Đảo ngược danh sách để có thứ tự từ đầu đến cuối
        state_list.reverse()
        return state_list
