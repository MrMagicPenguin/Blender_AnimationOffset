import bpy
from . action_creator import create_offset_action
from . action_creator import create_offset_shapekey_action
from bpy_types import Operator
from mathutils import Vector


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
