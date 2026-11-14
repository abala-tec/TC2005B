using Unity.VisualScripting;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.UIElements;   // el proyecto solo usa el nuevo Input System

[RequireComponent(typeof(Collider))]   // sin collider el raycast no detecta la piedra
[RequireComponent(typeof(Rigidbody))]
public class S8_RockDragDrop : MonoBehaviour
{
    private Camera mainCamera;
    private float liftHeight = 2.0f; // distancia del piso al suelo, cuando se alza la piedra
    private float alturaArrastre;         // Distancia de profundidad desde la cámara
    private bool arrastrando;  // cuando la piedra se esta moviendo (flag)
    public float rockStep = 2.0f;    // cuanto se mueve la piedra por el grid
    [SerializeField] public GameObject player;
    private S8_VelmaWalk_3D velma3D;  // gameobject dle jugador para bloquear sus controles
    private bool dropped = false; // cuando la piedra cae (para recalcular el grid)
    private Rigidbody rigdbody;

    void Start()
    {
        mainCamera = Camera.main;  // objeto de la camara del juego
        velma3D = player.GetComponent<S8_VelmaWalk_3D>();
        rigdbody = GetComponent<Rigidbody>();
    }

    void Update()
    {
        Mouse mouse = Mouse.current;
        if (mouse == null) return;

        Keyboard keyboard = Keyboard.current;
        if (keyboard == null) return;

        Vector2 pos = mouse.position.ReadValue();

        // Click: ¿el rayo desde la cámara pega en esta piedra?
        if (mouse.leftButton.wasPressedThisFrame)
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
            velma3D.DisableControls(false); arrastrando = false; dropped = true;
            rigdbody.isKinematic = false;      // suelta: la gravedad la hace caer
        }

        // una vez en el aire el bloque se mueve con las teclas aswd y flechas
        // y velma se hace bolita. (desactiva los controlles de velma)
        if (arrastrando)
        {
            velma3D.DisableControls(true);  // velma ya no se controla, se agacha y espera
            transform.position = new Vector3( transform.position.x, alturaArrastre , transform.position.z);

            if (arrastrando && (keyboard.upArrowKey.wasPressedThisFrame||keyboard.wKey.wasPressedThisFrame))
            {
                transform.position = new Vector3(transform.position.x, alturaArrastre, transform.position.z+rockStep);
            }
            if (arrastrando && (keyboard.downArrowKey.wasPressedThisFrame||keyboard.sKey.wasPressedThisFrame))
            {
                transform.position = new Vector3(transform.position.x, alturaArrastre, transform.position.z-rockStep);
            }

            if (arrastrando && (keyboard.leftArrowKey.wasPressedThisFrame||keyboard.aKey.wasPressedThisFrame))
            {
                transform.position = new Vector3(transform.position.x-rockStep, alturaArrastre, transform.position.z);
            }
            if (arrastrando && (keyboard.rightArrowKey.wasPressedThisFrame||keyboard.dKey.wasPressedThisFrame))
            {
                transform.position = new Vector3(transform.position.x+rockStep, alturaArrastre, transform.position.z);
            }
        }
    }

    void OnCollisionEnter(Collision collision)
    {
        if (dropped == true && collision.gameObject.layer == LayerMask.NameToLayer("Piso")) // toco el piso
        {
            dropped = false;
            S8_Grid.Instancia.calculaGrid();
        }
    }
}
