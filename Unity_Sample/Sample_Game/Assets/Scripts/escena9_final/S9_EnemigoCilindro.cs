using UnityEngine;
using UnityPipeline.Microsoft.CodeAnalysis.Operations;

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
    public bool muerto = false;                  // pa cuando que no se puera 2 pinches veces
    public SpriteRenderer sprender;               // sprite render para controlar la orientacion del sprite cuando el enemigo camina
    [HideInInspector] public Vector3 mirada;    // hacia donde mira el cono (independiente de la rotacion del transform/sprite)
    private S9_EnemyStateMachine esm;           // la estate machine que cambia los estados del enemigo (perseguir, patrullar, muerto)

    void Start()
    {
        sprender = GetComponent<SpriteRenderer>(); 
        mirada = transform.forward;             // arranca mirando hacia donde apunta el objeto en la escena
        esm = new S9_EnemyStateMachine();
        esm.Initialize(new S9_EPatrolState(this, esm));   // Iniciamos en Patrullar
    }

    void Update()
    {
        esm.Update();
    }

    void OnDrawGizmos()
    {
        esm?.DibujarGizmos();
    }

    // detecta de donde vino la patada: solo se muere si se la dan por detras
    public bool RecibirPatada(Vector3 origenPatada)
    {
        if (muerto) return false;   // ya esta muerto: no vuelve a entrar al estado

        if (PorDetras(origenPatada))
        {
            esm.Initialize(new S9_EMuertoState(this, esm));
            return true;
        }
        return false;
    }

    public bool GolpeVelma(Vector3 puntoContacto)
    {
        if (muerto) return false;   // ya esta muerto: no vuelve a entrar al estado

        return !PorDetras(puntoContacto);   // golpea solo si Velma esta enfrente (la mitad hacia donde mira)
    }

    // la patada cuenta solo si Velma esta detras del enemigo (en la mitad opuesta a donde mira)
    private bool PorDetras(Vector3 origenPatada)
    {
        Vector3 haciaVelma = origenPatada - transform.position;
        haciaVelma.y = 0;
        return Vector3.Dot(mirada, haciaVelma) < 0;   // negativo = esta a sus espaldas
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
