# This is the script that is being run through Blender's IDE and should not be considered `Production Ready`

import bpy

active_obj = bpy.context.active_object
# Add modifier
mod = active_obj.modifiers.new("Array", "ARRAY")
# Assign parameters to modifier
mod.relative_offset_displace = [0, 0, 1.1]
mod.count = 4

bpy.ops.object.modifier_apply(modifier='ARRAY')
# Separate by loose ends
bpy.ops.mesh.separate(type='LOOSE')

# TODO Make sure list isn't empty
tracks = active_obj.animation_data.nla_tracks
prev_key = tracks.strips[0].action.fcurves[0].keyframe_points.co
for obj in bpy.context.selected_objects:
    # print(obj.name)
    if obj == bpy.context.active_object:

        print(prev_key)
    else:
        for track in tracks:
            for strip in track.strips:
                action = strip.action
                for fcu in action.fcurves:
                    for keyframe in fcu.keyframe_points:
                        keyframe.co.x = prev_key.x + 2
                        keyframe.co.y = prev_key.y + 2
