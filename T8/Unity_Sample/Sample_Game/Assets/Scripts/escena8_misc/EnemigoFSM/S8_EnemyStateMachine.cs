// Este clase nos permite tener control sobre el inicio, cambio y refresh de los estados. 
// es el nucleo del StateMachine de los enemigos
public class S8_EnemyStateMachine
{
    private S8_IEnemyState currentState;

    public void Initialize(S8_IEnemyState primerEstado)
    {
        currentState = primerEstado;
        currentState.Enter();
    }

    public void ChangeState(S8_IEnemyState nuevoEstado)
    {
        currentState.Exit();
        currentState = nuevoEstado;
        currentState.Enter();
    }

    public void Update()
    {
        currentState?.Execute();
    }

    public void DibujarGizmos()
    {
        currentState?.DibujarGizmos();
    }
}
