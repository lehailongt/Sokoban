from functools import lru_cache

from constants import *


class Node:
    def __init__(self, state, g, parent=None, dead_squares=None, dist_to_goal=None):
        self.state = state
        self.rows = len(self.state)
        self.cols = len(self.state[0]) if self.rows else 0
        self.boxes = self.find_boxes()
        self.goals = self.find_goals()
        # Danh sách các ô bế tắc đã được tính toán từ trước (deadlock precomputation)
        self.dead_squares = dead_squares if dead_squares is not None else set()
        self.dist_to_goal = dist_to_goal if dist_to_goal is not None else {}
        self.player_pos = self.find_player()
        self.node_key = self.get_state_key()
        self.parent = parent
        self.g = g
        self.h = self.heuristic()
        self.f = self.g + self.h if self.h != INF else INF

    def get_state_key(self):
        """
        Tạo key duy nhất cho trạng thái bao gồm vị trí thùng và vị trí người chơi.
        Vì chúng ta tối ưu theo từng bước đi (Step-by-step), nên mỗi vị trí đứng 
        khác nhau của người chơi sẽ được coi là một trạng thái khác nhau.
        """
        return (tuple(sorted(self.boxes)), self.player_pos)

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
        """Heuristic chấp nhận được: ghép tối thiểu giữa thùng và đích.

        Lưu ý: hiện dùng DP bitmask để tính ghép tối thiểu (độ phức tạp O(n * 2^n)),
        phù hợp khi số thùng nhỏ. Đây là lower-bound cho số lần đẩy (push) còn lại.
        """
        if not self.boxes:
            return 0

        if len(self.goals) < len(self.boxes):
            return INF

        boxes = tuple(sorted(self.boxes))
        goals = tuple(sorted(self.goals))

        @lru_cache(maxsize=None)
        def match(box_index, used_mask):
            if box_index == len(boxes):
                return 0

            bx, by = boxes[box_index]
            best = INF

            for goal_index, (gx, gy) in enumerate(goals):
                if used_mask & (1 << goal_index):
                    continue

                tail = match(box_index + 1, used_mask | (1 << goal_index))
                if tail == INF:
                    continue

                # Lấy khoảng cách thực tế đã tính trước. Nếu không tới được thì coi như vô cùng.
                dist = self.dist_to_goal.get(goals[goal_index], {}).get((bx, by), INF)
                if dist == INF:
                    continue
                
                cost = dist + tail
                if cost < best:
                    best = cost

            return best

        return match(0, 0)

    def is_goal_node(self):
        """Kiểm tra xem đã thắng chưa."""
        for i in range(self.rows):
            for j in range(self.cols):
                if self.state[i][j] == BOX:
                    return False
        return True

    def is_deadlocked(self):
        """Kiểm tra deadlock bằng danh sách dead_squares (ô chết) đã được tính toán trước."""
        goal_set = set(self.goals)

        for bx, by in self.boxes:
            # Nếu thùng không nằm trên ô đích và vị trí hiện tại nằm trong dead_squares
            # thì có nghĩa là thùng này không bao giờ có thể được đẩy về đích nữa.
            if (bx, by) not in goal_set:
                if (bx, by) in self.dead_squares:
                    return True
        return False
        # Di chuyển thùng
