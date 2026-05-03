from collections import deque
import time

from constants import *
from node import Node


class IDAStarSolver:
    def __init__(self, board):
        self.board = [row[:] for row in board]
        self.rows = len(self.board)
        self.cols = len(self.board[0]) if self.rows else 0
        self.start_node = Node(self.board, 0)
        self.end_node = None
        self.time_up = 0
        self.visited = {}

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
                    BOX_ON_GOAL if target_cell == GOAL else BOX
                )

                child = Node(board, node.g + 1, parent=node)
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
        """Trả về list board từ start đến end."""
        if self.end_node is None:
            return []

        state_list = []
        node = self.end_node

        while node is not None:
            state_list.append(node.state)
            node = node.parent

        state_list.reverse()
        return state_list
