import bpy
from bpy.props import (BoolProperty,
                       IntProperty,
                       FloatVectorProperty,
                       StringProperty,
                       PointerProperty,
                       )
from bpy_types import (PropertyGroup,
                       Operator,
                       Panel)
from mathutils import Vector


def create_offset_action(seed_obj, offset_time: int, offset_value: tuple):
    """
    Creates a duplicate action for each action on an active object.

    :param offset_time: How many keyframes to offset the new action by relative to the start of the seed action?
    :param offset_value: How far to offset the property values of the new action relative to the seed action?
    :return: Reference to new action
    """

    # & Remove axis from this method or introduce bool for when dealing with loc/rot data_path
    # & Feels too specific for this method and repeats earlier expressions in run_linear_offset for handling loc/rot
    if seed_obj is not None:  # TODO refactor to param obj
        if seed_obj.animation_data is not None:
            for track in seed_obj.animation_data.nla_tracks:
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


def create_offset_shapekey_action(seed_obj, offset_time: int):
    """

    :param offset_time: How many keyframes to offset the new action by relative to the start of the seed action?
    :return: Reference to new action
    """
    if seed_obj is not None:
        if seed_obj.data.shape_keys.animation_data is not None:
            for tracks in seed_obj.data.shape_keys.animation_data.nla_tracks:
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


# TODO make operator
def duplicate_linear_offset(seed_obj, iterations, offset_position, offset_key, duplicate_actions, duplicate_shapekeys, collection_name):
    # Create a collection and add the objects to it

    coll = bpy.data.collections.new(collection_name)
    bpy.context.scene.collection.children.link(coll)

    # Move Active Object into new collection for the sake of cleanup
    # * Cube remains in 'Master' collection - add toggle for if it should be unlinked from there to keep things clean.
    bpy.data.collections[coll.name].objects.link(seed_obj)
    bpy.context.view_layer.update()

    # * Store original mesh data
    base_mesh = seed_obj.data
    base_location = seed_obj.matrix_world.to_translation()
    base_rotation = seed_obj.rotation_euler  # don't worry about quaternions 'til you're older, kiddo

    for n in range(3):  # Gets the true values for pos and rot in case of delta
        base_rotation[n] += seed_obj.delta_rotation_euler[n]

    for i in range(iterations):
        # * Create paramters for new object
        name = seed_obj.name + str(i)
        mesh = seed_obj.data
        mesh_copy = mesh.copy()

        new_object = bpy.data.objects.new(name, mesh_copy)

        new_object.location = base_location
        new_object.rotation_euler = base_rotation
        # Investigate using the actual object dimensions instead of world space coords
        new_object.delta_location += Vector(offset_position) * (i + 1)

        bpy.data.collections[coll.name].objects.link(new_object)
        bpy.context.view_layer.update()

        if duplicate_actions:
            if new_object.animation_data:
                new_object.animation_data.clear()
            # Creates blank animation
            new_object.animation_data_create()

            # TODO Look into how to expose or remove the 0,0,0 without breaking things
            new_object.animation_data.action = create_offset_action(seed_obj, offset_key * (i + 1), (0, 0, 0))

        # Shapekey animation
        if duplicate_shapekeys:
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

# for obj in bpy.context.selected_objects:
    # push_down_shapekey_actions(obj)
    # duplicate_linear_offset(obj, 5, (0, 0, .101), 3)


class RakasProperties(PropertyGroup):
    seed_object: PointerProperty(
        name="Base Object",
        description="Object to duplicate",
        type=bpy.types.Object
    )

    iterations: IntProperty(
        name="Iterations",
        description="How many copies of the object?",
        default=2,
        min=1,
        max=10000
    )

    duplicate_actions: BoolProperty(
        name="Duplicate Actions",
        description="Duplicate NLA Actions on seed object?",
        default=False,
    )

    duplicate_shapekeys: BoolProperty(
        name="Duplicate Shapekeys",
        description="Duplicate Shapekey Actions on seed object?",
        default=False,
    )

    offset_time: IntProperty(
        name="Offset Time",
        description="How many frames to offset from the original action?",
        default=0,
        min=0
    )

    offset_position: FloatVectorProperty(
        name="Position Offset",
        description="How much to offset duplicated object's position?",
        subtype='TRANSLATION',
        default=[1.0, 0.0, 0.0]
    )

    offset_rotation: FloatVectorProperty(
        name="Rotation Offset",
        description="How much to offset duplicated object's position?",
        subtype='ROTATION',
        default=[0.0, 0.0, 0.0]
    )

    collection_name: StringProperty(
        name="Name of collection to store duplicates",
        default="object.name"
    )


class OBJECT_OT_Rakas_Linear_Offset(Operator):
    bl_idname = "object.rakas_linear_offset"
    bl_label = "Linear Offset"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        props = scene.rakas_props

        duplicate_linear_offset(props.seed_object,
                                props.iterations,
                                props.offset_position,
                                props.offset_time,
                                props.duplicate_actions,
                                props.duplicate_shapekeys,
                                props.collection_name)

        return {'FINISHED'}


class OBJECT_PT_Rakas_Main(Panel):
    bl_idname = "object_PT_rakas_main"
    bl_label = "Rakas"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Rakas"

    @classmethod
    def poll(self, context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        layout.label(text="Rakas Settings")
        settings = context.scene.rakas_props
        layout.prop(settings, "seed_object")
        layout.prop(settings, "iterations")
        layout.prop(settings, "duplicate_actions")
        layout.prop(settings, "duplicate_shapekeys")
        layout.prop(settings, "offset_time")
        layout.prop(settings, "offset_position")
        layout.prop(settings, "collection_name", text="")

        props = layout.operator('object.rakas_linear_offset')


classes = (
    RakasProperties,
    OBJECT_OT_Rakas_Linear_Offset,
    OBJECT_PT_Rakas_Main
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.rakas_props = PointerProperty(type=RakasProperties)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.rakas_props


if __name__ == "__main__":
    register()
