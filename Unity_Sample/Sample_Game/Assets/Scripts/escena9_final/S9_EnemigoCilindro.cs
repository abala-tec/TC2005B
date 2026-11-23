using UnityEngine;

// La clase S9_EnemigoCilindro usa una maquina de estados para definir el behaviour del enemigo.
// Estados: Patrullar (BFS Random), Perseguir (BFS al jugador) y Muerto (collision off).
public class S9_EnemigoCilindro : MonoBehaviour
{
    public Transform jugador;                    // a que jugador se persigue (gameobject de velma)
    public float patrol_vel = 1.0f;              // velocidad normal (patrullar)
    public float chace_vel = 5.0f;               // velocidad de persecucion
    public float chace_check_time = 0.25f;       // cada cuantos segundos recalcula el camino (BFS)
    public float vision_rango = 8.0f;            // alcance del cono de vision
    public float vision_angulo = 90.0f;          // apertura total del cono (grados)
    public float golpe_angulo = 120.0f;          // que tan ancho es "enfrente" para golpear a Velma (180 = toda la mitad delantera)
    public int golpes_persiguiendo = 3;          // hachazos que necesita para morir si esta persiguiendo a Velma (patrullando muere de 1)
    public float retroceso_distancia = 1.0f;     // cuanto retrocede al recibir un hachazo (unidades = tiles)
    public float retroceso_tiempo = 0.25f;       // cuanto dura el retroceso (no camina ni golpea mientras retrocede)
    public bool muerto = false;                  // pa cuando que no se puera 2 pinches veces
    private int golpes_recibidos = 0;            // hachazos que lleva mientras persigue
    private Vector3 retroceso_vel;               // velocidad del retroceso (direccion lejos de Velma)
    private float retroceso_timer = 0f;          // > 0 = esta retrocediendo
    public SpriteRenderer sprender;               // sprite render para controlar la orientacion del sprite cuando el enemigo camina
    [HideInInspector] public Vector3 mirada;    // hacia donde mira el cono (independiente de la rotacion del transform/sprite)
    private S9_EnemyStateMachine esm;           // la estate machine que cambia los estados del enemigo (perseguir, patrullar, muerto)

    void Start()
    {
        sprender = GetComponent<SpriteRenderer>();

        // Rigidbody kinematic: se sigue moviendo por transform, pero Unity detecta bien sus choques con Velma
        Rigidbody rb = GetComponent<Rigidbody>();
        if (rb == null) rb = gameObject.AddComponent<Rigidbody>();
        rb.isKinematic = true;
        rb.useGravity = false;

        mirada = transform.forward;             // arranca mirando hacia donde apunta el objeto en la escena
        esm = new S9_EnemyStateMachine();
        esm.Initialize(new S9_EPatrolState(this, esm));   // Iniciamos en Patrullar
    }

    void Update()
    {
        // mientras retrocede no camina (la FSM espera)
        if (retroceso_timer > 0f)
        {
            Retroceder();
            return;
        }
        esm.Update();
    }

    // empuja al zombie lejos de Velma, sin atravesar paredes (revisa el grid)
    private void Retroceder()
    {
        retroceso_timer -= Time.deltaTime;

        Vector3 siguiente = transform.position + retroceso_vel * Time.deltaTime;
        S9_Grid grid = S9_Grid.Instancia;
        if (grid == null || grid.Libre(grid.MundoACelda(siguiente)))
        {
            transform.position = siguiente;
        }
        else
        {
            retroceso_timer = 0f;   // choco con una pared: deja de retroceder
        }
    }

    void OnDrawGizmos()
    {
        esm?.DibujarGizmos();
    }

    // Velma le dio un hachazo.
    // Patrullando (no la ha visto): muere de 1 golpe.
    // Persiguiendo: muere al llegar a golpes_persiguiendo.
    // Si no muere, retrocede un poco para darle chance a Velma del siguiente golpe.
    // Regresa true si el hachazo conecto (para el sonido).
    public bool RecibirHachazo(Vector3 origenHachazo)
    {
        if (muerto) return false;   // ya esta muerto: no vuelve a entrar al estado

        bool persiguiendo = esm.EstadoActual is S9_EPerseguirState;
        golpes_recibidos++;

        if (!persiguiendo || golpes_recibidos >= golpes_persiguiendo)
        {
            retroceso_timer = 0f;
            esm.ChangeState(new S9_EMuertoState(this, esm));
            return true;
        }

        // retroceso: lejos de Velma, en el suelo (XZ)
        Vector3 lejos = transform.position - origenHachazo;
        lejos.y = 0f;
        if (lejos.sqrMagnitude < 0.0001f) lejos = -mirada;   // Velma justo encima: retrocede hacia atras
        retroceso_vel = lejos.normalized * (retroceso_distancia / retroceso_tiempo);
        retroceso_timer = retroceso_tiempo;
        return true;
    }

    // apaga la fisica del zombie muerto: solo queda el sprite en el suelo
    public void DesactivarFisica()
    {
        foreach (Collider c in GetComponents<Collider>()) c.enabled = false;

        Rigidbody rb = GetComponent<Rigidbody>();
        if (rb != null) Destroy(rb);   // un Rigidbody no se puede "apagar": se quita
    }

    public bool GolpeVelma(Vector3 puntoContacto)
    {
        if (muerto) return false;   // ya esta muerto: no vuelve a entrar al estado
        if (retroceso_timer > 0f) return false;   // mientras retrocede no golpea

        return EnFrente(puntoContacto);   // golpea solo si Velma esta enfrente (dentro de golpe_angulo)
    }

    // Velma esta enfrente si el angulo entre la mirada y Velma es menor a la mitad de golpe_angulo
    private bool EnFrente(Vector3 posVelma)
    {
        Vector3 haciaVelma = posVelma - transform.position;
        haciaVelma.y = 0;
        return Vector3.Angle(mirada, haciaVelma) <= golpe_angulo / 2;
    }

    // cono de vision: el jugador se ve si esta dentro del rango, dentro del angulo frente al enemigo y sin pared en medio
    public bool VeJugador()
    {
        // si no hay jugador no hace nada
        if (jugador == null)
        {
            return false;
        }

        Vector3 origen = transform.position + Vector3.up;      // ojos del enemigo
        Vector3 dir = jugador.position + Vector3.up - origen;  // direcion de los ojos del enemigo a velma
        Vector3 plano = new Vector3(dir.x, 0, dir.z);          // lo mismo que direccion pero en el suelo para detectar el rango

        // checa si velma esta dentro del rango de vision
        if (dir.magnitude > vision_rango || Vector3.Angle(mirada, plano) > vision_angulo / 2)
        {
            return false;
        }

        // saca un rayo de enemigo a velma, si el rayo pega algo que no es el jugador, hay una pared en medio
        return !Physics.Raycast(origen, dir.normalized, out RaycastHit hit, dir.magnitude) || hit.transform.IsChildOf(jugador);
    }

    // dibuja el cono (verde = nada, rojo = jugador detectado)
    public void ConoVisionGizmo()
    {
        Gizmos.color = VeJugador() ? Color.red : Color.green;
        Vector3 o = transform.position + Vector3.up;
        Vector3 izq = o + Quaternion.AngleAxis(-vision_angulo / 2, Vector3.up) * mirada * vision_rango;
        Vector3 der = o + Quaternion.AngleAxis(vision_angulo / 2, Vector3.up) * mirada * vision_rango;
        Gizmos.DrawLine(o, izq);
        Gizmos.DrawLine(izq, der);
        Gizmos.DrawLine(der, o);
    }
}
