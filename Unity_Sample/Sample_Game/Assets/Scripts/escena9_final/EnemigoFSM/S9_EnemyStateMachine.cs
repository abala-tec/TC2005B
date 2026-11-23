// Este clase nos permite tener control sobre el inicio, cambio y refresh de los estados. 
// es el nucleo del StateMachine de los enemigos
public class S9_EnemyStateMachine
{
    private S9_IEnemyState currentState;

    // para saber en que estado esta el enemigo (ej. EstadoActual is S9_EPerseguirState)
    public S9_IEnemyState EstadoActual => currentState;

    public void Initialize(S9_IEnemyState primerEstado)
    {
        currentState = primerEstado;
        currentState.Enter();
    }

    public void ChangeState(S9_IEnemyState nuevoEstado)
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
