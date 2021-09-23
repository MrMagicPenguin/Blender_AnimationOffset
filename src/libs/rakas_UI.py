import bpy
from bpy_types import (Panel)

class OBJECT_PT_Rakas_Panel(Panel):
    bl_idname = "object_PT_rakas_panel"
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
        layout.prop(settings, "seed_object_uv")

        layout.operator("object.rakas_linear_offset")
