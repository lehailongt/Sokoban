from constants import *
from node import Node
import time

class IDAStarSolver:
    def __init__(self, board):
        self.board = board
        self.rows = len(self.board)
        self.cols = len(self.board[0])
        self.goals = self.find_goals()
        self.player_pos = self.find_player()

        self.start_node = Node(board, 0)
        self.end_node = None
        self.time_up = 0
        self.visited = {}
    
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
    
    def solve(self):
        """Giải bài toán bằng IDA*"""
        # BẮT ĐẦU ĐO THỜI GIAN
        start_time = time.time()
        threshold = self.start_node.h
        while True:
            visited = {}
            visited[self.start_node.node_key] = self.start_node
            node_list = [self.start_node]
            while len(node_list) > 0:
                current_node = node_list.pop()
                visited[current_node.node_key] = current_node
                if current_node.is_goal_node():
                    end_time = time.time()
                    self.time_up = end_time - start_time
                    print(f"Thời gian chạy thuật toán IDA*: {self.time_up}")
                    print(f"Số trạng thái đã duyệt {len(visited)}")
                    self.end_node = current_node
                    self.visited = visited
                    return
                for direction in DIRECTIONS:
                    next_node = current_node.next(direction)

                    if next_node == None or next_node.node_key in visited or next_node.f > threshold:
                        continue
                    node_list.append(next_node)
            print(f"Tăng ngưỡng lên: {threshold}")
            threshold += STEP_BETA
            # Điều kiện khi biết sẽ không có lời giải
            if threshold > 100: return

    def get_solution(self):
        # Trẻ về đường dẫn tới chiến thắng: list board
        node_key = self.end_node.node_key # type: ignore
        state_list = [self.end_node.state] # type: ignore

        start_key = self.start_node.node_key

        while node_key != start_key:
            current_node = self.visited[node_key]
            node_key = current_node.pre_node_key
            if node_key is not None:
                state_list.append(self.visited[node_key].state)

        state_list.reverse()
        return state_list




