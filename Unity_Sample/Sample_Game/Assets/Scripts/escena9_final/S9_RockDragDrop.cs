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
    public float rockSize = 2.0f;    // tamano de la piedra (lado mas largo en X/Z), lo aplica S9_Manzana al iniciar
    public float rockRepeat = 0.15f; // segundos entre cada paso mientras la tecla siga presionada
    private float tiempoPaso = 0f;   // cuenta regresiva para el siguiente paso
    [SerializeField] public GameObject player;
    private S9_VelmaWalk_3D velma3D;  // gameobject dle jugador para bloquear sus controles
    private bool dropped = false; // cuando la piedra cae (para recalcular el grid)
    private Rigidbody rigdbody;
    private Collider rockCollider;
    private bool velmaDebajo = false; // true = esta piedra tiene a Velma atrapada debajo
    public Material outlineMaterial;  // RockOutline_Rojo: contorno palpitante cuando Velma esta debajo
    private Material outlineInstancia; // copia propia (cada piedra tiene su centro)
    private Renderer rockRenderer;

    void Start()
    {
        mainCamera = Camera.main;  // objeto de la camara del juego
        velma3D = player.GetComponent<S9_VelmaWalk_3D>();
        rigdbody = GetComponent<Rigidbody>();
        rockCollider = GetComponent<Collider>();
        rockRenderer = GetComponentInChildren<Renderer>();
        if (outlineMaterial != null) outlineInstancia = new Material(outlineMaterial);
    }

    // prende/apaga el contorno: agrega o quita el material extra del renderer de la piedra
    // (un material extra vuelve a dibujar la misma malla con el shader del contorno)
    private void MostrarContorno(bool value)
    {
        if (outlineInstancia == null || rockRenderer == null) return;

        var mats = new System.Collections.Generic.List<Material>(rockRenderer.sharedMaterials);
        mats.Remove(outlineInstancia);
        if (value) mats.Add(outlineInstancia);
        rockRenderer.sharedMaterials = mats.ToArray();
    }

    void LateUpdate()
    {
        // el shader agranda la malla desde su centro: se lo pasamos (cambia mientras la piedra cae)
        if (velmaDebajo && outlineInstancia != null)
            outlineInstancia.SetVector("_Center", rockRenderer.bounds.center);
    }

    void OnDestroy()
    {
        if (outlineInstancia != null) Destroy(outlineInstancia);
    }

    // la piedra esta encima de Velma si la posicion de Velma (en X,Z) cae dentro de la huella de la piedra
    private bool CubreAVelma()
    {
        Bounds b = rockCollider.bounds;
        Vector3 p = player.transform.position;
        return p.x >= b.min.x && p.x <= b.max.x && p.z >= b.min.z && p.z <= b.max.z;
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

            S9_Grid.Instancia.calculaGrid();
        }
    }
}
