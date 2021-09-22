import bpy

from bpy.props import PointerProperty
from .libs.RakasProperties import RakasProperties
from .libs.object_creator import OBJECT_OT_Rakas_Linear_Offset
from .libs.rakas_UI import OBJECT_PT_Rakas_Panel


bl_info = {
    "name": "Rakas",
    "description": "Replicates Objects, including their Action and Shapekey animation, and adds an offset for both position and time. Based on the ARewO plugin by Frederik Steinmetz",
    "author": "Noah Price, Frederik Steinmetz",
    "version": (1, 1),
    "blender": (2, 80, 0),
    "location": "3D View",
    "warning": "This is an Alpha version",  # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "Animation"
}


classes = (
    RakasProperties,
    OBJECT_PT_Rakas_Panel,
    OBJECT_OT_Rakas_Linear_Offset,
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
