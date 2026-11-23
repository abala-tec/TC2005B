using UnityEngine;

// La clase S8_EnemigoCilindro usa una maquina de estados para definir el behaviour del enemigo.
// Estados: Patrullar (BFS Random), Perseguir (BFS al jugador) y Muerto (collision off).
public class S8_EnemigoCilindro : MonoBehaviour
{
    public Transform jugador;                    // a que jugador se persigue (gameobject de velma)
    public float chace_vel = 5.0f;               // velocidad de persecucion
    public float chace_check_time = 0.25f;       // cada cuantos segundos recalcula el camino (BFS)
    public float vision_rango = 8.0f;            // alcance del cono de vision
    public float vision_angulo = 90.0f;          // apertura total del cono (grados)
    public float golpe_angulo = 120.0f;          // que tan ancho es "enfrente" para golpear a Velma (180 = toda la mitad delantera)
    public int golpes_persiguiendo = 3;          // hachazos que necesita para morir si esta persiguiendo a Velma (patrullando muere de 1)
    public float retroceso_distancia = 1.0f;     // cuanto retrocede al recibir un hachazo (unidades = tiles)
    public float retroceso_tiempo = 0.25f;       // cuanto dura el retroceso (no camina ni golpea mientras retrocede)
    public bool muerto = false;                  // pa cuando se muera el
    private int golpes_recibidos = 0;            // hachazos que lleva
    private Vector3 retroceso_vel;               // velocidad del retroceso (direccion lejos de Velma)
    private float retroceso_timer = 0f;          // > 0 = esta retrocediendo
    private S8_EnemyStateMachine esm;

    void Start()
    {
        // Rigidbody kinematic: se sigue moviendo por transform, pero Unity detecta bien sus choques con Velma
        Rigidbody rb = GetComponent<Rigidbody>();
        if (rb == null) rb = gameObject.AddComponent<Rigidbody>();
        rb.isKinematic = true;
        rb.useGravity = false;

        esm = new S8_EnemyStateMachine();
        esm.Initialize(new S8_EPatrolState(this, esm));   // Iniciamos en Patrullar
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

    // el enemigo retrocede cuando lo atacan, revisa si por el empuje entra en colision con una pared
    private void Retroceder()
    {
        retroceso_timer -= Time.deltaTime;

        Vector3 siguiente = transform.position + retroceso_vel * Time.deltaTime;
        S8_Grid grid = S8_Grid.Instancia;
        if (grid == null || grid.Libre(grid.MundoACelda(siguiente)))
        {
            transform.position = siguiente;
        }
        else
        {
            retroceso_timer = 0f;   // choco con una pared: deja de retroceder
        }
    }

    // Esta es la funcion de unity (del gameobject) para dibujar gizmos de debugeo.
    // manda a llamar a otra funcion, que es usada por los estados de enemigo para dibujar los gizmos
    void OnDrawGizmos()
    {
        esm?.DibujarGizmos();
    }

    // Velma le dio un hachazo al enemigo (el script del jugador manda a llamar esta funcion)
    // Si esta Patrullando (no la ha visto): muere de 1 golpe.
    // si la esta Persiguiendo: muere al llegar a golpes_persiguiendo.
    // Si no muere, retrocede un poco para darle chance a Velma del siguiente golpe. (ver Retroceder())
    // Regresa true si el hachazo conecto (para el sonido).
    public bool RecibirHachazo(Vector3 origenHachazo)
    {
        if (muerto) return false;   // ya esta muerto: no vuelve a entrar al estado

        bool persiguiendo = esm.EstadoActual is S8_EPerseguirState;
        golpes_recibidos++;

        if (!persiguiendo || golpes_recibidos >= golpes_persiguiendo)
        {
            retroceso_timer = 0f;
            esm.ChangeState(new S8_EMuertoState(this, esm));
            return true;
        }

        // retroceso: lejos de Velma, en el suelo (XZ)
        Vector3 lejos = transform.position - origenHachazo;
        lejos.y = 0f;
        if (lejos.sqrMagnitude < 0.0001f) lejos = -transform.forward;   // Velma justo encima: retrocede hacia atras
        retroceso_vel = lejos.normalized * (retroceso_distancia / retroceso_tiempo);
        retroceso_timer = retroceso_tiempo;
        return true;
    }

    // apaga la fisica del zombie muerto: solo queda el cuerpo en el suelo (sprite)
    public void DesactivarFisica()
    {
        foreach (Collider c in GetComponents<Collider>()) c.enabled = false;

        Rigidbody rb = GetComponent<Rigidbody>();
        if (rb != null) Destroy(rb);   // un Rigidbody no se puede "apagar": se quita
    }

    public bool GolpeVelma(Vector3 puntoContacto)
    {
        if (muerto) return false;                 // ya esta muerto: no golpea
        if (retroceso_timer > 0f) return false;   // mientras retrocede no golpea

        return EnFrente(puntoContacto);   // golpea solo si Velma esta enfrente (dentro de golpe_angulo)
    }

    // Velma esta enfrente si el angulo entre el frente del zombie y Velma es menor a la mitad de golpe_angulo
    private bool EnFrente(Vector3 posVelma)
    {
        Vector3 haciaVelma = posVelma - transform.position;
        haciaVelma.y = 0;
        return Vector3.Angle(transform.forward, haciaVelma) <= golpe_angulo / 2;
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
        if (dir.magnitude > vision_rango || Vector3.Angle(transform.forward, plano) > vision_angulo / 2)
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
        Vector3 izq = o + Quaternion.AngleAxis(-vision_angulo / 2, Vector3.up) * transform.forward * vision_rango;
        Vector3 der = o + Quaternion.AngleAxis(vision_angulo / 2, Vector3.up) * transform.forward * vision_rango;
        Gizmos.DrawLine(o, izq);
        Gizmos.DrawLine(izq, der);
        Gizmos.DrawLine(der, o);
    }
}
