import pygame
import random
import math
from pygame import Vector2, SurfaceType
from enum import Enum

class ShapeType(Enum):
    Circle = 1
    Box = 2
COLOR_OPTIONS = ['red', 'white' ,'green', 'yellow']
class FlatBody:

    def __init__(self, position:Vector2, mass:float, width:float, height: float, radius: float, shapeType:ShapeType, isStatic = False) -> None:
        self.position = position
        self.velocity = Vector2()
        self.force = Vector2()
        self.rotation = 0
        self.rotationalVelocity = 0

        self.IS_STATIC = isStatic
        #this is to insure there is no negative or zero mass 
        mass = max(mass, 1)
        self.MASS = mass
        if isStatic: self.INVERSE_MASS = 0
        else: self.INVERSE_MASS = 1/mass
        #restitution = relative speed after collision/relative speed before collision ie. bounciness
        self.restitution = random.random()
        
        self.RADIUS = radius
        self.WIDTH = width
        self.HEIGHT = height

        self.shapeType = shapeType

        if self.shapeType == ShapeType.Box:
            self.vertices = create_vectices(width, height)
            self._transformedVertices = self.vertices
            #the triangle indices has to be accending order!!!
            self.triangleIndices = [(0,1,2), (0,2,3)]
        else:
            self.vertices = []
            self._transformedVertices = []
            self.triangleIndices = []
        
        self.transformUpdateNeeded = True
        if isStatic:
            self.color = 'brown'
            self.outLine = 'gray'
        else:
            self.color = random.sample(COLOR_OPTIONS, 1)[0]
            self.outLine = 'white'
    
    def get_transformedVertices(self) -> list:
        if self.transformUpdateNeeded:
            self._transformedVertices = self.transform_vertices()
            self.transformUpdateNeeded = False
        return self._transformedVertices
    
    def transform_vertices(self):
        sine = math.sin(self.rotation)
        cosine = math.cos(self.rotation)
        newVertices = []
        for vertex in self.vertices:
            newVertex = Vector2()
            newVertex.x = vertex.x*cosine-vertex.y*sine
            newVertex.y = vertex.x*sine+vertex.y*cosine
            newVertex += self.position
            newVertices.append(newVertex)
        return newVertices

    def physic_update(self, tickPerSec:int, gravity: Vector2):
        if self.IS_STATIC: gravity = Vector2()
        accleration = self.force/self.MASS + gravity
        self.velocity += accleration/tickPerSec
        self.push_body(self.velocity/tickPerSec)
        self.rotate_body(self.rotationalVelocity/tickPerSec)
        self.force = Vector2()

    def apply_force(self, amount: Vector2) -> None:
        self.force += amount
    def rotate_body(self, amount:float) -> None:
        self.rotation += amount
        self.transformUpdateNeeded = True
    def push_body(self, amount:Vector2) -> None:
        self.position += amount
        self.transformUpdateNeeded = True

    def move_body(self, pos:Vector2) -> None:
        self.position = pos
        self.transformUpdateNeeded = True

    def render(self, display:SurfaceType, pixelPerMeter:int) -> None:
        if self.shapeType == ShapeType.Box:
            pygame.draw.polygon(display, self.color, [worldvertex*pixelPerMeter for worldvertex in self.get_transformedVertices()])
            pygame.draw.polygon(display, self.outLine, [worldvertex*pixelPerMeter for worldvertex in self.get_transformedVertices()], width=1)
        else:
            pygame.draw.circle(display, self.color, self.position*pixelPerMeter, self.RADIUS*pixelPerMeter)
            pygame.draw.circle(display, self.outLine, self.position*pixelPerMeter, self.RADIUS*pixelPerMeter, width=1)
    
def create_circle(position:Vector2, mass:float, radius: float, isStatic = False) -> FlatBody:
    return FlatBody(position, mass, 0, 0, radius, ShapeType.Circle, isStatic)
def create_box(position:Vector2, mass:float, width:float, height: float, isStatic = False) -> FlatBody:
    return FlatBody(position, mass, width, height, 0, ShapeType.Box, isStatic)
def create_vectices(width: float, height:float) -> list:
    """the order of the vertices will be returned CLOCK WISE!!! THIS IS IMPORTANT!!!"""
    left = -width/2
    right = width/2
    top = -height/2
    bottom = height/2
    vertices = [Vector2(left, top),Vector2(right, top),Vector2(right, bottom),Vector2(left, bottom)]
    return vertices
    