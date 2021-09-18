# Thanks and credit to user `lemon` on Blender SE for the scale options
# https://blender.stackexchange.com/questions/75061/scale-uv-map-script

import bpy
from mathutils import Vector, Matrix
import numpy as np
from math import pi, sin, cos, atan2, hypot


def to_cartesian(polar_coord):
    length, angle = polar_coord.x, polar_coord.y
    return Vector((length * cos(angle), length * sin(angle)))


def to_polar(vector):
    x, y = vector[0], vector[1]
    angle = atan2(y, x)
    return Vector((hypot(x, y), angle))


# Get object and UV map given their names
# !rm
def GetObjectAndUVMap(obj, uvMapName):

    if obj is not None:
        if obj.type == 'MESH':
            uvMap = obj.data.uv_layers[uvMapName]
            return obj, uvMap

    print("No Mesh Selected!")

    return None, None


def GetAspectRatio(obj):
    return obj.dimensions.y / obj.dimensions.x


# Scale a 2D vector v, considering a scale s and a pivot point p
def Scale2D(v, s, p):
    # pivot.x + scale.x * vector.x - pivot.x
    # pivot.y + scale.y * vector.y - pivot.y
    return (p[0] + s[0] * (v[0] - p[0]),
            p[1] + s[1] * (v[1] - p[1]))


def Rotate2D(obj, angle, pivot, uvs):
    aspect = GetAspectRatio(obj)
    R = Matrix((
        (np.cos(angle), np.sin(angle) / aspect),
        (-aspect * np.sin(angle), np.cos(angle))
    ))

    uvs = np.dot(
        uvs.reshape((-1, 2)) - pivot,
        R) + pivot

    return uvs


def Translate2D(v, t):
    return ((v[0] + t[0]),
            (v[1] + t[1]))


# Scale a UV map iterating over its coordinates to a given scale and with a pivot point
def ScaleUV(uvMap, scale, pivot):
    for uvIndex in range(len(uvMap.data)):
        uvMap.data[uvIndex].uv = Scale2D(uvMap.data[uvIndex].uv, scale, pivot)


def RotateUV(obj, angle, pivot):
    uvs = np.empty(2 * len(obj.data.loops))
    obj.data.uv_layers.active.data.foreach_get("uv", uvs)
    print(uvs)
    uvs = Rotate2D(obj, angle, pivot, uvs)

    obj.data.uv_layers.active.data.foreach_set("uv", uvs.ravel())
    obj.data.update()

def TranslateUV(uvMap, translate):
    for uvIndex in range(len(uvMap.data)):
        uvMap.data[uvIndex].uv = Translate2D(uvMap.data[uvIndex].uv, translate)


# UV data are not accessible in edit mode
bpy.ops.object.mode_set(mode='OBJECT')

# The names of the object and map
uvMapName = 'UVMap'

# Defines the pivot and scale
wpivot = Vector((0.5, 0.5))
scale = Vector((2, 2))
rotation = pi / 4  # use numpy.radians(degrees) instead
# * Mind that UV coords are in a 0-1 space; adding whole numbers to a vector will not change the pattern significantly.
translate = Vector((1, 0))

# Get the object from names
obj = bpy.context.active_object
uvMap = GetObjectAndUVMap(obj, uvMapName)


# If the object is found, scale its UV map
if obj is not None:
    RotateUV(obj, rotation, wpivot)
