# This is the script that is being run through Blender's IDE and should not be considered `Production Ready`

import bpy

active_obj = bpy.context.active_object
# Add modifier
mod = active_obj.modifiers.new("Array", "ARRAY")
# Assign parameters to modifier
mod.relative_offset_displace = [0, 0, 1.1]
mod.count = 4

bpy.ops.object.modifier_apply(modifier='Array')
# Separate by loose ends
bpy.ops.mesh.separate(type='LOOSE')

# TODO Make sure list isn't empty

# need an index for each keyframe
# currently only returns keyframe[0]

prev_key = active_obj.animation_data.nla_tracks[0].strips[0].action.fcurves[0].keyframe_points[0].co

for obj in bpy.context.selected_objects:
    print(obj.name)
    if obj == bpy.context.active_object:
        continue
    else:
        for track in obj.animation_data.nla_tracks:
            for strip in track.strips:
                action = strip.action
                for fcu in action.fcurves:
                    for keyframe in fcu.keyframe_points:
                        keyframe.co.x = prev_key.x + 2
                        keyframe.co.y = prev_key.y + 2
                        print(keyframe.co)
                        print(prev_key)