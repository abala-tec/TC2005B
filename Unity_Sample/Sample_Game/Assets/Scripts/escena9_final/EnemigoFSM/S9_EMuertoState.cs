using UnityEngine;

// Enemigo Muerto
public class S9_EMuertoState : S9_IEnemyState
{
    private readonly S9_EnemigoCilindro enemy;
    private readonly S9_EnemyStateMachine esm;

    // constructor necesita la clase ligada al GameObject que esta en la escena. (S9_EnemigoCilindro)
    public S9_EMuertoState(S9_EnemigoCilindro enemy, S9_EnemyStateMachine esm)
    {
        this.enemy = enemy;
        this.esm = esm;
    }

    // empieza el estado de muerto
    public void Enter()
    {
        Debug.Log("Estado: Bien Muerto");

        // Solo se puede morir una vez
        if (enemy.muerto == false)
        {
            Transform t = enemy.transform;
            t.Rotate(t.right, -90f, Space.World); // rotar
            t.position += Vector3.down * (t.localScale.y - t.localScale.x / 2f);  // acostar sobre el suelo
            enemy.muerto = true;
        }
    }

    // Un zombie muerto no hace nada
    public void Execute()
    {
        return;
    }

    public void Exit()
    {
        return;
    }

    public void DibujarGizmos()
    {
        return;
    }
}
