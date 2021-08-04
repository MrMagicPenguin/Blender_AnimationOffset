import bpy

obj = bpy.context.active_object

if obj.data.shape_keys is not None:
    for shapekey in obj.data.shape_keys.animation_data.nla_tracks:
        print(shapekey.strips[0].action)

if obj.animation_data.nla_tracks is not None:
    for track in obj.animation_data.nla_tracks:
        print(track.strips[0].action)
