import bpy
import src.action_creator as ac
from mathutils import Vector

active_object = bpy.context.active_object  # ! this should be passed through class context


def duplicate_linear_offset(iterations, offset_position, offset_key):
    # Create a collection and add the objects to it
    coll = bpy.data.collections.new(active_object.name + "Offset Array")
    bpy.context.scene.collection.children.link(coll)

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

        new_object.animation_data_create()
        new_object.animation_data.action = ac.create_offset_action(offset_key * (i + 1), (0, 0, 0))
