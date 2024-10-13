import pygame
from pygame import Vector2
class Camera:
    def __init__(self, windowSize:Vector2) -> None:
        self.position = Vector2(0,0)
        self.windowSize = windowSize