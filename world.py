import flatBody
import collision
import random
import pygame
import math
from pygame import Vector2, SurfaceType
from flatBody import ShapeType, FlatBody

class World:
    def __init__(self) -> None:
        self.pixelsPerMeter = 10
        self.controlBody = None
        self.flatBodies = [flatBody.create_circle(Vector2(),1,0)]

    def render(self, display:SurfaceType):
        for body in self.flatBodies:
            body.render(display, self.pixelsPerMeter)
    def step(self, tickPerSecond:int):
        for body in self.flatBodies:
            body.physic_update(tickPerSecond)
            body.outLine = 'white'
        
        #collision
        flatBodies = self.flatBodies
        for i in range(len(flatBodies)-1):
            bodyA = flatBodies[i]
            for j in range(i+1, len(flatBodies)):
                bodyB = flatBodies[j]
                collide = self.get_collide(bodyA, bodyB)
                if bodyA.IS_STATIC and bodyB.IS_STATIC or collide == None:
                    continue
                if bodyA.IS_STATIC:
                    bodyB.push_body(collide)
                elif bodyB.IS_STATIC:
                    bodyA.push_body(-collide)
                else:
                    bodyA.push_body(-collide/2)
                    bodyB.push_body(collide/2)
                    self.resolve_collision(collide, bodyA, bodyB)
        
    def resolve_collision(self, collide:Vector2, bodyA:FlatBody, bodyB:FlatBody):
        normal = collide.normalize()
        relativeVelocity = bodyB.velocity-bodyA.velocity
        
        if relativeVelocity.dot(normal) > 0:
            return
        #the minium restitution
        e = min(bodyA.restitution, bodyB.restitution)
        j = -(1+e)*normal.dot(relativeVelocity)
        j /=  bodyA.INVERSE_MASS + bodyB.INVERSE_MASS

        #impluse = the change in momentum
        impluse = j * normal

        bodyA.velocity -= impluse * bodyA.INVERSE_MASS
        bodyB.velocity += impluse * bodyB.INVERSE_MASS 
    def get_collide(self, bodyA:FlatBody, bodyB: FlatBody):
        if bodyA.shapeType == ShapeType.Box and bodyB.shapeType == ShapeType.Box:
            collide = collision.intersect_poly(bodyA.get_transformedVertices(), bodyB.get_transformedVertices())
        elif bodyA.shapeType == ShapeType.Circle and bodyB.shapeType == ShapeType.Circle:
            collide = collision.intersect_circle(bodyA.position, bodyA.RADIUS, bodyB.position, bodyB.RADIUS)
        elif bodyA.shapeType == ShapeType.Box and bodyB.shapeType == ShapeType.Circle:
            collide = collision.intersect_poly_circle(bodyB.position, bodyB.RADIUS, bodyA.get_transformedVertices())
        elif bodyB.shapeType == ShapeType.Box and bodyA.shapeType == ShapeType.Circle:
            #the directions has to be swaped since the relations between A and B is swaped if this is not done 
            #then collision will be resolved in the opposite direction leading to shutters
            collide = collision.intersect_poly_circle(bodyA.position, bodyA.RADIUS, bodyB.get_transformedVertices())
            if collide != None:
                collide = -collide
        return collide


    def create_randomBodies(self, num: int, bound):
        bound = (bound[0]//self.pixelsPerMeter, bound[1]//self.pixelsPerMeter)
        flatBodies = self.flatBodies
        
        for _ in range(num):
            isStatic = False#random.randint(0,1) == 0
            pos = Vector2(random.randrange(0, bound[0]), random.randrange(0, bound[1]))
            mass = random.randrange(1, 10)
            if random.random() <= 0.5:
                width = random.randrange(1, 2)
                height = random.randrange(1, 2)
                rotation = random.random()*2*math.pi
                body = flatBody.create_box(pos, mass, width, height, isStatic)
                body.rotation = rotation
            else:
                radius = random.randrange(1, 2)
                body = flatBody.create_circle(pos, mass, radius, isStatic)
            flatBodies.append(body)
        if num >= 1: self.controlBody = flatBodies[1]

    def control_body(self):
        #control the body
        if self.controlBody == None:
            return
        dir = Vector2()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            dir.y -= 1
        if keys[pygame.K_a]:
            dir.x -= 1
        if keys[pygame.K_s]:
            dir.y += 1
        if keys[pygame.K_d]:
            dir.x += 1
        
        self.controlBody.apply_force(dir*100)