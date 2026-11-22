using UnityEngine;
using System.Collections.Generic;

// Checa que S9_EPerseguirState herada de S9_IEnemyState
// Entonces a FUERZA tiene que implmentar las funciones y propiedades que S9_IEnemyState diga. 
public class S9_EPerseguirState : S9_IEnemyState
{
    private readonly S9_EnemigoCilindro enemy;
    private readonly S9_EnemyStateMachine esm;
    private float tiempoRecalculo = 0f;
    private List<Vector2Int> camino;       // casillas por recorrer
    private int versionGrid;    // para determinar si el grid se actualizo 

    // constructor necesita la clase ligada al GameObject que esta en la escena. (S9_EnemigoCilindro)
    public S9_EPerseguirState(S9_EnemigoCilindro enemy, S9_EnemyStateMachine esm)
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
        S9_Grid grid = S9_Grid.Instancia;

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
            esm.ChangeState(new S9_EPatrolState(enemy, esm));
            return;
        }

        // caminar hacia la PRIMERA casilla del camino (camino[0])
        Vector3 objetivo = grid.CeldaAMundo(camino[0]);
        objetivo.y = enemy.transform.position.y;       // la altura no cambia

        // avanza mirando hacia el objetivo (el cono mira hacia el objetivo)
        Vector3 haciaObjetivo = objetivo - enemy.transform.position;
        // if (haciaObjetivo.sqrMagnitude > 0.0001f) enemy.transform.rotation = Quaternion.LookRotation(haciaObjetivo);

        // rota el sprite dependiendo de hacia donde va al zombie
        float orientacion_h =  enemy.transform.position.x - objetivo.x;
        enemy.sprender.flipX = (orientacion_h < 0) ?  false : true;  

        enemy.transform.position = Vector3.MoveTowards(enemy.transform.position, objetivo, enemy.chace_vel * Time.deltaTime);
        if (enemy.transform.position == objetivo) camino.RemoveAt(0);
    }

    public void Exit()
    {
        Debug.Log("MVV: Me vale ve... Velma");
    }

    public void DibujarGizmos()
    {
        S9_Grid grid = S9_Grid.Instancia;
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
