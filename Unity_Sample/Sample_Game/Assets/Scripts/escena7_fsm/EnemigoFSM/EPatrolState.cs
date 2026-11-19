using UnityEngine;
using System.Collections.Generic;

// Checa que EPatrolstate herada de IEnemyState
// Entonces a FUERZA tiene que implmentar las funciones y propiedades que IEnemyState diga. 
public class EPatrolState: IEnemyState
{
    private readonly EnemigoCilindro enemy;
    private readonly EnemyStateMachine esm;
    private float tiempoRecalculo = 0f;
    // private float llego = false;
    private Vector2Int  patrullaGoal;
    private List<Vector2Int> camino;       // casillas por recorrer
    
    
    // constructor necesita la clase ligada al GameObject que esta en la escena. (EnemigoCilindro)
    public EPatrolState(EnemigoCilindro enemy, EnemyStateMachine esm)
    {
        this.enemy = enemy;
        this.esm = esm;
    }

    // empieza el chase a velma
    public void Enter()
    {
        Debug.Log("Estado: Comienza patrulla");
        BuscarCamino();
    }

    // usa un celda aleatoria para patrullar por el mapa y generar el camino
    public void BuscarCamino()
    {
        S7_Grid grid = S7_Grid.Instancia;
        patrullaGoal = grid.MundoACelda(enemy.transform.position);
        camino = grid.BuscarCamino(patrullaGoal,
                                   grid.GetRandomCelda());

        Debug.Log($"Estado: Patrullando celda {patrullaGoal}");
    }

    // revisa si el jugador esta dentro del cono de vision del enemigo (ver EnemigoCilindro.VeJugador)
    public void BuscarJugador()
    {
        // si ve al jugador cambia de estado
        if (enemy.VeJugador()) 
        {
            esm.ChangeState(new EPerseguirState(enemy, esm));
        }
    }

    // patrulla de un punto a otro del mapa mientras busca al jugador.
    public void Execute()
    {
        S7_Grid grid = S7_Grid.Instancia;

        BuscarJugador();  // revisa si el jugador esta en campo de visionI

        // sin camino: busca otra vez (llego a destino)
        if (camino == null || camino.Count == 0) { 
            BuscarCamino(); 
        }   

        // caminar hacia la PRIMERA casilla del camino (camino[0])
        // camino[0] el primer elemento de la lista de nodos a caminar
        Vector3 objetivo = grid.CeldaAMundo(camino[0]);
        objetivo.y = enemy.transform.position.y;   // la altura no cambia

        // Esto es para que el enemigo avance mirando al objetivo (camino[0])
        Vector3 haciaObjetivo = objetivo - enemy.transform.position;
        if (haciaObjetivo.sqrMagnitude > 0.0001f) enemy.transform.rotation = Quaternion.LookRotation(haciaObjetivo);  
        enemy.transform.position = Vector3.MoveTowards(enemy.transform.position, objetivo, enemy.chace_vel * Time.deltaTime);

        // va quitando el primer elemento de la lista al caminar.
        if (enemy.transform.position == objetivo) camino.RemoveAt(0);  
    }

    // temrina el chase
    public void Exit()
    {
    // constructor necesita la clase ligada al GameObject que esta en la escena.  (EnemigoCilindro)
        Debug.Log("Ya NO patrullo mas");
    }

    // muestra los rallos de buscqueda y el camino de patrulla
    public void DibujarGizmos()
    {
        S7_Grid grid = S7_Grid.Instancia;

        enemy.ConoVisionGizmo();

        if (camino == null || camino.Count == 0) return;
        for (int i = 0; i < camino.Count - 1; i++)
        {
            Gizmos.color = new Color(1, 0, 1, 0.9f);  // para patrullar el color es diferente
            Gizmos.DrawLine(
                grid.CeldaAMundo(camino[i]) + Vector3.up,
                grid.CeldaAMundo(camino[i + 1]) + Vector3.up
            );
        }
    }
}
