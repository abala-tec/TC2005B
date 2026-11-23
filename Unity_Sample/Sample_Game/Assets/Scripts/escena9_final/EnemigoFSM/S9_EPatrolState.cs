using UnityEngine;
using System.Collections.Generic;

// Checa que S9_EPatrolState herada de S9_IEnemyState
// Entonces a FUERZA tiene que implmentar las funciones y propiedades que S9_IEnemyState diga. 
public class S9_EPatrolState : S9_IEnemyState
{
    private readonly S9_EnemigoCilindro enemy;
    private readonly S9_EnemyStateMachine esm;
    private Vector2Int patrullaGoal;
    private List<Vector2Int> camino;       // casillas por recorrer
    private int versionGrid;              // para saber si el grid se actualizo

    // constructor necesita la clase ligada al GameObject que esta en la escena. (S9_EnemigoCilindro)
    public S9_EPatrolState(S9_EnemigoCilindro enemy, S9_EnemyStateMachine esm)
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
        S9_Grid grid = S9_Grid.Instancia;
        patrullaGoal = grid.MundoACelda(enemy.transform.position);
        camino = grid.BuscarCamino(patrullaGoal, grid.GetRandomCelda());

        versionGrid = grid.version;
        Debug.Log($"Estado: Patrullando celda {patrullaGoal} Grid version: {versionGrid}");
    }

    // revisa si el jugador esta dentro del cono de vision del enemigo (ver S9_EnemigoCilindro.VeJugador)
    public void BuscarJugador()
    {
        // si ve al jugador cambia de estado
        if (enemy.VeJugador())
        {
            esm.ChangeState(new S9_EPerseguirState(enemy, esm));
        }
    }

    // patrulla de un punto a otro del mapa mientras busca al jugador.
    public void Execute()
    {
        S9_Grid grid = S9_Grid.Instancia;

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
        // solo gira el cono (enemy.mirada), no el transform: asi el sprite no rota, solo se voltea con flipX
        if (haciaObjetivo.sqrMagnitude > 0.0001f) enemy.mirada = haciaObjetivo.normalized;

        // rota el sprite dependiendo de hacia donde va al zombie
        float orientacion_h =  enemy.transform.position.x - objetivo.x;
        // solo voltea si de verdad se mueve en X (si camina solo en Z conserva hacia donde miraba)
        if (Mathf.Abs(orientacion_h) > 0.01f) enemy.sprender.flipX = orientacion_h > 0;

        enemy.transform.position = Vector3.MoveTowards(enemy.transform.position, objetivo, enemy.patrol_vel * Time.deltaTime);

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
        S9_Grid grid = S9_Grid.Instancia;
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
