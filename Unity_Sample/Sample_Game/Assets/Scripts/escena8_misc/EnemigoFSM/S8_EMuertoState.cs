using UnityEngine;

// Enemigo Muerto
public class S8_EMuertoState : S8_IEnemyState
{
    private readonly S8_EnemigoCilindro enemy;
    private readonly S8_EnemyStateMachine esm;

    // constructor necesita la clase ligada al GameObject que esta en la escena. (S8_EnemigoCilindro)
    public S8_EMuertoState(S8_EnemigoCilindro enemy, S8_EnemyStateMachine esm)
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
            enemy.DesactivarFisica();   // sin collider ni rigidbody: solo queda el cuerpo en el suelo
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
