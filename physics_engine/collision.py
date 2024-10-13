from pygame import Vector2
from flatBody import FlatBody, ShapeType, FlatAABB
import math

class CollideInfo:
    def __init__(self, collide: Vector2, bodyA: FlatBody, bodyB: FlatBody, contactPoints: list) -> None:
        self.collide = collide
        self.bodyA = bodyA
        self.bodyB = bodyB
        self.contactPoints = contactPoints

def _project_vertices(vertices:list, axis: Vector2) -> tuple:
    minVal = math.inf
    maxVal = -math.inf

    for vertex in vertices:
        proj = axis.dot(vertex)
        minVal = min(proj, minVal)
        maxVal = max(proj, maxVal)
    return minVal, maxVal
def _project_circle(center: Vector2, radius:float, axis: Vector2):
    dir = axis.normalize()
    dirAndRadius = dir*radius
    p1 = center+dirAndRadius
    p2 = center-dirAndRadius
    min, max = axis.dot(p1), axis.dot(p2)
    if min > max:
        min,max = max, min
    return min, max

def find_contact(bodyA:FlatBody, bodyB:FlatBody):
    contact = Vector2()
    if bodyA.shapeType == ShapeType.Box and bodyB.shapeType == ShapeType.Box:
        contact = find_poly_contact_point(bodyA.get_transformedVertices(), bodyB.get_transformedVertices())
    elif bodyA.shapeType == ShapeType.Circle and bodyB.shapeType == ShapeType.Circle:
        contact = [find_circle_contact_point(bodyA.position, bodyB.position, bodyA.RADIUS)]
    elif bodyA.shapeType == ShapeType.Box and bodyB.shapeType == ShapeType.Circle:
        contact = [find_circle_poly_contact_point(bodyB.position, bodyA.get_transformedVertices())]
    elif bodyB.shapeType == ShapeType.Box and bodyA.shapeType == ShapeType.Circle:
        contact = [find_circle_poly_contact_point(bodyA.position, bodyB.get_transformedVertices())]
    return contact
                    
def _closest_point_on_poly(center:Vector2, vertices:list):
    result = None
    minDis = math.inf
    for vertex in vertices:
        if minDis > (vertex-center).magnitude():
            result = vertex
    return result

def point_edge_distance(point: Vector2, a: Vector2, b: Vector2):
    ab = b-a
    ap = point-a
    proj = ap.dot(ab)
    abLenSq = ab.magnitude_squared()

    distance = proj/abLenSq
    contact = None
    if distance <= 0:
        contact = a
    elif distance >= 1:
        contact = b
    else:
        contact = a + ab *distance
    return (contact, (point-contact).magnitude_squared())
        
def find_poly_contact_point(verticesA: list, verticesB: list):

    min_sqrt = math.inf
    contact_points = list[Vector2()]
    for i in range(len(verticesA)):
        p = verticesA[i]
        for j in range(len(verticesB)):
            va = verticesB[j]
            vb = verticesB[(j+1)%len(verticesB)]
            contactInfo = point_edge_distance(p, va, vb)
            
            if round(min_sqrt,5) == round(contactInfo[1],5):
                if contactInfo[0] != contact_points[0]:
                    min_sqrt = contactInfo[1]
                    contact_points.append(contactInfo[0])

            elif min_sqrt > contactInfo[1]:
                min_sqrt = contactInfo[1]
                contact_points = [contactInfo[0]]
    
    for i in range(len(verticesB)):
        p = verticesB[i]
        for j in range(len(verticesA)):
            va = verticesA[j]
            vb = verticesA[(j+1)%len(verticesA)]
            contactInfo = point_edge_distance(p, va, vb)
            
            if round(min_sqrt,5) == round(contactInfo[1],5):
                if contactInfo[0] != contact_points[0]:
                    min_sqrt = contactInfo[1]
                    contact_points.append(contactInfo[0])

            elif min_sqrt > contactInfo[1]:
                min_sqrt = contactInfo[1]
                contact_points = [contactInfo[0]]
    return contact_points
                    



def find_circle_contact_point(centerA: Vector2, centerB: Vector2, radiusA: float):
    ab = centerB-centerA
    if ab.magnitude == 0: return Vector2()
    dir = ab.normalize()
    return centerA + dir*radiusA

def find_circle_poly_contact_point(centerA: Vector2, vertices: list):
    min_sqr = math.inf
    contact_point = Vector2()
    for i in range(len(vertices)):
        va = vertices[i]
        vb = vertices[(i+1)%len(vertices)]
        contactInfo = point_edge_distance(centerA, va, vb)
        if contactInfo[1] < min_sqr:
            min_sqr = contactInfo[1]
            contact_point = contactInfo[0]
    return contact_point


def intersect_poly(verticesA:list, verticesB: list, centerA: Vector2, centerB:Vector2):
    normal = Vector2()
    depth = math.inf
    #SAT using the normal of the 1st polygon as an Axis
    for i in range(len(verticesA)):
        vertex1:Vector2 = verticesA[i]
        vertex2:Vector2 = verticesA[(i+1)%len(verticesA)]

        edge:Vector2 = vertex2-vertex1
        axis = Vector2(-edge.y, edge.x)
        minA, maxA = _project_vertices(verticesA, axis)
        minB, maxB = _project_vertices(verticesB, axis)
        #if there is no closing in any of the axis then there is no collision
        if minA >= maxB or minB >= maxA:
            return None
        #finding the minimum value to resolve the collision
        axisDepth = min(maxB-minA, maxA-minB)
        if axisDepth < depth:
            depth = axisDepth
            normal = axis

    #SAT using the normal of the 2nd polygon as an Axis
    for i in range(len(verticesB)):
        vertex1:Vector2 = verticesB[i]
        vertex2:Vector2 = verticesB[(i+1)%len(verticesB)]

        edge:Vector2 = vertex2-vertex1
        axis = Vector2(-edge.y, edge.x)
        minA, maxA = _project_vertices(verticesA, axis)
        minB, maxB = _project_vertices(verticesB, axis)
        #if there is no closing in any of the axis then there is no collision
        if minA >= maxB or minB >= maxA:
            return None
        #finding the minimum value to resolve the collision
        axisDepth = min(maxB-minA, maxA-minB)
        if axisDepth < depth:
            depth = axisDepth
            normal = axis

    #set the normal vector in the right direction
    dir = centerB-centerA

    if normal.dot(dir) < 0: normal = -normal
    depth /= normal.magnitude()
    normal = normal.normalize()
    return normal*depth



def intersect_poly_circle(circleCenter: Vector2, circleRadius:float, vertices: list, boxCenter: Vector2):
    normal = Vector2()
    depth = math.inf
    #checks using the normals of the polygon as an axis
    for i in range(len(vertices)):
        vertex1:Vector2 = vertices[i]
        vertex2:Vector2 = vertices[(i+1)%len(vertices)]

        edge:Vector2 = vertex2-vertex1
        axis = Vector2(-edge.y, edge.x)
        minA, maxA = _project_vertices(vertices, axis)
        minB, maxB = _project_circle(circleCenter, circleRadius, axis)
        if minA >= maxB or minB >= maxA:
            return None
        axisDepth = min(maxB-minA, maxA-minB)
        if axisDepth < depth:
            depth = axisDepth
            normal = axis
    #checks using the distance between the closest point and circles center as an axis
    closestPoint = _closest_point_on_poly(circleCenter, vertices)
    axis = closestPoint - circleCenter
    minA, maxA = _project_vertices(vertices, axis)
    minB, maxB = _project_circle(circleCenter, circleRadius, axis)

    if minA >= maxB or minB >= maxA:
        return None
    
    axisDepth = min(maxB-minA, maxA-minB)
    if axisDepth < depth:
        depth = axisDepth
        normal = axis
    #set the normal vector in the right direction
    centerA = boxCenter
    centerB = circleCenter
    dir = centerB-centerA
    
    if normal.dot(dir) < 0: normal = -normal
    depth /= normal.magnitude()
    normal = normal.normalize()
    return normal * depth



def intersect_circle(centerA: Vector2, radiusA: float, centerB: Vector2, radiusB: float):
    distance = (centerA-centerB).magnitude()
    radii = radiusA+radiusB
    if distance >= radii:
        return None
    normal = centerA - centerB
    #this is to insure that there is no divide by 0 errors
    if normal != Vector2():
        normal = normal.normalize()
    depth = radii - distance
    return -normal*depth



def collideAABB(aabbA: FlatAABB, aabbB: FlatAABB):
    if aabbA.maxX <= aabbB.minX or aabbB.maxX <= aabbA.minX:
        return False
    if aabbA.maxY <= aabbB.minY or aabbB.maxY <= aabbA.minY:
        return False
    return True
def resolve_collision_with_rotation(contactInfo: CollideInfo):
    collide = contactInfo.collide
    normal = collide.normalize()
    bodyA = contactInfo.bodyA
    bodyB = contactInfo.bodyB
    contactPoints = contactInfo.contactPoints
    e = min(bodyA.restitution, bodyB.restitution)

    impluseList = []
    radiusAList = []
    radiusBList = []

    for cp in contactPoints:
        #the distance from the contact point to the center
        ra = cp - bodyA.position
        rb = cp - bodyB.position
        
        radiusAPerp = Vector2(-ra.y, ra.x)
        radiusBPerp = Vector2(-rb.y, rb.x)

        linearRotationVelocityA = radiusAPerp*bodyA.rotationalVelocity
        linearRotationVelocityB = radiusBPerp*bodyB.rotationalVelocity

        relativeVelocity = bodyB.velocity+linearRotationVelocityB - (bodyA.velocity + linearRotationVelocityA)

        contactVelocityMag = relativeVelocity.dot(normal)

        if contactVelocityMag > 0:
            continue

        raduisAPerpDotNormal = radiusAPerp.dot(normal)
        raduisBPerpDotNormal = radiusBPerp.dot(normal)

        denom = bodyA.INVERSE_MASS + bodyB.INVERSE_MASS + (raduisAPerpDotNormal**2) * bodyA.inverseInteria + (raduisBPerpDotNormal**2) * bodyB.inverseInteria
        j = -(1+e)*contactVelocityMag
        j /= denom
        j /= len(contactPoints)
        impluse = j * normal
        impluseList.append(impluse)
        radiusAList.append(ra)
        radiusBList.append(rb)

    for i in range(len(impluseList)):
        impluse = impluseList[i]
        ra = radiusAList[i]
        rb = radiusBList[i]
        bodyA.velocity += -impluse * bodyA.INVERSE_MASS
        bodyA.rotationalVelocity += -ra.cross(impluse) * bodyA.inverseInteria
        bodyB.velocity += impluse * bodyB.INVERSE_MASS
        bodyB.rotationalVelocity += rb.cross(impluse) * bodyB.inverseInteria

def resolve_collision(collideInfo: CollideInfo):
    bodyA = collideInfo.bodyA
    bodyB = collideInfo.bodyB
    collide = collideInfo.collide
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
        
def get_collide(bodyA:FlatBody, bodyB: FlatBody):
    if bodyA.shapeType == ShapeType.Box and bodyB.shapeType == ShapeType.Box:
        collide = intersect_poly(bodyA.get_transformedVertices(), bodyB.get_transformedVertices(), bodyA.position, bodyB.position)
    elif bodyA.shapeType == ShapeType.Circle and bodyB.shapeType == ShapeType.Circle:
        collide = intersect_circle(bodyA.position, bodyA.RADIUS, bodyB.position, bodyB.RADIUS)
    elif bodyA.shapeType == ShapeType.Box and bodyB.shapeType == ShapeType.Circle:
        collide = intersect_poly_circle(bodyB.position, bodyB.RADIUS, bodyA.get_transformedVertices(), bodyA.position)
    elif bodyB.shapeType == ShapeType.Box and bodyA.shapeType == ShapeType.Circle:
        #the directions has to be swaped since the relations between A and B is swaped if this is not done 
        #then collision will be resolved in the opposite direction leading to shutters
        collide = intersect_poly_circle(bodyA.position, bodyA.RADIUS, bodyB.get_transformedVertices(), bodyB.position)
        if collide != None:
            collide = -collide
    return collide
