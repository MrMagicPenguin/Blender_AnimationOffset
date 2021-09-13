import bpy
from mathutils import Vector


# Get object and UV map given their names
def GetObjectAndUVMap(objName, uvMapName):
    try:
        obj = bpy.data.selobjects[objName]

        if obj.type == 'MESH':
            uvMap = obj.data.uv_layers[uvMapName]
            return obj, uvMap
    except:
        print("Error")

    return None, None


# Scale a 2D vector v, considering a scale s and a pivot point p
def Scale2D(v, s, p):
    return (p[0] + s[0] * (v[0] - p[0]), p[1] + s[1] * (v[1] - p[1]))


def Rotate2D(v, r, p):
    pass


def Translate2D(v, t, p):


# Scale a UV map iterating over its coordinates to a given scale and with a pivot point
def ScaleUV(uvMap, scale, pivot):
    for uvIndex in range(len(uvMap.data)):
        uvMap.data[uvIndex].uv = Scale2D(uvMap.data[uvIndex].uv, scale, pivot)


# UV data are not accessible in edit mode
bpy.ops.object.mode_set(mode='OBJECT')

# The names of the object and map
objName = 'Cube'
uvMapName = 'UVMap'

# Defines the pivot and scale
pivot = Vector((0.5, 0.5))
scale = Vector((2, 2))

# Get the object from names
obj, uvMap = GetObjectAndUVMap(objName, uvMapName)

# If the object is found, scale its UV map
if obj is not None:
    ScaleUV(uvMap, scale, pivot)