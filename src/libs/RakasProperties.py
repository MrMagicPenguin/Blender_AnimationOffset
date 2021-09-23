import bpy
from bpy.props import (BoolProperty,
                       IntProperty,
                       FloatVectorProperty,
                       StringProperty,
                       PointerProperty,
                       EnumProperty
                       )
from bpy_types import (PropertyGroup)

class RakasProperties(PropertyGroup):
    seed_object: PointerProperty(
        name="Base Object",
        description="Object to duplicate",
        type=bpy.types.Object
    )

    seed_object_uv: EnumProperty()

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