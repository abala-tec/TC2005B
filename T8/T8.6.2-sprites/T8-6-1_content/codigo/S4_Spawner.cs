using UnityEngine;

public class S4_Spawner : MonoBehaviour
{
    // GameObject que se va spawnear.
    [SerializeField] private GameObject enemigo;

    public int numeroEnemigos = 50;
    public int radio = 50;

    // genera un numero aleatorio de enemigos alrededor del spawner ()ffffffffffff
    void Start()
    {
        Vector3 spawn_pos = transform.position; //posicion del spawner

        // repetir para cada enemigo
        for (int i=0; i<numeroEnemigos; i++)
        {
            // randomizar la posicion del enemigo alrededor un radio en un plano
            float rnd_x = UnityEngine.Random.Range(-radio, radio);
            float rnd_z = UnityEngine.Random.Range(-radio, radio);

            // set posicion y rotacion de cada esfera
            Vector3 enemy_pos = new Vector3( spawn_pos.x + rnd_x, 0.5f, spawn_pos.z + rnd_z );
            Quaternion enemy_rotation = Quaternion.identity;

            // crea nueva instancia
            GameObject nuevoEnemigo = Instantiate(enemigo, enemy_pos, enemy_rotation); 

            // set del nombre del enemigo
            nuevoEnemigo.name = "EnemigoClon_" + i;    
        }
        
    }
}