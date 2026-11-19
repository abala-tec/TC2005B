using UnityEngine;
using System.Collections.Generic;

// Checa que EPerseguirState herada de IEnemyState
// Entonces a FUERZA tiene que implmentar las funciones y propiedades que IEnemyState diga. 
public class EPerseguirState: IEnemyState
{
    private readonly EnemigoCilindro enemy;
    private readonly EnemyStateMachine esm;
    private float tiempoRecalculo = 0f;
    private List<Vector2Int> camino;       // casillas por recorrer
    
    
    // constructor necesita la clase ligada al GameObject que esta en la escena. (EnemigoCilindro)
    public EPerseguirState(EnemigoCilindro enemy, EnemyStateMachine esm)
    {
        this.enemy = enemy;
        this.esm = esm;
    }

    // empieza el chase a velma
    public void Enter()
    {
        Debug.Log("Estado: Perseguir a Velma");
    }
    
    // Aqui va la logica de perseguir a Velma usando BFS
    public void Execute()
    {
        S7_Grid grid = S7_Grid.Instancia;

        // recalcular el camino cada 0.25 s (no en cada frame: es innecesario)
        tiempoRecalculo -= Time.deltaTime;
        if (tiempoRecalculo <= 0f)
        {
            tiempoRecalculo = enemy.chace_check_time;
            camino = grid.BuscarCamino(grid.MundoACelda(enemy.transform.position),
                                       grid.MundoACelda(enemy.jugador.position));
        }

        // UnityEngine.Debug.Log(camino);
        if (camino == null || camino.Count == 0) 
        { // sin camino: cambia de estado a patrol y termina
            esm.ChangeState(new EPatrolState(enemy, esm));
            return;   
        }
        
        // caminar hacia la PRIMERA casilla del camino (camino[0])
        Vector3 objetivo = grid.CeldaAMundo(camino[0]);
        objetivo.y = enemy.transform.position.y;       // la altura no cambia   
        
        // avanza mirando hacia el objetivo. (el cono mira hacia el objetivo)
        Vector3 haciaObjetivo = objetivo - enemy.transform.position;
        if (haciaObjetivo.sqrMagnitude > 0.0001f) enemy.transform.rotation = Quaternion.LookRotation(haciaObjetivo);  

        enemy.transform.position = Vector3.MoveTowards(enemy.transform.position, objetivo, enemy.chace_vel * Time.deltaTime);
        if (enemy.transform.position == objetivo) camino.RemoveAt(0);  
    }

    // temrina el chase
    public void Exit()
    {
    // constructor necesita la clase ligada al GameObject que esta en la escena.  (EnemigoCilindro)
        Debug.Log("MVV: Me vale ve... Velma");
    }

    public void DibujarGizmos()
    {
        S7_Grid grid = S7_Grid.Instancia;

        if (camino == null || camino.Count == 0) return;
        for (int i = 0; i < camino.Count - 1; i++)
        {
            Gizmos.color = new Color(1, 1, 0, 0.9f);
            Gizmos.DrawLine(
                grid.CeldaAMundo(camino[i]) + Vector3.up,
                grid.CeldaAMundo(camino[i + 1]) + Vector3.up
            );
        }
    }
}
