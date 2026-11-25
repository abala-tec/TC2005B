# blender -b -P Tools/split_graveyard.py -- <in.gltf> <out_dir>
import bpy, sys, os
from mathutils import Vector
src, out = sys.argv[sys.argv.index("--") + 1:]
os.makedirs(out, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
# material metal-roughness por nombre: (baseColor sRGB, metallic, roughness, emissive sRGB, fuerza)
MAT = {
    "Stone": ("8C8C94", 0.0, 0.85, None, 0), "Wood": ("6B4423", 0.0, 0.75, None, 0),
    "Metall": ("3A3A40", 0.9, 0.45, None, 0), "CoffinCross": ("C9A13B", 1.0, 0.35, None, 0),
    "Ground": ("4A5A2E", 0.0, 1.0, None, 0), "Grass1": ("4F7A2A", 0.0, 0.9, None, 0),
    "Grass2": ("6E9A35", 0.0, 0.9, None, 0), "Treese": ("4A3826", 0.0, 0.95, None, 0),
    "Pumplkin": ("E07B12", 0.0, 0.6, None, 0), "Skull": ("E3DCC6", 0.0, 0.7, None, 0),
    "Mashrooms": ("C8B08A", 0.0, 0.8, None, 0), "fly_agaric_white": ("F2F0E6", 0.0, 0.8, None, 0),
    "material": ("C4241B", 0.0, 0.55, None, 0), "Light": ("FFD873", 0.0, 0.2, "FFC14D", 3),
    "12_-_Default": ("2E2E33", 0.7, 0.5, None, 0), "Bats": ("1A1A1F", 0.0, 0.8, None, 0),
}
def lin(h): return [(int(h[i:i + 2], 16) / 255) ** 2.2 for i in (0, 2, 4)]   # sRGB -> lineal
for m in bpy.data.materials:
    d = MAT.get(m.name.split(".")[0].replace(" ", "_"))
    if not m.node_tree: continue
    if not d: print("SIN MATERIAL EN TABLA:", m.name); continue
    b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    for l in list(b.inputs["Base Color"].links): m.node_tree.links.remove(l)
    b.inputs["Base Color"].default_value = (*lin(d[0]), 1)
    b.inputs["Metallic"].default_value = d[1]
    b.inputs["Roughness"].default_value = d[2]
    # valores glTF por defecto: el import de Sketchfab traia ior 1000 y specular raro
    b.inputs["IOR"].default_value = 1.5
    b.inputs["Specular IOR Level"].default_value = 0.5
    b.inputs["Specular Tint"].default_value = (1, 1, 1, 1)
    if d[3]:
        b.inputs["Emission Color"].default_value = (*lin(d[3]), 1)
        b.inputs["Emission Strength"].default_value = d[4]
root = bpy.data.objects["RootNode"]
elems = list(root.children)
# bake Sketchfab root rotation/scale into each element (clear parent, keep transform)
for e in elems:
    mw = e.matrix_world.copy(); e.parent = None; e.matrix_world = mw
usados = {}
for e in elems:
    objs = [e] + list(e.children_recursive)
    meshes = [o for o in objs if o.type == 'MESH']
    if not meshes: continue
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    mn = Vector(map(min, *pts)); mx = Vector(map(max, *pts))
    # pivot at bottom-center so it sits on the floor at y=0 in Unity
    e.location -= Vector(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mn.z))
    bpy.context.view_layer.update()
    name = e.name.split(".")[0].replace(" ", "_")
    usados[name] = usados.get(name, 0) + 1
    if usados[name] > 1: name += f"_{usados[name]}"
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, name + ".gltf"), export_format='GLTF_SEPARATE', use_selection=True, export_apply=True)
    e.location += Vector(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mn.z))
    print("EXPORTED", name, tuple(round(v, 2) for v in (mx - mn)))
