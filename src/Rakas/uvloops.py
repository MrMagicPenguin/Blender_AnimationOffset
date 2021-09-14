import bpy

# access mesh data:
obj = bpy.context.active_object
mesh_data = obj.data
mesh_loops = mesh_data.loops
uv_index = 0
# iterate teh mesh loops:
for lp in mesh_loops:
    # access uv loop:
    uv_loop = mesh_data.uv_layers[uv_index].data[lp.index]
    uv_coords = uv_loop.uv
    print('vert: {}, U: {}, V: {}'.format(lp.vertex_index,      uv_coords[0], uv_coords[1]))


