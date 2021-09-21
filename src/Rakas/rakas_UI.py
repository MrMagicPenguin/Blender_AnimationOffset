# <pep8 compliant>

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
        description="How much to offset duplicated objects?",
        subtype='TRANSLATION',
        default=[1.0, 0.0, 0.0]
    )

    collection_name: StringProperty(
        name="Name of collection to store duplicates",
        default="object.name"
    )


class OBJECT_OT_Rakas_Main(Operator):
    bl_idname = "object.rakas_main"
    bl_label = "Rakas Example"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        props = scene.rakas_props
        print(props.iterations)

        return {'FINISHED'}


class OBJECT_PT_Rakas_Main(Panel):
    bl_idname = "object_PT_rakas_main"
    bl_label = "Rakas"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tool"

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

        props = layout.operator('object.rakas_main')


classes = (
    RakasProperties,
    OBJECT_OT_Rakas_Main,
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
