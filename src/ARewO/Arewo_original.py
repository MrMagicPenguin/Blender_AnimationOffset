import bpy
import math
from mathutils import Vector
import random
from bpy.props import StringProperty, IntProperty

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

bl_info = {
    "name": "arewo",
    "description": "Replicates Objects with their animation offset in time",
    "author": "Frederik Steinmetz",
    "version": (1, 0),
    "blender": (2, 68, 0),
    "location": "Toolshelf",
    "warning": "This is an Alpha version",  # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "http://www.blenderdiplom.com",
    "category": "Animation"}


# Arewo Simple
def run_linear_offset(loops, offset_frames, random_range, offset_position, offset_rotation, create_parent):
    obj = bpy.context.active_object
    if create_parent:  # if a parent needs to be created
        if obj.parent is None:
            bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0), layers=obj.layers)
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
        bpy.context.scene.objects.link(new_object)
        new_object.layers = obj.layers
        # Offset in Time, Space and Scale
        new_object.location = original_location
        new_object.delta_location = new_object.delta_location + Vector(offset_position) * (i + 1)  # without for loop

        for n in range(3):
            new_object.delta_rotation_euler[n] = obj.rotation_euler[n] + offset_rotation[n] * (i + 1)
        # creates a random number in +/- half the given range
        random_offset = int(round((random.random() - 0.5) * random_range))
        if offset_frames == 0:
            offset_time = round(random.random() * random_range)
        else:
            offset_time = offset_frames * (i + 1) + random_offset

        # Offset keyframes if Exist
        if obj.animation_data is not None:
            new_action = obj.animation_data.action.copy()
            fcurves = new_action.fcurves
            print(i, ": random: ", random_offset, ", offset Time: ", offset_time)
            for curve in fcurves:
                keyframePoints = curve.keyframe_points
                for keyframe in keyframePoints:
                    keyframe.co[0] += offset_time
                    keyframe.handle_left[0] += offset_time
                    keyframe.handle_right[0] += offset_time

            new_object.animation_data_create()
            new_object.animation_data.action = new_action

        if create_parent:  # if a parent object was created, the new object will be a child of it
            new_object.parent = par
    bpy.context.scene.update()  # probably unnecessary, just in case though


##################################################################################

# Run Object Offset
def run_object_offset(loops, offset_frames, random_range, starting_frame, spacing, inherit_scale, inherit_rotation,
                      create_parent, hide_render):
    # starting frame of the evaluation of the placer object animation
    bpy.context.scene.frame_set(starting_frame - spacing)
    # Temporarily storing obj as vars
    par = obj = bpy.context.active_object

    if obj.parent is not None:
        print("Your object has a parenting relation, results could be unexpected")
    if create_parent:  # creates a parent object, if needed
        bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0), layers=obj.layers)
        par = bpy.context.active_object
        par.name = "Arewo_Parent"

    placer = bpy.data.objects[bpy.context.scene.placer_object]
    evaluated_frame = starting_frame
    obj_list = []
    for i in range(loops):
        # defines the parameters for the new object
        name_object = obj.name + "_" + str(i)
        empty_mesh = bpy.data.meshes.new("Empty_Mesh")
        obj_list.append(bpy.data.objects.new(name_object, empty_mesh))
        obj_list[i].layers = obj.layers
        bpy.context.scene.objects.link(obj_list[i])
        # sychnronize the parameters with the placer animation
        obj_list[i].location = placer.matrix_world.to_translation()
        if inherit_scale:
            obj_list[i].delta_scale = placer.matrix_world.to_scale()
        if inherit_rotation:
            obj_list[i].delta_rotation_euler = placer.matrix_world.to_euler()
        # creates a random number in +/- half the given range

        random_offset = int(round((random.random() - 0.5) * random_range))
        if offset_frames == 0:
            offset_time = round(random.random() * random_range)
        else:
            random_offset = int(round((random.random() - 0.5) * random_range))
            offset_time = offset_frames * i + random_offset

        if obj.animation_data != None:  # Offset keyframes - if Exist
            if obj.animation_data.action != None:  # Offset keyframes - if Exist
                new_action = bpy.data.actions.new(obj.animation_data.action.name + str(i))
                # creates a copy of the original action
                new_action = obj.animation_data.action.copy()
                # offsets the keyframes by the calculated value
                fcurves = new_action.fcurves
                for curve in fcurves:
                    keyframePoints = curve.keyframe_points
                    for keyframe in keyframePoints:
                        keyframe.co[0] += offset_time
                        keyframe.handle_left[0] += offset_time
                        keyframe.handle_right[0] += offset_time

                obj_list[i].animation_data_create()
                obj_list[i].animation_data.action = new_action

        if create_parent:
            obj_list[i].parent = par
        # evaluates the next frame of the placer animation
        evaluated_frame += spacing
        bpy.context.scene.frame_set(evaluated_frame)
    for me in obj_list:
        me.data = obj.data
    if hide_render:
        obj.hide_render = True
        obj.parent = None
    bpy.context.scene.update()


##################################################################################
# Arewo Experimental
def run_with_armature(loops, offset_frames, random_range, starting_frame, spacing, inherit_rotation, inherit_scale,
                      mute_mods, hide_render):
    if mute_mods:
        run_mute_modifiers()
    else:
        run_enable_modifiers()

    bpy.context.scene.frame_set(starting_frame - spacing)  # moves in time to evaluate placer location
    placer = bpy.data.objects[bpy.context.scene.placer_object]
    par = obj = original_obj = arm = placer  # temp storing objects
    kinder = bpy.context.selected_objects  # stores selected objects
    offset_time = offset_frames
    temp_location = obj.location  # For placing the original at it's original location

    # determines which is the armature
    armcount = 0
    for ob in kinder:
        ob.hide_render = False  # in case they got hidden in the last run
        if ob.type == 'ARMATURE':
            original_arm = ob
            temp_location = original_arm.location  # not working, gets changed everytime you change a parameter, should not be the case...
            armcount += 1
            if armcount > 1:  # checks if there's already an armature in the selected objec
                print("Using multiple armatures can be problematic")
    evaluated_frame = starting_frame
    bpy.context.scene.frame_set(evaluated_frame)
    original_arm.location = placer.matrix_world.to_translation()
    if inherit_rotation:
        original_arm.delta_rotation_euler = placer.matrix_world.to_euler()
    if inherit_scale:
        #   original_arm.delta_scale = placer.matrix_world.to_scale() # give weird results for negative scales
        for n in range(3):
            original_arm.delta_scale[n] = placer.scale[n]

    # For loop starts
    for i in range(loops):
        evaluated_frame += spacing
        bpy.context.scene.frame_set(evaluated_frame)  # advances in time to evaluate placer location

        bpy.ops.object.select_all(action='DESELECT')  # They will only be addressed directly
        for ob in kinder:
            ob.select = True

        bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked": True})
        for ob in bpy.context.selected_objects:  # determine the copy of the armature
            if ob.type == 'ARMATURE':
                arm = ob
        bpy.ops.object.make_single_user(  # Makes the animation data a single user
            type='SELECTED_OBJECTS',
            object=False,
            obdata=False,
            material=False,
            texture=False,
            animation=True
        )
        # Determining how many frammes the animation needs to be offset
        if offset_frames == 0:
            offset_time = round(random.random() * random_range)
        else:  # creates a random number in +/- half the given range
            random_offset = int(round((random.random() - 0.5) * random_range))
            offset_time = offset_frames * i + random_offset

        original_arm.location = placer.matrix_world.to_translation()
        if inherit_rotation:
            original_arm.delta_rotation_euler = placer.matrix_world.to_euler()
        if inherit_scale:
            for n in range(3):
                original_arm.delta_scale[n] = placer.scale[n]
        # Offset the animation if there is one
        if arm.animation_data != None:
            if arm.animation_data.action != None:  # Previously deleted actions still get stored in animation data, so double check
                animData = arm.animation_data
                action = animData.action
                fcurves = action.fcurves
                for curve in fcurves:
                    keyframePoints = curve.keyframe_points
                    for keyframe in keyframePoints:
                        keyframe.co[0] += offset_time
                        keyframe.handle_left[0] += offset_time
                        keyframe.handle_right[0] += offset_time

    # END FOR LOOP
    # hides the original objects
    if hide_render:
        for ob in kinder:
            ob.hide_render = True
    bpy.context.scene.update()


# helper function
def layer(n):
    return (n - 1) * [False] + [True] + (20 - n) * [False]


# function to temporarily disable all but the armature modifiers - for performance increas, duh
def run_mute_modifiers():
    objects = bpy.context.selected_objects
    for ob in objects:
        for mod in ob.modifiers:
            if mod.type != 'ARMATURE':
                mod.show_viewport = False


# function to reenable all modifiers
def run_enable_modifiers():
    objects = bpy.context.selected_objects
    for ob in objects:
        for mod in ob.modifiers:
            mod.show_viewport = True


# Able to apply a modifier and transfers the changes to all objects sharing this datablock
def apply_for_multi(remove_existing, remove_same):
    users = []
    success = False
    mod_type = 'ARMATURE'  # temp storing modifier name
    original = bpy.context.active_object
    for ob in bpy.data.objects:
        ob.select = False
        if ob.data == original.data:
            users.append(ob)

    original.select = True
    bpy.ops.object.make_single_user(object=True, obdata=True)
    try:
        mod_type = original.modifiers[0].type
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=original.modifiers[0].name)
        success = True
    except:
        print("No modifiers found on this object, doing nothing")
    if success:
        for obj in users:
            obj.data = original.data
            if remove_existing:
                for mod in obj.modifiers:
                    obj.modifiers.remove(mod)
            elif remove_same:
                for mod in obj.modifiers:
                    if mod.type == mod_type:
                        obj.modifiers.remove(mod)


def randomize_datablocks(seed):
    objs = bpy.context.selected_objects

    datablocks = []
    materials = [mat.material for mat in bpy.context.active_object.material_slots]
    if (len(materials) > 1):
        for i in range(len(materials)):
            datablocks.append(bpy.context.active_object.data.copy())
            datablocks[i].materials.clear()
            datablocks[i].materials.append(materials[i])

    bpy.ops.object.select_all(action='DESELECT')

    for ob in objs:
        print(ob.type)
        if ob.type == ('MESH' or 'CURVE' or 'SURFACE' or 'FONT'):
            ran = random.randrange(len(materials))
            ob.data = datablocks[ran]
        else:
            print('Object cannot have a material assigned, doing nothing...')


def randomize_materials(seed):
    objs = bpy.context.selected_objects
    bpy.ops.object.make_single_user(object=True, obdata=True, material=False, texture=False, animation=False)
    materials = [mat.material for mat in bpy.context.active_object.material_slots]
    for ob in objs:
        if ob.type == ('MESH' or 'CURVE' or 'SURFACE' or 'FONT'):
            ran = random.randrange(len(materials))
            ob.data.materials.clear()
            ob.data.materials.append(materials[ran])
        else:
            print(ob.name, ' cannot have one or more materials assigned to it, doing nothing...')


# ----------------------------- Operators ------------------------------
# Operator Arewo simple
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
        default=(1, 0, 0),
        subtype='TRANSLATION',
        description="Linear location offset"
    )
    offset_rotation = bpy.props.FloatVectorProperty(
        name="Rotation Offset",
        default=(0, 0, 0),
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


##################################################################################
# Operator arewo Offset Object
class arewo_object_offset(bpy.types.Operator):
    bl_idname = "anim.arewo_object_offset"
    bl_label = "Object Offset"
    bl_description = "Allows great control via a placer object. Only one Mesh, no modifiers supported"
    bl_options = {'REGISTER', 'UNDO'}
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
    starting_frame = bpy.props.IntProperty(
        name="Start Frame",
        default=1,
        min=0,
        max=10000,
        description="Starting time of the path / animation for the placer object"
    )
    spacing = bpy.props.IntProperty(
        name="Spacing",
        default=1,
        min=0,
        max=1000,
        description="No. of Frames in the Placer animation to be skipped before placing the next copy"
    )
    inherit_scale = bpy.props.BoolProperty(
        name="Inherit Scale",
        default=False,
        description="Also copies the scale of the placer object"
    )
    inherit_rotation = bpy.props.BoolProperty(
        name="Inherit Rotation",
        default=False,
        description="Also copies the rotation of the placer object"
    )
    create_parent = bpy.props.BoolProperty(
        name="Create Parent",
        default=False,
        description="Create a parent object for all added objects"
    )
    hide_render = bpy.props.BoolProperty(
        name="Hide Render",
        default=True,
        description="Keeps the original object from being rendered"
    )

    def execute(self, context):
        run_object_offset(
            self.loops,
            self.offset_frames,
            self.random_offset,
            self.starting_frame,
            self.spacing,
            self.inherit_scale,
            self.inherit_rotation,
            self.create_parent,
            self.hide_render
        )
        return {'FINISHED'}
    ##################################################################################


# Operator Armature Offset
class arewo_advanced(bpy.types.Operator):
    bl_idname = "anim.arewo_armature_offset"
    bl_label = "Armature Offset"
    bl_description = "Allows great control via a placer object. Multiple objects and armature supported"
    bl_options = {'REGISTER', 'UNDO'}
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
        max=1000,
        description="Random offset for the animation in frames"
    )
    starting_frame = bpy.props.IntProperty(
        name="Start Frame",
        default=1,
        min=0,
        max=10000,
        description="Starting time of the path / animation for the placer object"
    )
    spacing = bpy.props.IntProperty(
        name="Spacing",
        default=1,
        min=1,
        max=10000,
        description="No. of Frames in the Placer animation to be skipped before placing the next copy"
    )
    inherit_scale = bpy.props.BoolProperty(
        name="Inherit Scale",
        default=False,
        description="Makes the copies the same scale as the placer object at the evaluated frame"
    )
    inherit_rotation = bpy.props.BoolProperty(
        name="Inherit Rotation",
        default=False,
        description="Gives the copies the same rotation as the placer object at the evaluated frame"
    )
    mute_mods = bpy.props.BoolProperty(
        name="Mute Modifiers",
        default=False,
        description="Temporarily hide modifiers, you can re-enable them by using the Enable Modifiers button from the Speed Up Tools",
    )
    hide_render = bpy.props.BoolProperty(
        name="Hide Render",
        default=True,
        description="Keeps the original object from being rendered"
    )

    def execute(self, context):
        run_with_armature(
            self.loops,
            self.offset_frames,
            self.random_offset,
            self.starting_frame,
            self.spacing,
            self.inherit_rotation,
            self.inherit_scale,
            self.mute_mods,
            self.hide_render
        )
        return {'FINISHED'}
    ##################################################################################


class mute_modifiers(bpy.types.Operator):
    bl_idname = "object.mute_modifiers"
    bl_label = "Mute Modifiers"
    bl_description = "Shuts off Viewport visibility of every modifier of the selected objects that is not an Armature"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        run_mute_modifiers()
        return {'FINISHED'}


class enable_modifiers(bpy.types.Operator):
    bl_idname = "object.enable_modifiers"
    bl_label = "Enable Modifiers"
    bl_description = "Enables Viewport visibility of all modifiers of the selected objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        run_enable_modifiers()
        return {'FINISHED'}


class apply_modifier_for_multi(bpy.types.Operator):
    bl_idname = "object.apply_modifier_for_multi"
    bl_label = "Apply Modifier"
    bl_description = "Applies the 1. Modifier of the selected objects and passes the changes to all objects sharing the same datablock"
    bl_options = {'REGISTER', 'UNDO'}
    remove_existing = bpy.props.BoolProperty(
        name="Remove Existing",
        default=False,
        description="Removes all modifiers from objects with the same datablock"
    )
    remove_same = bpy.props.BoolProperty(
        name="Remove Same Type",
        default=True,
        description="Removes modifiers with the same type as the applied one from objects"
    )

    def execute(self, context):
        apply_for_multi(
            self.remove_existing,
            self.remove_same
        )
        return {'FINISHED'}


class random_data(bpy.types.Operator):
    bl_idname = "object.random_data"
    bl_label = "Randomize Datablocks"
    bl_description = "Assigns a random material to each selected object, picking from the material slots of the active_object"
    bl_options = {'REGISTER', 'UNDO'}
    seed = bpy.props.IntProperty(
        name="Seed",
        default=0,
        min=1,
        max=100,
        description="Seed for the random distribution"
    )

    def execute(self, context):
        randomize_datablocks(self.seed)
        return {'FINISHED'}


class random_materials(bpy.types.Operator):
    bl_idname = "object.random_materials"
    bl_label = "Randomize Materials"
    bl_description = "Assigns a random material to each selected object, picking from the material slots of the active_object"
    bl_options = {'REGISTER', 'UNDO'}
    seed = bpy.props.IntProperty(
        name="Seed",
        default=0,
        min=1,
        max=100,
        description="Seed for the random distribution"
    )

    def execute(self, context):
        randomize_materials(self.seed)
        return {'FINISHED'}


# ------------- The Panel ----------------
class arewo_panel(bpy.types.Panel):
    """Animation Offset"""
    bl_idname = "arewo.replicate"  # unique identifier for buttons and menu items to reference.
    bl_label = "Arewo"  # display name in the interface.
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "ARewO"
    bl_context = "objectmode"
    bpy.types.Scene.placer_object = StringProperty(name="Placer Object")

    def draw(self, context):
        layout = self.layout
        split = layout.split()
        row = layout.row()
        col = split.column(align=True)
        col.operator("anim.arewo_simple", icon="MOD_ARRAY")
        if len(bpy.context.selected_objects) > 0 and bpy.context.active_object != None:
            col.enabled = True
        else:
            col.enabled = False
        split = row.split()

        col = split.column(align=True)
        col.operator("anim.arewo_object_offset", icon="PARTICLE_POINT")
        if (bpy.context.active_object == None or len(
                bpy.context.selected_objects) == 0 or bpy.context.scene.placer_object == "" or bpy.context.active_object.type != 'MESH'):
            col.active = False
        else:
            col.active = True

        row2 = layout.row()
        split = row2.split()
        col = split.column(align=True)
        col.operator("anim.arewo_armature_offset", icon="ARMATURE_DATA")
        if (bpy.context.active_object == None or len(
                bpy.context.selected_objects) < 2 or bpy.context.scene.placer_object == "" or not 'ARMATURE' in (ob.type
                                                                                                                 for ob
                                                                                                                 in
                                                                                                                 bpy.context.selected_objects)):
            col.active = False
        else:
            col.active = True
        # Helper tools
        layout.prop_search(
            context.scene,  # not sure
            "placer_object",  # Scene property
            bpy.context.scene,  # where to search
            "objects",  # category to search in
            "Placer:"  # lable name
        )

        layout.label("Speed Up Tools")
        row = layout.row()
        split = row.split()
        col = split.column(align=True)
        col.operator("object.mute_modifiers", icon='VISIBLE_IPO_OFF')
        col.operator("object.enable_modifiers", icon='VISIBLE_IPO_ON')
        col.operator("object.apply_modifier_for_multi", icon='MOD_REMESH')
        row = layout.row()
        split = row.split()
        col = split.column(align=True)
        col.operator("object.random_data", icon='MATERIAL')
        col.operator("object.random_materials", icon='MATERIAL')
        if len(bpy.context.active_object.material_slots) < 2:
            col.active = False
        else:
            col.active = True


# Registering

def register():
    bpy.utils.register_class(arewo_panel)
    bpy.utils.register_class(arewo_simple)
    bpy.utils.register_class(arewo_object_offset)
    bpy.utils.register_class(arewo_advanced)
    bpy.utils.register_class(mute_modifiers)
    bpy.utils.register_class(enable_modifiers)
    bpy.utils.register_class(apply_modifier_for_multi)
    bpy.utils.register_class(random_data)
    bpy.utils.register_class(random_materials)


def unregister():
    bpy.utils.unregister_class(arewo_panel)
    bpy.utils.unregister_class(arewo_simple)
    bpy.utils.unregister_class(arewo_object_offset)
    bpy.utils.unregister_class(arewo_advanced)
    bpy.utils.unregister_class(mute_modifiers)
    bpy.utils.unregister_class(enable_modifiers)
    bpy.utils.unregister_class(apply_modifier_for_multi)
    bpy.utils.unregister_class(random_data)
    bpy.utils.unregister_class(random_materials)


if __name__ == "__main__":
    register()
    print("ARewO successfully registered")
