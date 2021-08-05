import bpy
import src.action_creator as ac
from mathutils import Vector

active_object = bpy.context.active_object  # ! this should be passed through class context


def duplicate_linear_offset(iterations, offset_position, offset_key):
    # Create a collection and add the objects to it
    coll = bpy.data.collections.new(active_object.name + "Offset Array")
    bpy.context.scene.collection.children.link(coll)

    # Move Active Object into new collection for the sake of cleanup
    # ? investigate why Cube continues to exist in Scene Collection as well, may need to be unlinked.
    bpy.data.collections[coll.name].objects.link(active_object)
    bpy.context.view_layer.update()

    # * Store original mesh data
    base_mesh = active_object.data
    base_location = active_object.matrix_world.to_translation()
    base_rotation = active_object.rotation_euler  # don't worry about quaternions 'til you're older, kiddo

    for n in range(3):  # Gets the true values for pos and rot in case of delta
        base_rotation[n] += active_object.delta_rotation_euler[n]

    for i in range(iterations):
        # * Create paramters for new object
        name = active_object.name + str(i)
        mesh = active_object.data
        mesh_copy = mesh.copy()

        new_object = bpy.data.objects.new(name, mesh_copy)

        new_object.location = base_location
        new_object.delta_location = new_object.delta_location + Vector(offset_position) * (i + 1)

        bpy.data.collections[coll.name].objects.link(new_object)
        bpy.context.view_layer.update()

        # remove old action
        if new_object.animation_data:
            new_object.animation_data.clear()

        # Generic animation
        new_object.animation_data_create()
        new_object.animation_data.action = ac.create_offset_action(offset_key * (i + 1), (0, 0, 0))

        # Shapekey animation
        new_object_shapekeys = new_object.data.shape_keys  # convenience variable

        if new_object_shapekeys.animation_data is not None:
            new_object.data.shape_keys.animation_data_clear()

        new_object_shapekeys.animation_data_create()
        new_object_shapekeys.animation_data.action = ac.create_offset_shapekey_action(offset_key * (i + 1))

# test call
# duplicate_linear_offset(1, (0, 3, 0), 10)