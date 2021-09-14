# Thanks and credit to user `lemon` on Blender SE for the scale options
# https://blender.stackexchange.com/questions/75061/scale-uv-map-script

import bpy
from mathutils import Vector
from math import pi, sin, cos, atan2, hypot


def extract_vertex_uv_coords(uvMap, uv_index):
    coord_list = []
    for loop in obj.data.loops:
        uv_loop = uvMap.data[loop.index]
        uv_coords = uv_loop.uv
        coord_list.append(uv_coords)
    return coord_list


def to_cartesian(polar_coord):
    length, angle = polar_coord[0], polar_coord[1]
    return length * cos(angle), length * sin(angle)


def to_polar(vector):
    x, y = vector[0], vector[1]
    angle = atan2(y, x)
    return hypot(vector), angle


# Get object and UV map given their names
def GetObjectAndUVMap(objName, uvMapName):
    try:
        obj = bpy.context.active_object

        if obj.type == 'MESH':
            uvMap = obj.data.uv_layers[uvMapName]
            return obj, uvMap
    except:
        print("Error")

    return None, None


# Scale a 2D vector v, considering a scale s and a pivot point p
def Scale2D(v, s, p):
    # pivot.x + scale.x * vector.x - pivot.x
    # pivot.y + scale.y * vector.y - pivot.y
    return (p[0] + s[0] * (v[0] - p[0]),
            p[1] + s[1] * (v[1] - p[1]))


def Rotate2D(v, r):
    # get distance of vector
    # convert v, p to polar coords
    # add/subtract r from v
    # convert to cartesian
    # return Vector2 coords
    v_polar = [to_polar(v) for v in v]
    v_rotated_polar = [(l, angle + r) for l, angle in v_polar]
    v_rotated = [to_cartesian(p) for p in v_rotated_polar]
    return v_rotated


def Translate2D(v, t):
    return ((v[0] + t[0]),
            (v[1] + t[1]))


# Scale a UV map iterating over its coordinates to a given scale and with a pivot point
def ScaleUV(uvMap, scale, pivot):
    for uvIndex in range(len(uvMap.data)):
        uvMap.data[uvIndex].uv = Scale2D(uvMap.data[uvIndex].uv, scale, pivot)


def RotateUV(uvMap, rotation):
    for uvIndex in range(len(uvMap.data)):
        vertices = extract_vertex_uv_coords(uvMap, uvIndex)
        uvMap.data[uvIndex].uv = Rotate2D(vertices, rotation)


def TranslateUV(uvMap, translate):
    for uvIndex in range(len(uvMap.data)):
        uvMap.data[uvIndex].uv = Translate2D(uvMap.data[uvIndex].uv, translate)


# UV data are not accessible in edit mode
bpy.ops.object.mode_set(mode='OBJECT')

# The names of the object and map
objName = 'Cube'
uvMapName = 'UVMap'

# Defines the pivot and scale
pivot = Vector((0.5, 0.5))
scale = Vector((2, 2))
rotation = pi/4
# * UV coords are in a 0-1 space; adding whole numbers to a vector will not change the pattern significantly.
translate = Vector((1, 0))

# Get the object from names
obj, uvMap = GetObjectAndUVMap(objName, uvMapName)

# If the object is found, scale its UV map
if obj is not None:
    print(extract_vertex_uv_coords(uvMap, 0))

