import os

import pygame

from constants import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def parse_level(level_number):
    """Chuyển map kí tự: mảng text -> mảng 2 chiều từng kí tự.

    Các level trong file mẫu có thể bị lệch độ dài dòng, nên pad về cùng chiều rộng
    để toàn bộ board luôn hình chữ nhật.
    """
    level_data = LEVELS[level_number]
    width = max(len(row) for row in level_data)
    board = [list(row.ljust(width, WALL)) for row in level_data]
    return board


def load_image(file_name, default_color):
    """Load ảnh từ file hoặc tạo surface thay thế nếu thiếu ảnh."""
    try:
        if not file_name:
            raise FileNotFoundError

        path = os.path.join(BASE_DIR, "images", file_name)
        image = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(image, (CELL_SIZE, CELL_SIZE))
    except Exception:
        surface = pygame.Surface((CELL_SIZE, CELL_SIZE))
        surface.fill(default_color)
        pygame.draw.rect(surface, (255, 255, 255), surface.get_rect(), 2)
        return surface
