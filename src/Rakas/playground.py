import bpy
import numpy as np
from mathutils import Vector

active_object = bpy.context.active_object


def create_offset_action(offset_time: int, offset_value: tuple):
    """
    Creates a duplicate action for each action on an active object.

    :param offset_time: How many keyframes to offset the new action by relative to the start of the seed action?
    :param offset_value: How far to offset the property values of the new action relative to the seed action?
    :return: Reference to new action
    """

    # ? take active_object reference out of this method?
    # & Remove axis from this method or introduce bool for when dealing with loc/rot data_path
    # & Feels too specific for this method and repeats earlier expressions in run_linear_offset for handling loc/rot
    if active_object is not None:
        if active_object.animation_data is not None:
            for track in active_object.animation_data.nla_tracks:
                for strip in track.strips:
                    action = strip.action
                    new_action = bpy.data.actions[action.name].copy()

                    fcurves = [fc for fc in new_action.fcurves]
                    for curve in fcurves:
                        kfps = curve.keyframe_points
                        axis = curve.array_index  # axis x,y,z as 0,1,2 for location & rotation
                        for keyframe in kfps:
                            keyframe.co.y += offset_value[axis]
                            keyframe.co.x += offset_time
                            keyframe.handle_left[0] += offset_time
                            keyframe.handle_right[0] += offset_time

                    return new_action
        else:
            print("No stored actions on active object!")
    else:
        print("No Active Object!")


def create_offset_shapekey_action(offset_time: int):
    """

    :param offset_time: How many keyframes to offset the new action by relative to the start of the seed action?
    :return: Reference to new action
    """
    if active_object is not None:
        if active_object.data.shape_keys.animation_data is not None:
            for tracks in active_object.data.shape_keys.animation_data.nla_tracks:
                for strip in tracks.strips:
                    action = strip.action
                    new_action = bpy.data.actions[action.name].copy()

                    fcurves = [fc for fc in new_action.fcurves]
                    for fc in fcurves:
                        kfps = fc.keyframe_points
                        for kf in kfps:
                            print(kf.co.x)
                            print(kf.co.x + offset_time)
                            kf.co.x += offset_time
                            kf.handle_left[0] += offset_time
                            kf.handle_right[0] += offset_time

                    return new_action

        else:
            print("No shapekey data!")
    else:
        print("No active object!")


def duplicate_linear_offset(obj, iterations, offset_position, offset_key):
    # Create a collection and add the objects to it
    coll = bpy.data.collections.new(obj.name + "Offset Array")
    bpy.context.scene.collection.children.link(coll)

    # Move Active Object into new collection for the sake of cleanup
    # ? investigate why Cube continues to exist in Scene Collection as well, may need to be unlinked.
    bpy.data.collections[coll.name].objects.link(obj)
    bpy.context.view_layer.update()

    # * Store original mesh data
    base_mesh = obj.data
    base_location = obj.matrix_world.to_translation()
    base_rotation = obj.rotation_euler  # don't worry about quaternions 'til you're older, kiddo

    for n in range(3):  # Gets the true values for pos and rot in case of delta
        base_rotation[n] += obj.delta_rotation_euler[n]

    for i in range(iterations):
        # * Create paramters for new object
        name = obj.name + str(i)
        mesh = obj.data
        mesh_copy = mesh.copy()

        new_object = bpy.data.objects.new(name, mesh_copy)

        new_object.location = base_location
        new_object.rotation_euler = base_rotation
        # Investigate using the actual object dimensions instead of world space coords
        new_object.delta_location += Vector(offset_position) * (i + 1)

        bpy.data.collections[coll.name].objects.link(new_object)
        bpy.context.view_layer.update()

        # remove old action
        if new_object.animation_data:
            new_object.animation_data.clear()

        # Generic animation
        new_object.animation_data_create()
        new_object.animation_data.action = create_offset_action(offset_key * (i + 1), (0, 0, 0))

        # Shapekey animation
        new_object_shapekeys = new_object.data.shape_keys  # convenience variable

        if new_object_shapekeys.animation_data is not None:
            new_object.data.shape_keys.animation_data_clear()

        new_object_shapekeys.animation_data_create()
        new_object_shapekeys.animation_data.action = create_offset_shapekey_action(offset_key * (i + 1))


def push_down_shapekey_actions(obj):
    if obj.data.shape_keys.animation_data is not None:
        action = obj.data.shape_keys.animation_data.action
        if action is not None:
            track = obj.data.shape_keys.animation_data.nla_tracks.new()
            track.strips.new(action.name, action.frame_range[0], action)
            obj.data.shape_keys.animation_data.action = None
    else:
        print("No anim data")


# This is in BU/FT/M etc, be aware of seed obj scaling
# duplicate_linear_offset(active_object, 17, (0.145, 0, 0), 3)

for obj in bpy.context.selected_objects:
    push_down_shapekey_actions(obj)
    # duplicate_linear_offset(obj, 5, (0, 0, .101), 3)