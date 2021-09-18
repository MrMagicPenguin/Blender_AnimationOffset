# Thanks and credit to user `lemon` on Blender SE for the scale options
# https://blender.stackexchange.com/questions/75061/scale-uv-map-script

import bpy
from mathutils import Vector
from math import pi, sin, cos, atan2, hypot


def to_cartesian(polar_coord):
    length, angle = polar_coord.x, polar_coord.y
    return Vector((length * cos(angle), length * sin(angle)))


def to_cartesian_pivot(polar_coord, angle, pivot):
    # ? does this change from polar to cartesian? does this formula assume cartesian coords?
    x_rotated = ((polar_coord.x - pivot.x) * cos(angle)) - ((polar_coord.y - pivot.y) * sin(angle)) + pivot.x
    y_rotated = ((polar_coord.x - pivot.x) * sin(angle)) - ((polar_coord.y - pivot.y) * cos(angle))n + pivot.y
    return Vector((x_rotated, y_rotated))


def to_polar(vector):
    x, y = vector[0], vector[1]
    angle = atan2(y, x)
    return Vector((hypot(x, y), angle))


# Get object and UV map given their names
# !rm
def GetObjectAndUVMap(objName, uvMapName):
    try:
        obj = bpy.context.active_object

        if obj.type == 'MESH':
            uvMap = obj.data.uv_layers[uvMapName]
            return obj, uvMap
    except:
        print("No Mesh Selected!")

    return None, None


# Scale a 2D vector v, considering a scale s and a pivot point p
def Scale2D(v, s, p):
    # pivot.x + scale.x * vector.x - pivot.x
    # pivot.y + scale.y * vector.y - pivot.y
    return (p[0] + s[0] * (v[0] - p[0]),
            p[1] + s[1] * (v[1] - p[1]))


def Rotate2D(v, r, p):
    # get distance of vector
    # convert v, p to polar coords
    # add/subtract r from v
    # convert to cartesian
    # return Vector2 coords
    # * thanks to Mark Booth
    # https://stackoverflow.com/questions/620745/c-rotating-a-vector-around-a-certain-point

    v_polar = to_polar(v)
    v_rotated_polar = Vector((v_polar.x, v_polar.y + r))
    v_prime = to_cartesian_pivot(v_rotated_polar, r, p)
    return v_prime


def Translate2D(v, t):
    return ((v[0] + t[0]),
            (v[1] + t[1]))


# Scale a UV map iterating over its coordinates to a given scale and with a pivot point
def ScaleUV(uvMap, scale, pivot):
    for uvIndex in range(len(uvMap.data)):
        uvMap.data[uvIndex].uv = Scale2D(uvMap.data[uvIndex].uv, scale, pivot)


def RotateUV(uvMap, rotation, pivot):
    for uvIndex in range(len(uvMap.data)):
        uvMap.data[uvIndex].uv = Rotate2D(uvMap.data[uvIndex].uv, rotation, pivot)


def TranslateUV(uvMap, translate):
    for uvIndex in range(len(uvMap.data)):
        uvMap.data[uvIndex].uv = Translate2D(uvMap.data[uvIndex].uv, translate)


# UV data are not accessible in edit mode
bpy.ops.object.mode_set(mode='OBJECT')

# The names of the object and map
objName = 'Cube'
uvMapName = 'UVMap'

# Defines the pivot and scale
wpivot = Vector((0.5, 0.5))
scale = Vector((2, 2))
rotation = pi / 4
# * Mind that UV coords are in a 0-1 space; adding whole numbers to a vector will not change the pattern significantly.
translate = Vector((1, 0))

# Get the object from names
obj, uvMap = GetObjectAndUVMap(objName, uvMapName)

# If the object is found, scale its UV map
if obj is not None:
    RotateUV(uvMap, rotation, wpivot)
