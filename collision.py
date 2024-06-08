from pygame import Vector2
import math

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

def _closest_point_on_poly(center:Vector2, vertices:list):
    result = None
    minDis = math.inf
    for vertex in vertices:
        if minDis > (vertex-center).magnitude():
            result = vertex
    return result

def _center_vector(vertices:list):
    total = Vector2()
    for vertex in vertices:
        total += vertex
    return total/len(vertices)



def intersect_poly(verticesA:list, verticesB: list):
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
    centerA = _center_vector(verticesA)
    centerB = _center_vector(verticesB)
    dir = centerB-centerA

    if normal.dot(dir) < 0: normal = -normal
    depth /= normal.magnitude()
    normal = normal.normalize()
    return normal*depth



def intersect_poly_circle(circleCenter: Vector2, circleRadius:float, vertices: list):
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
    centerA = _center_vector(vertices)
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