using Unity.VisualScripting;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.UIElements;   // el proyecto solo usa el nuevo Input System

[RequireComponent(typeof(Collider))]   // sin collider el raycast no detecta la piedra
[RequireComponent(typeof(Rigidbody))]
public class S9_RockDragDrop : MonoBehaviour
{
    private Camera mainCamera;
    private float liftHeight = 2.0f; // distancia del piso al suelo, cuando se alza la piedra
    private float alturaArrastre;         // Distancia de profundidad desde la cámara
    private bool arrastrando;  // cuando la piedra se esta moviendo (flag)
    public float rockStep = 2.0f;    // cuanto se mueve la piedra por el grid (con cada tecla)
    public float rockRepeat = 0.15f; // segundos entre cada paso mientras la tecla siga presionada
    public GameObject replacementPrefab;
    public float hachazoFuerza = 0.3f;      // impulso de cada pieza hacia el lado opuesto al golpe (masa pieza = 0.1)
    public float hachazoDispersion = 0.1f;  // impulso hacia afuera del centro de la caja (que se abra)
    public float hachazoArriba = 0.15f;     // impulso hacia arriba
    public float hachazoGiro = 0.01f;       // giro aleatorio de cada pieza
    private float tiempoPaso = 0f;   // cuenta regresiva para el siguiente paso
    [SerializeField] public GameObject player;
    private S9_VelmaWalk_3D velma3D;  // gameobject dle jugador para bloquear sus controles
    private bool dropped = false; // cuando la piedra cae (para recalcular el grid)
    private Rigidbody rigdbody;
    private Collider rockCollider;
    private bool velmaDebajo = false; // true = esta piedra tiene a Velma atrapada debajo
    public Material outlineMaterial;  // RockOutline_Rojo: contorno palpitante cuando Velma esta debajo
    private Material outlineInstancia; // copia propia (cada piedra tiene su centro)
    private MeshRenderer[] rockRenderers;  // solo las mallas de la caja (un gltf como Coffin2 trae varias: madera + cruz)
    public Color colorDestino = new Color(0.2f, 0.5f, 1f, 1f);   // contorno de las casillas donde va a caer
    private LineRenderer destino;      // se ve en el juego (no es gizmo): indicador para el jugador

    // un gltf trae sus mallas como hijos en la capa Default: toda la caja en la capa del padre (Cajas)
    // para que el grid (CheckBox) y el hachazo la vean aunque el collider este en un hijo
    void Awake()
    {
        foreach (Transform t in GetComponentsInChildren<Transform>(true)) t.gameObject.layer = gameObject.layer;
    }

    void Start()
    {
        mainCamera = Camera.main;  // objeto de la camara del juego
        velma3D = player.GetComponent<S9_VelmaWalk_3D>();
        rigdbody = GetComponent<Rigidbody>();
        rockCollider = GetComponent<Collider>();
        rockRenderers = GetComponentsInChildren<MeshRenderer>();
        rigdbody.isKinematic = true;
        if (outlineMaterial != null) outlineInstancia = new Material(outlineMaterial);

        // si la version rota es un molde dentro de la escena, se esconde (solo se clona al hachazo)
        if (replacementPrefab != null && replacementPrefab.scene.IsValid()) replacementPrefab.SetActive(false);

        // NO es hijo de la caja: si lo fuera, se copiaria al clonar el molde y contaria como malla de la caja
        // (descuadra el contorno rojo y la medida para apoyarla en el piso)
        destino = new GameObject(name + "_destino").AddComponent<LineRenderer>();
        destino.useWorldSpace = true;
        destino.loop = true;
        destino.positionCount = 4;
        destino.widthMultiplier = 0.06f;
        destino.material = new Material(Shader.Find("Sprites/Default"));   // unlit, usa el color de la linea
        destino.startColor = destino.endColor = colorDestino;
        destino.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
        destino.enabled = false;
    }

    // contorno de las casillas del grid que va a ocupar la caja al caer (cae recto: misma huella en X,Z)
    private void MostrarDestino()
    {
        S9_Grid g = S9_Grid.Instancia;
        Physics.SyncTransforms();         // la caja se movio por transform: que el collider este donde se ve
        g.RectBloqueado(rockCollider, out Vector3 a, out Vector3 c);   // las mismas casillas que se pintan de rojo
        float y = 0.03f;                  // apenas sobre el piso
        destino.SetPositions(new[] { new Vector3(a.x, y, a.z), new Vector3(c.x, y, a.z), new Vector3(c.x, y, c.z), new Vector3(a.x, y, c.z) });
    }

    // prende/apaga el contorno: agrega o quita el material extra del renderer de la piedra
    // (un material extra vuelve a dibujar la misma malla con el shader del contorno)
    private void MostrarContorno(bool value)
    {
        if (outlineInstancia == null) return;

        foreach (Renderer r in rockRenderers)
        {
            var mats = new System.Collections.Generic.List<Material>(r.sharedMaterials);
            mats.Remove(outlineInstancia);
            if (value) mats.Add(outlineInstancia);
            r.sharedMaterials = mats.ToArray();
        }
    }

    void LateUpdate()
    {
        // el shader agranda la malla desde su centro: se lo pasamos (cambia mientras la piedra cae)
        if (velmaDebajo && outlineInstancia != null)
        {
            // un solo centro para todas las mallas: el contorno crece parejo alrededor de toda la caja
            Bounds b = rockRenderers[0].bounds;
            foreach (Renderer r in rockRenderers) b.Encapsulate(r.bounds);
            outlineInstancia.SetVector("_Center", b.center);
        }
    }

    void OnDestroy()
    {
        if (outlineInstancia != null) Destroy(outlineInstancia);
        if (destino != null) { Destroy(destino.material); Destroy(destino.gameObject); }
    }

    // la piedra esta encima de Velma si la posicion de Velma (en X,Z) cae dentro de la huella de la piedra
    private bool CubreAVelma()
    {
        Bounds b = rockCollider.bounds;
        Vector3 p = player.transform.position;
        return p.x >= b.min.x && p.x <= b.max.x && p.z >= b.min.z && p.z <= b.max.z;
    }

    static Vector3 CentroMallas(GameObject g)
    {
        MeshRenderer[] rs = g.GetComponentsInChildren<MeshRenderer>();
        if (rs.Length == 0) return g.transform.position;
        Bounds b = rs[0].bounds;
        foreach (MeshRenderer r in rs) b.Encapsulate(r.bounds);
        return b.center;
    }

    public bool RecibirHachazo(Vector3 pos)
    {
        if (replacementPrefab != null)
        {
            // la version rota conserva SU rotacion y escala (ajustadas en la escena para verse igual a la caja):
            // la caja y su version rota pueden venir de modelos con escalas distintas (Coffin2 0.023 vs Coffin2_roto 2.34)
            GameObject newObject = Instantiate(replacementPrefab, transform.position, replacementPrefab.transform.rotation);
            newObject.transform.SetParent(transform.parent, true);
            newObject.transform.localScale = replacementPrefab.transform.lossyScale;
            newObject.SetActive(true);   // el molde de la version rota esta apagado en la escena

            // encimada exacto sobre la caja: mismo centro de sus mallas
            newObject.transform.position += CentroMallas(gameObject) - CentroMallas(newObject);

            // direccion del golpe: de Velma hacia la caja (en el suelo XZ), las piezas salen hacia el lado opuesto a Velma
            Vector3 dirGolpe = transform.position - pos;
            dirGolpe.y = 0f;
            dirGolpe = dirGolpe.sqrMagnitude > 0.0001f ? dirGolpe.normalized : transform.forward;

            // las piezas estan kinematic (la caja rota se queda armada); el hachazo las suelta para que caigan
            foreach (Rigidbody pieza in newObject.GetComponentsInChildren<Rigidbody>())
            {
                pieza.isKinematic = false;

                // cada pieza: empuje en la direccion del golpe + un poco hacia afuera del centro (se abre) + un poco hacia arriba
                Vector3 haciaAfuera = (pieza.worldCenterOfMass - transform.position).normalized;
                Vector3 impulso = dirGolpe * hachazoFuerza
                                + haciaAfuera * hachazoDispersion
                                + Vector3.up * hachazoArriba;
                pieza.AddForce(impulso * Random.Range(0.8f, 1.2f), ForceMode.Impulse);
                pieza.AddTorque(Random.insideUnitSphere * hachazoGiro, ForceMode.Impulse);   // que giren al salir
            }
        }

        // destruye el model anterior
        Destroy(gameObject);

        return true;
    }

    void Update()
    {
        Mouse mouse = Mouse.current;
        if (mouse == null) return;

        Keyboard keyboard = Keyboard.current;
        if (keyboard == null) return;

        Vector2 pos = mouse.position.ReadValue();

        // Click: ¿el rayo desde la cámara pega en esta piedra?
        if (mouse.leftButton.isPressed && !arrastrando)   // solo la levanta una vez (si no, sube cada frame)
        {
            Ray rayo = mainCamera.ScreenPointToRay(pos);
            if (Physics.Raycast(rayo, out RaycastHit hit) && hit.transform == transform)
            {
                arrastrando = true;
                // Profundidad del objeto respecto a la cámara
                // zDistance = mainCamera.WorldToScreenPoint(transform.position).z;
                // Levantamos el objeto verticalmente en su lugar
                // transform.position =  transform.position + (Vector3.up * liftHeight);
                alturaArrastre = transform.position.y + liftHeight;
                rigdbody.isKinematic = true;   // en el aire: sin gravedad, la mueve el script
            }
        }

        // solo si estaba arrastrando: un click suelto no debe soltar/recalcular nada
        if (mouse.leftButton.wasReleasedThisFrame && arrastrando)
        {
            // cae encima de Velma: la atrapa ANTES de caer, asi la piedra la atraviesa y toca el suelo
            if (!velmaDebajo && !velma3D.atrapada && CubreAVelma())
            {
                velmaDebajo = true;
                velma3D.Atrapar(true);
                MostrarContorno(true);
            }

            velma3D.DisableControls(false); arrastrando = false; dropped = true;  // si esta atrapada sigue agachada
            rigdbody.isKinematic = false;      // suelta: la gravedad la hace caer
            destino.enabled = false;
        }

        // una vez en el aire el bloque se mueve con las teclas aswd y flechas
        // y velma se hace bolita. (desactiva los controlles de velma)
        if (arrastrando)
        {
            velma3D.DisableControls(true);  // velma ya no se controla, se agacha y espera
            transform.position = new Vector3( transform.position.x, alturaArrastre , transform.position.z);

            // le quitaron la piedra de encima: Velma recupera su collider
            // (sigue agachada mientras se arrastre la piedra y al soltarla ya se puede mover)
            if (velmaDebajo && !CubreAVelma())
            {
                velmaDebajo = false;
                velma3D.Atrapar(false);
                MostrarContorno(false);
            }

            // direccion de las teclas presionadas (se pueden combinar: diagonal)
            Vector3 dir = Vector3.zero;
            if (keyboard.upArrowKey.isPressed    || keyboard.wKey.isPressed) dir.z += 1;
            if (keyboard.downArrowKey.isPressed  || keyboard.sKey.isPressed) dir.z -= 1;
            if (keyboard.leftArrowKey.isPressed  || keyboard.aKey.isPressed) dir.x -= 1;
            if (keyboard.rightArrowKey.isPressed || keyboard.dKey.isPressed) dir.x += 1;

            if (dir == Vector3.zero)
            {
                tiempoPaso = 0f;   // sin teclas: el siguiente toque mueve la piedra de inmediato
            }
            else
            {
                // mientras la tecla siga presionada da un paso de rockStep cada rockRepeat segundos
                // (sigue avanzando por casillas completas del grid)
                tiempoPaso -= Time.deltaTime;
                if (tiempoPaso <= 0f)
                {
                    transform.position += dir * rockStep;
                    tiempoPaso = rockRepeat;
                }
            }

            // en el aire: marca en azul las casillas donde va a caer
            MostrarDestino();
            destino.enabled = true;
        }
    }

    void OnCollisionEnter(Collision collision)
    {
        // toco el piso u otra piedra/pared: se vuelve a congelar
        int piso = LayerMask.NameToLayer("Piso");
        int paredes = LayerMask.NameToLayer("Paredes");

        if (dropped == true && (collision.gameObject.layer == piso || collision.gameObject.layer == paredes))
        {
            dropped = false;

            // frena cualquier resto de caida antes de congelarla
            rigdbody.linearVelocity = Vector3.zero;
            rigdbody.angularVelocity = Vector3.zero;
            rigdbody.isKinematic = true;

            // al caer el choque la puede correr un poco: vuelve a quedar en medio de sus casillas
            Physics.SyncTransforms();
            Vector3 centro = rockCollider.bounds.center;
            transform.position += S9_Grid.Instancia.Alinear(centro) - centro;
            Physics.SyncTransforms();

            S9_Grid.Instancia.calculaGrid();
        }
    }
}
