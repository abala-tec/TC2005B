using UnityEditor;
using UnityEngine;

// Crea Coffin2_roto.prefab a partir del gltf: a cada pedazo le pone MeshCollider convexo + Rigidbody
// (mismos valores que las piezas de cubo_madera_roto). El prefab es variante del gltf: si se regenera el gltf, se actualiza.
// CLI (con Unity cerrado):
//   Unity -batchmode -quit -projectPath . -executeMethod S9_CrearPiezasRotas.Crear -logFile -
public static class S9_CrearPiezasRotas
{
    const string Gltf = "Assets/Models/low_poly_graveyard/separados/Coffin2_roto.gltf";
    const string Prefab = "Assets/Models/low_poly_graveyard/separados/Coffin2_roto.prefab";

    [MenuItem("Tools/S9/Crear Coffin2_roto con fisica")]
    public static void Crear()
    {
        AssetDatabase.ImportAsset(Gltf, ImportAssetOptions.ForceUpdate);
        GameObject modelo = AssetDatabase.LoadAssetAtPath<GameObject>(Gltf);
        if (modelo == null) throw new System.Exception("No se pudo cargar " + Gltf);

        GameObject inst = (GameObject)PrefabUtility.InstantiatePrefab(modelo);
        int n = 0;
        foreach (MeshFilter mf in inst.GetComponentsInChildren<MeshFilter>())
        {
            MeshCollider mc = mf.gameObject.AddComponent<MeshCollider>();
            mc.sharedMesh = mf.sharedMesh;
            mc.convex = true;                       // un Rigidbody que se mueve necesita collider convexo

            Rigidbody rb = mf.gameObject.AddComponent<Rigidbody>();
            rb.mass = 0.1f;
            rb.isKinematic = true;                  // armada hasta el hachazo (RecibirHachazo la suelta)
            rb.interpolation = RigidbodyInterpolation.Interpolate;
            rb.collisionDetectionMode = CollisionDetectionMode.ContinuousDynamic;
            n++;
        }

        PrefabUtility.SaveAsPrefabAsset(inst, Prefab, out bool ok);
        Object.DestroyImmediate(inst);
        if (!ok) throw new System.Exception("No se pudo guardar " + Prefab);
        Debug.Log($"S9_CrearPiezasRotas: {Prefab} con {n} piezas (MeshCollider convexo + Rigidbody)");
    }
}
