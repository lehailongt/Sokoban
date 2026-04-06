import pygame, os
from constants import *


def parse_level(level_number):
    """Chuyển map kí tự: mảng text -> mảng 2 chiều từng kí tự"""
    level_data = LEVELS[level_number]
    
    board = [list(row) for row in level_data]
    return board


def load_image(file_name, default_color):
    """Load ảnh từ file"""
    try:
        path = os.path.join("images", file_name)
        image = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(image, (CELL_SIZE, CELL_SIZE))
    except:
        # Tạo surface màu thay thế
        surface = pygame.Surface((CELL_SIZE, CELL_SIZE))
        surface.fill(default_color)
        pygame.draw.rect(surface, (255, 255, 255), surface.get_rect(), 2)
        return surface

