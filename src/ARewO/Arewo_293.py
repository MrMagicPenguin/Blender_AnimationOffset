import random
import bpy
from bpy.props import StringProperty
from mathutils import Vector

# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


# Arewo Simple
def run_linear_offset(loops, offset_frames, random_range, offset_position, offset_rotation, create_parent):
    obj = bpy.context.active_object
    if create_parent:  # if a parent needs to be created
        if obj.parent is None:
            bpy.ops.object.empty_add(type="PLAIN_AXES", location=[0, 0, 0])
            par = bpy.context.active_object
            par.name = "Arewo_Parent"
            obj.parent = par
        else:
            print("Your object already has a parent, this may cause problems.")

    # store original object data
    base_mesh = obj.data
    original_location = obj.matrix_world.to_translation()
    original_rotation = obj.rotation_euler

    for n in range(3):  # Gets the true values for pos and rot in case of delta
        original_rotation[n] += obj.delta_rotation_euler[n]

    for i in range(loops):
        # Creates parameters for the new object
        name = obj.name + str(i)
        new_object = bpy.data.objects.new(name, base_mesh)

        # * This may be a relic system for when Scenes/Layers were handled differently (<2.80)
        bpy.context.scene.objects.link(new_object)
        new_object.layers = obj.layers

        # Offset in Time, Space and Scale
        new_object.location = original_location
        new_object.delta_location = new_object.delta_location + offset_position * (i + 1)  # without for loop

        for n in range(3):
            new_object.delta_rotation_euler[n] = obj.rotation_euler[n] + offset_rotation[n] * (i + 1)
        # creates a random number in +/- half the given range
        random_offset = int(round((random.random() - 0.5) * random_range))
        if offset_frames == 0:
            offset_time = round(random.random() * random_range)
        else:
            offset_time = offset_frames * (i + 1) + random_offset

        # Offset keyframes if Exist
        # ? Shape Keys require additional work
        if obj.animation_data is not None:
            # ? Should be looped for multiple NLA strips?
            new_action = obj.animation_data.action.copy()
            fc = new_action.fcurves
            print(i, ": random: ", random_offset, ", offset Time: ", offset_time)
            for curve in fc:
                kfps = curve.keyframe_points
                for keyframe in kfps:
                    keyframe.co[0] += offset_time
                    keyframe.handle_left[0] += offset_time
                    keyframe.handle_right[0] += offset_time

            new_object.animation_data_create()
            new_object.animation_data.action = new_action

        if create_parent:  # if a parent object was created, the new object will be a child of it
            new_object.parent = par
    bpy.context.scene.update()  # probably unnecessary, just in case though

# linear offset operator
class arewo_simple(bpy.types.Operator):
    bl_idname = "anim.arewo_simple"
    bl_label = "Linear Offset"
    bl_description = "Linear version, only allows for limited options, only one object, no modifiers supported"
    bl_options = {'REGISTER', 'UNDO'}
    # Defining the adjustable parameters
    loops = bpy.props.IntProperty(
        name="Iterations",
        default=2,
        min=1,
        max=10000,
        description="Number of copies to be generated."
    )
    offset_frames = bpy.props.IntProperty(
        name="Offset Frames",
        default=10,
        min=0,
        max=10000,
        description="Offset for the animation in frames"
    )
    random_offset = bpy.props.IntProperty(
        name="Random Offset",
        default=0,
        min=0,
        max=10000,
        description="Random offset for the animation in frames"
    )
    offset_position = bpy.props.FloatVectorProperty(
        name="Location Offset",
        default=[1, 0, 0],
        subtype='TRANSLATION',
        description="Linear location offset"
    )
    offset_rotation = bpy.props.FloatVectorProperty(
        name="Rotation Offset",
        default=[0, 0, 0],
        subtype='EULER',
        description="Rotation offset"
    )
    create_parent = bpy.props.BoolProperty(
        name="Create Parent",
        default=False,
        description="Create a parent object for all added objects"
    )

    def execute(self, context):
        run_linear_offset(
            self.loops,
            self.offset_frames,
            self.random_offset,
            self.offset_position,
            self.offset_rotation,
            self.create_parent
        )
        return {'FINISHED'}

class arewo_panel(bpy.types.Panel):
    """Animation Offset"""
    bl_idname = "arewo.replicate"
    bl_label = "Arewo"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
