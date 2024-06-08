import flatBody
import collision
import random
import pygame
import math
import time
import camera
from pygame import Vector2, SurfaceType
from flatBody import ShapeType, FlatBody

class World:
    def __init__(self, windowSize: Vector2) -> None:
        self.camera = camera.Camera(windowSize)
        #PPM = pixel per meter
        self.DEFAULT_PPM = 20
        self.zoom = 1
        self.pixelsPerMeter = self.DEFAULT_PPM
        self.bound = windowSize/self.DEFAULT_PPM

        self.mousePrevious = (False, False, False)
        self.GRAVITY = Vector2(0, 9.8)
        self.controlBody = flatBody.create_box(self.bound/2, 1,1,1)
        self.controlBody.color = 'blue'
        self.FPS = 0
        self.tempFPS = 0
        self.previousTime = time.time()
        ground  = flatBody.create_box(Vector2(self.bound.x/2, self.bound.y-1), 1, self.bound.x-10, 1, isStatic=True)
        self.flatBodies = [self.controlBody, ground]
        #self.create_randomBodies(10)

    def render(self, display:SurfaceType):
        for body in self.flatBodies:
            body.render(display, self.pixelsPerMeter, self.camera)

    def player_input(self, tickPerSecond):
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()
        cameraMove = Vector2()

        if mouse[0] and not self.mousePrevious[0]:
            body = flatBody.create_box(self.screen_to_world(Vector2(pygame.mouse.get_pos())), 1, 1, 1)
            self.flatBodies.append(body)
        if mouse[2] and not self.mousePrevious[2]:
            radius = random.randrange(5,20)/10
            body = flatBody.create_circle(self.screen_to_world(Vector2(pygame.mouse.get_pos())), 1, radius)
            self.flatBodies.append(body)    
        if keys[pygame.K_EQUALS]:
            self.zoom += 0.125/tickPerSecond
            self.pixelsPerMeter = self.zoom * self.DEFAULT_PPM
        if keys[pygame.K_MINUS]:
            self.zoom -= 0.125/tickPerSecond
            self.pixelsPerMeter = self.zoom * self.DEFAULT_PPM
        if keys[pygame.K_p]:
            self.debug()
        if keys[pygame.K_UP]:
            cameraMove += Vector2(0,1)
        if keys[pygame.K_DOWN]:
            cameraMove += Vector2(0,-1)
        if keys[pygame.K_RIGHT]:
            cameraMove += Vector2(-1,0)
        if keys[pygame.K_LEFT]:
            cameraMove += Vector2(1,0)
        self.camera.position += cameraMove*self.pixelsPerMeter/tickPerSecond*10
        self.control_body(keys)
        self.mousePrevious = mouse

    def step(self, tickPerSecond:int, subStep:int):
        self.tempFPS += 1
        if time.time() > self.previousTime+1:
            self.previousTime = time.time()
            self.FPS = self.tempFPS
            self.tempFPS = 0
        collides = []
        for _ in range(subStep):
            for body in self.flatBodies:
                body.physic_update(tickPerSecond*subStep, self.GRAVITY)
            
            #collision
            flatBodies = self.flatBodies
            for i in range(len(flatBodies)-1):
                bodyA = flatBodies[i]
                aabbA = bodyA.aabb
                for j in range(i+1, len(flatBodies)):
                    bodyB = flatBodies[j]
                    aabbB = bodyB.aabb
                    if not collision.collideAABB(aabbA, aabbB):
                        continue
                    if bodyA.IS_STATIC and bodyB.IS_STATIC:
                        continue
                    collide = collision.get_collide(bodyA, bodyB)
                    if collide == None:
                        continue
                    if bodyA.IS_STATIC:
                        bodyB.push_body(collide)
                        self
                    elif bodyB.IS_STATIC:
                        bodyA.push_body(-collide)
                    else:
                        bodyA.push_body(-collide/2)
                        bodyB.push_body(collide/2)
                    collides.append((collide, bodyA, bodyB))
        for collideInfo in collides:
            collide = collideInfo[0]
            bodyA = collideInfo[1]
            bodyB = collideInfo[2]
            collision.resolve_collision(collide, bodyA, bodyB)
        
        for body in self.flatBodies:
            self.void_bodyPos(body)
            #self.wrap_bodyPos(body)

    def create_randomBodies(self, num:int):
        flatBodies = self.flatBodies
        
        for _ in range(num):
            isStatic = random.randint(1,3) == 0
            pos = Vector2(random.random()*self.bound.x, random.random()*self.bound.y)
            mass = random.randrange(10, 20)/10
            if random.random() <= 0.2:
                width = random.randrange(10, 20)/20
                height = random.randrange(10, 20)/20
                rotation = random.random()*2*math.pi
                body = flatBody.create_box(pos, mass, width, height, isStatic)
                body.rotation = rotation
            else:
                radius = random.randrange(10, 20)/20
                body = flatBody.create_circle(pos, mass, radius, isStatic)
            flatBodies.append(body)
    def control_body(self, keys: list):
        #control the body
        if self.controlBody == None:
            return
        dir = Vector2()
        if keys[pygame.K_w]:
            dir.y -= 1
        if keys[pygame.K_a]:
            dir.x -= 1
        if keys[pygame.K_s]:
            dir.y += 1
        if keys[pygame.K_d]:
            dir.x += 1
        
        self.controlBody.apply_force(dir*100)
    
    def void_bodyPos(self, body:FlatBody):
        if body.position.y > self.bound.y:
            self.flatBodies.remove(body)
    def wrap_bodyPos(self, body: FlatBody):
        body.position.x = body.position.x % self.bound.x
        body.position.y = body.position.y % self.bound.y

    def world_to_screen(self, world_pos:Vector2):
        return (world_pos+self.camera.position)*self.pixelsPerMeter
    
    def screen_to_world(self, screen_pos:Vector2):
        return (screen_pos - self.camera.position)/self.pixelsPerMeter

    def debug(self):
        print(f"FPS: {self.FPS}")
        print(f"Body Count: {len(self.flatBodies)}")