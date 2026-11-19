using UnityEngine;
using System.Collections.Generic;

// Checa que S8_EPatrolState herada de S8_IEnemyState
// Entonces a FUERZA tiene que implmentar las funciones y propiedades que S8_IEnemyState diga. 
public class S8_EPatrolState : S8_IEnemyState
{
    private readonly S8_EnemigoCilindro enemy;
    private readonly S8_EnemyStateMachine esm;
    private Vector2Int patrullaGoal;
    private List<Vector2Int> camino;       // casillas por recorrer
     private int versionGrid;              // para saber si el grid se actualizo

    // constructor necesita la clase ligada al GameObject que esta en la escena. (S8_EnemigoCilindro)
    public S8_EPatrolState(S8_EnemigoCilindro enemy, S8_EnemyStateMachine esm)
    {
        this.enemy = enemy;
        this.esm = esm;
    }

    // empieza el estado de patrulla
    public void Enter()
    {
        Debug.Log("Estado: Comienza patrulla");
        BuscarCamino();
    }

    // usa una celda aleatoria para patrullar por el mapa y generar el camino
    public void BuscarCamino()
    {
        S8_Grid grid = S8_Grid.Instancia;
        patrullaGoal = grid.MundoACelda(enemy.transform.position);
        camino = grid.BuscarCamino(patrullaGoal, grid.GetRandomCelda());

        versionGrid = grid.version;
        Debug.Log($"Estado: Patrullando celda {patrullaGoal} Grid version: {versionGrid}");
    }

    // revisa si el jugador esta dentro del cono de vision del enemigo (ver S8_EnemigoCilindro.VeJugador)
    public void BuscarJugador()
    {
        // si ve al jugador cambia de estado
        if (enemy.VeJugador())
        {
            esm.ChangeState(new S8_EPerseguirState(enemy, esm));
        }
    }

    // patrulla de un punto a otro del mapa mientras busca al jugador.
    public void Execute()
    {
        S8_Grid grid = S8_Grid.Instancia;

        BuscarJugador();  // revisa si el jugador esta en campo de vision

        // sin camino: busca otra vez (llego a destino)
        if (camino == null || camino.Count == 0 || versionGrid != grid.version)
        {
            BuscarCamino();
            if (camino == null || camino.Count == 0) return;  // no hay ruta disponible
        }

        // caminar hacia la PRIMERA casilla del camino (camino[0])
        Vector3 objetivo = grid.CeldaAMundo(camino[0]);
        objetivo.y = enemy.transform.position.y;   // la altura no cambia

        // avanza mirando al objetivo (el cono mira hacia el objetivo)
        Vector3 haciaObjetivo = objetivo - enemy.transform.position;
        if (haciaObjetivo.sqrMagnitude > 0.0001f) enemy.transform.rotation = Quaternion.LookRotation(haciaObjetivo);
        enemy.transform.position = Vector3.MoveTowards(enemy.transform.position, objetivo, enemy.chace_vel * Time.deltaTime);

        // va quitando el primer elemento de la lista al caminar.
        if (enemy.transform.position == objetivo) camino.RemoveAt(0);
    }

    public void Exit()
    {
        Debug.Log("Ya NO patrullo mas");
    }

    // muestra los rayos de busqueda y el camino de patrulla
    public void DibujarGizmos()
    {
        S8_Grid grid = S8_Grid.Instancia;
        if (grid == null) return;

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
