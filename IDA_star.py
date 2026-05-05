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
        # Tính toán trước danh sách các ô chết (deadlock) để dùng chung cho mọi Node
        self.dead_squares = self._precompute_deadlock()
        # Khởi tạo Node bắt đầu với danh sách ô chết
        self.start_node = Node(self.board, 0, dead_squares=self.dead_squares)

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

    def _precompute_deadlock(self):
        """
        Tính toán các ô chết (dead squares) bằng cách kéo thùng ngược từ các ô đích.
        Ý tưởng: Nếu một cái thùng ở vị trí A có thể được KÉO về vị trí B, 
        thì có nghĩa là nếu thùng ở B, ta có thể ĐẨY nó về A.
        Nếu loang từ tất cả các Đích, ô nào không thể kéo tới được thì đó là ô chết.
        """
        goals = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] in [GOAL, BOX_ON_GOAL, PLAYER_ON_GOAL]:
                    goals.append((r, c))

        # alive_squares: Tập hợp các ô mà thùng đứng đó vẫn có cơ hội về đích
        alive_squares = set()
        queue = deque()

        # Bắt đầu loang từ các ô đích
        for g in goals:
            alive_squares.add(g)
            queue.append(g)

        while queue:
            bx, by = queue.popleft()

            for dx, dy in DIRECTIONS.values():
                # Thử kéo ngược: 
                # bx, by là vị trí hiện tại của thùng
                # target_box_pos là vị trí thùng sẽ được kéo tới (bx + dx, by + dy)
                # player_pos là vị trí người chơi phải đứng để kéo (bx + 2*dx, by + 2*dy)
                
                target_box_pos = (bx + dx, by + dy)
                player_pos = (bx + 2 * dx, by + 2 * dy)

                # Kiểm tra xem vị trí mới của thùng và vị trí đứng của người có hợp lệ không
                if self._in_bounds(target_box_pos[0], target_box_pos[1]) and \
                   self._in_bounds(player_pos[0], player_pos[1]):
                    
                    # Cả ô thùng tới và ô người đứng đều không được là tường
                    if self.board[target_box_pos[0]][target_box_pos[1]] != WALL and \
                       self.board[player_pos[0]][player_pos[1]] != WALL:
                        
                        if target_box_pos not in alive_squares:
                            alive_squares.add(target_box_pos)
                            queue.append(target_box_pos)

        # Những ô không phải tường mà không thể kéo thùng từ đích tới được => Ô chết
        dead_squares = set()
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] != WALL and (r, c) not in alive_squares:
                    dead_squares.add((r, c))
        
        return dead_squares

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
        # Sinh các nút con bằng cách liệt kê các push hợp lệ.
        # Với mỗi thùng, xét 4 hướng: nếu người chơi có thể tới ô phía sau thùng
        # và ô đích trống thì tạo trạng thái mới sau khi đẩy thùng.
        # Cách này đảm bảo `g` được đo theo số lần đẩy (push).
        reachable = self._reachable_positions(node.state, node.player_pos)
        children = []
        seen_keys = set()
        px, py = node.player_pos

        for bx, by in node.boxes:
            for dx, dy in DIRECTIONS.values():
                player_spot = (bx - dx, by - dy)
                target_spot = (bx + dx, by + dy)

                if player_spot not in reachable:
                    continue
                if not self._in_bounds(target_spot[0], target_spot[1]):
                    continue

                target_cell = node.state[target_spot[0]][target_spot[1]]
                if target_cell in [WALL, BOX, BOX_ON_GOAL]:
                    continue

                board = [row[:] for row in node.state]

                board[px][py] = GOAL if board[px][py] == PLAYER_ON_GOAL else FLOOR
                board[bx][by] = (
                    PLAYER_ON_GOAL if board[bx][by] == BOX_ON_GOAL else PLAYER
                )
                board[target_spot[0]][target_spot[1]] = (
                    BOX_ON_GOAL if target_cell in [GOAL, PLAYER_ON_GOAL] else BOX
                )

                child = Node(board, node.g + 1, parent=node, dead_squares=self.dead_squares)
                if child.is_deadlocked():
                    continue
                if child.node_key in seen_keys:
                    continue

                seen_keys.add(child.node_key)
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
        """Trả về list board từ start đến end, bao gồm cả các bước đi bộ."""
        if self.end_node is None:
            return []

        node_list = []
        node = self.end_node

        while node is not None:
            node_list.append(node)
            node = node.parent

        node_list.reverse()

        state_list = [node_list[0].state]

        for i in range(len(node_list) - 1):
            parent = node_list[i]
            child = node_list[i + 1]

            # Sửa lỗi tốc biến: Tìm xem cái thùng nào vừa bị đẩy từ parent sang child
            old_boxes = set(parent.boxes)
            new_boxes = set(child.boxes)
            
            diff_old = old_boxes - new_boxes
            diff_new = new_boxes - old_boxes
            if diff_old and diff_new:
                moved_box_old = list(diff_old)[0]
                moved_box_new = list(diff_new)[0]
                
                # Tính toán hướng đẩy (dx, dy) và vị trí người chơi CẦN ĐỨNG để đẩy cái thùng đó
                dx = moved_box_new[0] - moved_box_old[0]
                dy = moved_box_new[1] - moved_box_old[1]
                player_spot = (moved_box_old[0] - dx, moved_box_old[1] - dy)

                # Sinh ra các trạng thái (frame) diễn tả cảnh người chơi đi bộ tới player_spot
                walk_path = self._find_walk_path(parent.state, parent.player_pos, player_spot)
                
                curr_px, curr_py = parent.player_pos
                for wx, wy in walk_path:
                    new_board = [row[:] for row in state_list[-1]]
                    # Xóa hình ảnh người chơi ở vị trí cũ
                    new_board[curr_px][curr_py] = GOAL if new_board[curr_px][curr_py] == PLAYER_ON_GOAL else FLOOR
                    # Đặt hình ảnh người chơi ở vị trí mới trên đường đi
                    new_board[wx][wy] = PLAYER_ON_GOAL if new_board[wx][wy] == GOAL else PLAYER
                    state_list.append(new_board)
                    curr_px, curr_py = wx, wy
                    
            # Thêm trạng thái bản đồ sau khi đã đẩy thùng thành công
            state_list.append(child.state)

        return state_list
