using UnityEngine;
using System.Collections.Generic;
using UnityEditor.Callbacks;
using UnityEngine.Assertions.Must;

// Enemigo Muerto
public class EMuertoState: IEnemyState
{
    private readonly EnemigoCilindro enemy;
    private readonly EnemyStateMachine esm;
    
    // constructor necesita la clase ligada al GameObject que esta en la escena. (EnemigoCilindro)
    public EMuertoState(EnemigoCilindro enemy, EnemyStateMachine esm)
    {
        this.enemy = enemy;
        this.esm = esm;
    }

    // empieza el chase a velma
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
