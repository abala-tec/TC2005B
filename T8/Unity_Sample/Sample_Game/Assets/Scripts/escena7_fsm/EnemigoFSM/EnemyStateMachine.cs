
// Este clase nos permite tener control sobre el inicio, cambio y refresh de los estados. 
// es el nucleo del StateMachine de los enemigos
public class EnemyStateMachine
{
    private IEnemyState currentState;
    public void Initialize(IEnemyState primerEstado)
    {
        currentState = primerEstado;
        currentState.Enter();
    }
    public void ChangeState(IEnemyState nuevoEstado)
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
        currentState.DibujarGizmos();
    }
}