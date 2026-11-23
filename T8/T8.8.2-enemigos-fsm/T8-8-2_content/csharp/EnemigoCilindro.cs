using UnityEngine;

// La clase EnemigoCilindro se redefiniio completamente para usar una machina de estados (anterioremente solo Perseguia con BFS)
// para definir el behaviour del este enemigo. en Patrullar (BSF Random), Muerto (collsion off), Perseguir (BSF al personaje)
public class EnemigoCilindro : MonoBehaviour
{
    public Transform jugador;             // a que jugador se persigue (gameobject de velma)
    public float chace_vel = 5.0f;    // velocidad de persecucion
    public float chace_check_time = 0.25f;       // cada cuántos segundos recalcula el camino (BFS)
    public float vision_rango = 8.0f;    // alcance del cono de vision
    public float vision_angulo = 90.0f;  // apertura total del cono (grados)
    public int golpes_persiguiendo = 3;          // hachazos que necesita para morir si esta persiguiendo a Velma (patrullando muere de 1)
    public float retroceso_distancia = 1.0f;     // cuanto retrocede al recibir un hachazo (unidades = tiles)
    public float retroceso_tiempo = 0.25f;       // cuanto dura el retroceso (no camina mientras retrocede)
    public bool muerto = false;  // pa cuando se muera el
    private int golpes_recibidos = 0;            // hachazos que lleva
    private Vector3 retroceso_vel;               // velocidad del retroceso (direccion lejos de Velma)
    private float retroceso_timer = 0f;          // > 0 = esta retrocediendo
    private EnemyStateMachine esm;

    void Start()
    {
        // Rigidbody kinematic: se sigue moviendo por transform, pero Unity detecta bien sus choques con Velma
        Rigidbody rb = GetComponent<Rigidbody>();
        if (rb == null) rb = gameObject.AddComponent<Rigidbody>();
        rb.isKinematic = true;
        rb.useGravity = false;

        esm = new EnemyStateMachine();
        esm.Initialize(new EPatrolState(this, esm));   // Iniciamos en Patrullar
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

    void OnDrawGizmos()
    {
        esm?.DibujarGizmos();
    }

    // Velma le dio un hachazo.
    // Patrullando (no la ha visto): muere de 1 golpe.
    // Persiguiendo: muere al llegar a golpes_persiguiendo.
    // Si no muere, retrocede un poco para darle chance a Velma del siguiente golpe.
    // Regresa true si el hachazo conecto.
    public bool RecibirHachazo(Vector3 origenHachazo)
    {
        if (muerto) return false;   // ya esta muerto: no vuelve a entrar al estado

        bool persiguiendo = esm.EstadoActual is EPerseguirState;
        golpes_recibidos++;

        if (!persiguiendo || golpes_recibidos >= golpes_persiguiendo)
        {
            retroceso_timer = 0f;
            esm.ChangeState(new EMuertoState(this, esm));
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

    // empuja al zombie lejos de Velma, sin atravesar paredes (revisa el grid)
    private void Retroceder()
    {
        retroceso_timer -= Time.deltaTime;

        Vector3 siguiente = transform.position + retroceso_vel * Time.deltaTime;
        S7_Grid grid = S7_Grid.Instancia;
        if (grid == null || grid.Libre(grid.MundoACelda(siguiente)))
        {
            transform.position = siguiente;
        }
        else
        {
            retroceso_timer = 0f;   // choco con una pared: deja de retroceder
        }
    }

    // apaga la fisica del zombie muerto: solo queda el cuerpo en el suelo
    public void DesactivarFisica()
    {
        foreach (Collider c in GetComponents<Collider>()) c.enabled = false;

        Rigidbody rb = GetComponent<Rigidbody>();
        if (rb != null) Destroy(rb);   // un Rigidbody no se puede "apagar": se quita
    }

    // cono de vision: el jugador se ve si esta dentro del rango, dentro del angulo frente al enemigo y sin pared en medio
    public bool VeJugador()
    {
        // si no hay jugador no hace nada
        if (jugador == null) {
            return false;
        }
        Vector3 origen = transform.position + Vector3.up;   // ojos del enemigo
        Vector3 dir = jugador.position + Vector3.up - origen;  // direcion de los ojos del enemigo a velma 
        Vector3 plano = new Vector3(dir.x, 0, dir.z);  // lo mismo que direccion pero en en suelo para detectar el rango

        // checa si velma esta dentro del rango de vision
        if (dir.magnitude > vision_rango || Vector3.Angle(transform.forward, plano) > vision_angulo / 2) 
        {
            return false;  
        }

        // saca un rayo de enemego a velma, si el rayo pega algo que no es el jugador, hay una pared en medio
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
