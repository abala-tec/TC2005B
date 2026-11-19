using UnityEngine;
using System.Collections.Generic;

// Checa que S8_EPerseguirState herada de S8_IEnemyState
// Entonces a FUERZA tiene que implmentar las funciones y propiedades que S8_IEnemyState diga. 
public class S8_EPerseguirState : S8_IEnemyState
{
    private readonly S8_EnemigoCilindro enemy;
    private readonly S8_EnemyStateMachine esm;
    private float tiempoRecalculo = 0f;
    private List<Vector2Int> camino;       // casillas por recorrer
    private int versionGrid;    // para determinar si el grid se actualizo 

    // constructor necesita la clase ligada al GameObject que esta en la escena. (S8_EnemigoCilindro)
    public S8_EPerseguirState(S8_EnemigoCilindro enemy, S8_EnemyStateMachine esm)
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
        S8_Grid grid = S8_Grid.Instancia;

        // recalcular el camino cada chace_check_time (no en cada frame: es innecesario)
        tiempoRecalculo -= Time.deltaTime;
        if (tiempoRecalculo <= 0f || versionGrid != grid.version)
        {
            tiempoRecalculo = enemy.chace_check_time;
            versionGrid = grid.version;
            camino = grid.BuscarCamino(grid.MundoACelda(enemy.transform.position),
                                       grid.MundoACelda(enemy.jugador.position));
        }

        if (camino == null || camino.Count == 0 )
        {   // sin camino: cambia de estado a patrulla y termina
            esm.ChangeState(new S8_EPatrolState(enemy, esm));
            return;
        }

        // caminar hacia la PRIMERA casilla del camino (camino[0])
        Vector3 objetivo = grid.CeldaAMundo(camino[0]);
        objetivo.y = enemy.transform.position.y;       // la altura no cambia

        // avanza mirando hacia el objetivo (el cono mira hacia el objetivo)
        Vector3 haciaObjetivo = objetivo - enemy.transform.position;
        if (haciaObjetivo.sqrMagnitude > 0.0001f) enemy.transform.rotation = Quaternion.LookRotation(haciaObjetivo);

        enemy.transform.position = Vector3.MoveTowards(enemy.transform.position, objetivo, enemy.chace_vel * Time.deltaTime);
        if (enemy.transform.position == objetivo) camino.RemoveAt(0);
    }

    public void Exit()
    {
        Debug.Log("MVV: Me vale ve... Velma");
    }

    public void DibujarGizmos()
    {
        S8_Grid grid = S8_Grid.Instancia;
        if (grid == null) return;

        enemy.ConoVisionGizmo();

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
