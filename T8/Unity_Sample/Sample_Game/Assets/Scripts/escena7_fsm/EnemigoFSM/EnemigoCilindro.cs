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
    public bool muerto = false;  // pa cuando se muera el
    private EnemyStateMachine esm;

    void Start()
    {
        esm = new EnemyStateMachine();
        esm.Initialize(new EPatrolState(this, esm));   // Iniciamos en Patrullar
    } 
    void Update()
    {
        esm.Update();
    }
    
    void OnDrawGizmos()
    {
        esm?.DibujarGizmos();
    }

    // detecta de donde vino la patada si no la recibe al frente, se muere
    public void RecibirPatada(Vector3 origenPatada)
    {
        // patada fuera del cono de vision mata al enemigo
        Vector3 haciaVelma = origenPatada - transform.position;
        haciaVelma.y = 0;
        if (Vector3.Angle(transform.forward, haciaVelma) > vision_angulo / 2) 
            esm.Initialize(new EMuertoState(this, esm));
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
