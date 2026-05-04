from collections import deque
from constants import DIRECTIONS, WALL, BOX, BOX_ON_GOAL
from node import Node
from IDA_star import IDAStarSolver
from ultils import parse_level
import time

def optimized_key(self):
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
    return (tuple(sorted(self.boxes)), min(reachable))

Node.get_state_key = optimized_key

from constants import LEVELS
for i in range(len(LEVELS)):
    t0 = time.time()
    solver = IDAStarSolver(parse_level(i))
    solver.solve()
    print(f'Level {i}: {len(solver.visited)} states evaluated in {time.time()-t0:.4f}s')
