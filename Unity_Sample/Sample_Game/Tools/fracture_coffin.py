# Rompe un modelo gltf en pedazos (Voronoi con cortes planos) y lo exporta como otro gltf.
# Cada pedazo es un objeto aparte, hijo de un vacio en el origen: queda encimado exacto sobre el original.
# Uso (desde Assets/Models/low_poly_graveyard/separados):
#   blender -b -P ../../../../Tools/fracture_coffin.py -- Coffin2.gltf Coffin2_roto.gltf 12
# La malla "Wood" se rompe en N pedazos; las demas (la cruz) quedan como un pedazo entero.
import bpy, bmesh, sys, random, os
from mathutils import Vector

src, dst, n = [os.path.abspath(a) for a in sys.argv[sys.argv.index("--") + 1:][:2]] + [sys.argv[-1]]
n = int(n)
random.seed(7)   # siempre los mismos pedazos

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
originales = [o for o in bpy.data.objects if o.type == 'MESH']

raiz = bpy.data.objects.new(os.path.basename(dst).rsplit(".", 1)[0], None)
bpy.context.scene.collection.objects.link(raiz)

def pedazo(bm, nombre, materiales):
    # origen del pedazo en su centro: gira sobre si mismo al salir volando
    centro = sum((v.co for v in bm.verts), Vector()) / len(bm.verts)
    bmesh.ops.translate(bm, verts=bm.verts, vec=-centro)
    me = bpy.data.meshes.new(nombre)
    bm.to_mesh(me)
    for m in materiales: me.materials.append(m)
    o = bpy.data.objects.new(nombre, me)
    o.location = centro
    o.parent = raiz
    bpy.context.scene.collection.objects.link(o)
    return o

def malla_mundo(o):
    bm = bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)   # el gltf parte vertices por cara
    return bm

k = 0
for o in originales:
    base = malla_mundo(o)
    mats = list(o.data.materials)
    if "Wood" not in o.name:
        pedazo(base, f"pieza_{k:02d}", mats); k += 1   # la cruz sale entera
        continue

    xs = [v.co for v in base.verts]
    lo = Vector([min(c[i] for c in xs) for i in range(3)])
    hi = Vector([max(c[i] for c in xs) for i in range(3)])
    semillas = [Vector([random.uniform(lo[i], hi[i]) for i in range(3)]) for _ in range(n)]

    # el modelo entero como objeto temporal: operando del Boolean. Cerrado: el fondo del ataud viene abierto
    # y con hoyos el Boolean no sabe que es adentro (rellena con la celda y sale debajo del piso)
    bmesh.ops.holes_fill(base, edges=[e for e in base.edges if e.is_boundary])
    me = bpy.data.meshes.new("tmp"); base.to_mesh(me)
    entero = bpy.data.objects.new("tmp", me)
    bpy.context.scene.collection.objects.link(entero)

    for i, s in enumerate(semillas):
        # celda de Voronoi: una caja mas grande que el modelo, recortada por planos. Es convexa:
        # cada corte deja un solo borde plano y se tapa sin errores
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(hi - lo) * 1.001, verts=bm.verts)   # justo del tamano del modelo: nada sale de su caja
        bmesh.ops.translate(bm, vec=(hi + lo) / 2, verts=bm.verts)
        for j, t in enumerate(semillas):
            if i == j: continue
            # se queda solo lo que esta mas cerca de s que de t
            r = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
                                       plane_co=(s + t) / 2, plane_no=(t - s).normalized(), clear_outer=True)
            corte = [e for e in r["geom_cut"] if isinstance(e, bmesh.types.BMEdge) and e.is_valid and e.is_boundary]
            if corte: bmesh.ops.holes_fill(bm, edges=corte)
        celda_me = bpy.data.meshes.new("celda"); bm.to_mesh(celda_me); bm.free()
        celda = bpy.data.objects.new("celda", celda_me)
        bpy.context.scene.collection.objects.link(celda)

        # pedazo = celda INTERSECCION modelo (Exact aguanta la tapa encimada sobre el cuerpo del ataud)
        mod = celda.modifiers.new("corte", 'BOOLEAN')
        mod.operation, mod.solver, mod.object = 'INTERSECT', 'EXACT', entero
        mod.use_self, mod.use_hole_tolerant = True, True
        bpy.context.view_layer.objects.active = celda
        bpy.ops.object.modifier_apply(modifier=mod.name)

        bm = bmesh.new(); bm.from_mesh(celda.data)
        bpy.data.objects.remove(celda)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
        if len(bm.faces) < 4: bm.free(); continue          # la celda no toco el modelo
        for f in bm.faces: f.material_index = 0
        pedazo(bm, f"pieza_{k:02d}", mats); k += 1
    bpy.data.objects.remove(entero)
    base.free()

for o in originales: bpy.data.objects.remove(o)
for o in [o for o in bpy.data.objects if o.type == 'EMPTY' and o != raiz]: bpy.data.objects.remove(o)

bpy.ops.object.select_all(action='DESELECT')
raiz.select_set(True)
for c in raiz.children: c.select_set(True)
bpy.ops.export_scene.gltf(filepath=dst, export_format='GLTF_SEPARATE', use_selection=True)
print("PIEZAS", k)
