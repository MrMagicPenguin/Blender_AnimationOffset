import bpy

active_object = bpy.context.active_object  # ! this should be passed through class context


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
                    # copies the given action to new variable
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
            return False
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
                        for keyframe in kfps:
                            keyframe.co.x += offset_time
                            keyframe.handle_left[0] += offset_time
                            keyframe.handle_right[0] += offset_time

                    return new_action

        else:
            print("No shapekey data!")
    else:
        print("No active object!")
