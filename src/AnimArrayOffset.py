import bpy


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


def modulate_anim_property(obj, delta):
    for tracks in obj.animation_data.nla_tracks:
        for track in tracks:
            for strip in track.strips:
                action = strip.action

                for fc in action.fcurves:
                    for kf in fc.keyframe_points:
                        kf.co.y += delta


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
    _mod_list[:] = [i * modifier for i in lst]
    return _mod_list


def move_keyframes():
    # * Animations are stored in Non Linear Actions (NLA) containers, so we assume that any animation will have one
    # * Stored long-term ("pushed down") as an NLA block or otherwise.
    # * Looking up by object rather than by action name is easier so assume any animations must be pushed down

    active_obj = bpy.context.active_object
    objects = bpy.context.selected_objects

    modifier_list = get_modifier_list(objects, 3)
    # TODO Make sure list isn't empty
    tracks = active_obj.animation_data.nla_tracks  # this is a dictionary

    for obj in objects:
        print(obj.name)
        if obj == active_obj:
            print("Active Object!")
            pass
        else:
            print("Selected Object!")
            # get old keyframe
            # make new keyframe = old_keyframe + delta_time || + delta_value
            # delete old keyframes

    # Get all keyframes (X,Y) from a given NLA Action
    # * X Coord is Frame #
    # * Y Coord is Keyed Value
    for obj in bpy.context.selected_objects:
        print(obj.name)
        if obj == bpy.context.active_object:
            print("Active Object!")
            pass
        else:
            print("Selected Object!")
            for i in bpy.context.selected_objects:
                move_nla_strip(tracks, modifier_list[objects.index(obj)])
                modulate_anim_property(tracks, modifier_list[objects.index(obj)])


class ArrayAnimOffsetOperator(bpy.types.Operator):
    bl_idname = "mesh.arr_anim_offset"
    bl_label = "Array Animation Offset Operator"

    def execute(self, context):
        print("Hello World")
        return {'FINISHED'}


bpy.utils.register_class(ArrayAnimOffsetOperator)

bpy.ops.mesh.arr_anim_offset()
