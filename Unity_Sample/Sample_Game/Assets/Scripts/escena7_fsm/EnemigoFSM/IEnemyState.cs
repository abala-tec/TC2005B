
// Esto es una interface, es una clase abstracta que define el "esqueleto" de otras clases que hereden de ella
// Si heradas de esta clase tienes que implmentar las funciones y la propiedades definidas dentro de la interface.  
// La vamos a usar para definir las funciones de cada estado del enemigo
public interface IEnemyState   
{
    void Enter();      // Entra al estado 
    void Execute();    // aqui lleva la logica del estado (Update() del dicho estado)
    void Exit();       // sale del estado 
    void DibujarGizmos();  // dibuja los gizmos
}
