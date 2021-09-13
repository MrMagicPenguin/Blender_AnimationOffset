import bpy
import numpy as np


def add_array_modifier(count, offsetX, offsetY, offsetZ, offsetU, offsetV):
    # get selected or relevant object
    # Start with object containing correct animation values, assume it is ready to be duplicated.
    active_obj = bpy.context.active_object
    # Add modifier
    mod = active_obj.modifiers.new("Array", "ARRAY")
    # Assign parameters to modifier
    mod.constant_offset_displace = [offsetX, offsetY, offsetZ]
    mod.count = count
    # Adjust UV offset while we are here
    mod.offset_u = offsetU
    mod.offset_v = offsetV


def fcurve_shift(fcurve, shift=(0, 0), shift_handles=True):
    props = ("co", "handle_left", "handle_right") if shift_handles else ("co",)
    for prop in props:
        kfps = np.empty(len(fcurve.keyframe_points) << 1)
        fcurve.keyframe_points.foreach_get(prop, kfps)
        kfps = kfps.reshape((2, -1)) + shift
        fcurve.keyframe_points.foreach_set(prop, kfps.ravel())


# make sure an object *is* active before calling this
def separate_objects():
    bpy.ops.object.modifier_apply(modifier='ARRAY')
    # Separate by loose ends
    bpy.ops.mesh.separate('LOOSE')


def move_nla_strip(tracks, delta):
    for track in tracks:
        for strip in track.strips:
            strip.frame_start += delta
            strip.frame_end += delta


def modulate_anim_property(tracks, delta):
    for track in tracks:
        for strip in track.strips:
            action = strip.action

            for fc in action.fcurves:
                fcurve_shift(fc, (delta, delta))


def index_list(lst: list):
    """
    Returns a new list of the index values of the given list.

    For example, a list of [1,1,1,1] as input would return [0,1,2,3]

    :param lst: Input list
    :return: Output new list of index tokens
    """
    _list = [i for i, e in enumerate(lst)]
    return _list


def get_modifier_list(lst, modifier):
    _mod_list = []
    _mod_list[:] = [i * 3 for i in lst]
    return _mod_list


def move_keyframes():
    # * Animations are stored in Non Linear Actions (NLA) containers, so we assume that any animation will have one
    # * Stored long-term ("pushed down") as an NLA block or otherwise.
    # * Looking up by object rather than by action name is easier so assume any animations must be pushed down

    active_obj = bpy.context.active_object
    objects = bpy.context.selected_objects

    i_list = index_list(objects)
    modifier_list = get_modifier_list(i_list, 3)

    tracks = active_obj.animation_data.nla_tracks  # change to each user

    for obj in objects:
        if obj == active_obj:
            print("Active Object")
            continue
        else:
            print(obj.animation_data.nla_tracks.values())
            print(modifier_list[objects.index(obj)])
            move_nla_strip(tracks, modifier_list[objects.index(obj)])
            modulate_anim_property(obj.animation_data.nla_tracks, modifier_list[objects.index(obj)])


move_keyframes()