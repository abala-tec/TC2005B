using UnityEngine;

// Crea un hijo "XRay" con un SpriteRenderer que usa el material de rayos X
// (Custom/SpriteXRayOutline) y le copia el sprite del padre cada frame,
// para que el contorno siga la animacion. Solo se ve cuando hay una pared enfrente.
public class S9_XRaySprite : MonoBehaviour
{
    public Material xrayMaterial;                 // XRay_Velma o XRay_Zombie

    private SpriteRenderer padre = null;
    private SpriteRenderer xray = null;

    void Start()
    {
        padre = GetComponent<SpriteRenderer>();

        // Si este objeto es clon de un molde que ya tenia el hijo, lo reutilizamos
        Transform t = transform.Find("XRay");
        if (t == null)
        {
            t = new GameObject("XRay").transform;
            t.SetParent(transform, false);
        }

        xray = t.GetComponent<SpriteRenderer>();
        if (xray == null) xray = t.gameObject.AddComponent<SpriteRenderer>();
        xray.sharedMaterial = xrayMaterial;
        xray.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
        xray.receiveShadows = false;
    }

    void LateUpdate()
    {
        if (padre == null || xray == null) return;
        xray.sprite  = padre.sprite;
        xray.flipX   = padre.flipX;
        xray.flipY   = padre.flipY;
        xray.enabled = padre.enabled;
    }
}
