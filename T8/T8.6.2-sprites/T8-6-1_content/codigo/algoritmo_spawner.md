# Algoritmo: spawner de enemigos

El script `S4_Spawner.cs` crea 50 copias de una esfera alrededor del objeto
Spawner. Las copias se crean una sola vez, al inicio de la escena.

## 1. Guardar el centro

```csharp
Vector3 spawn_pos = transform.position;
```

`transform.position` es la posición del objeto que tiene el script. En la escena,
el Spawner está en `(-50, 0, -50)`.

## 2. Repetir 50 veces

```csharp
for (int i = 0; i < numeroEnemigos; i++)
{
    // Crear un enemigo
}
```

`i` empieza en 0 y termina en 49. La condición se revisa antes de cada vuelta.
Cuando `i` llega a 50, el bucle se detiene. Son 50 vueltas.

## 3. Elegir una posición aleatoria

```csharp
float rnd_x = UnityEngine.Random.Range(-radio, radio);
float rnd_z = UnityEngine.Random.Range(-radio, radio);

Vector3 enemy_pos = new Vector3(
    spawn_pos.x + rnd_x, 0.5f, spawn_pos.z + rnd_z);
```

`Random.Range(-radio, radio)` devuelve un valor entre `-radio` y `radio`. El límite
superior no se incluye cuando los valores son enteros.

El desplazamiento se suma a `spawn_pos`. Así las esferas quedan alrededor del
spawner, no alrededor del origen del mundo.

La altura se fija en `0.5`. La esfera mide 1 de diámetro, así que su centro queda a
media unidad del piso.

### Error frecuente

```csharp
// MAL: solo genera valores positivos
float rnd_x = UnityEngine.Random.Range(0, radio);
float rnd_z = UnityEngine.Random.Range(0, radio);
```

Con `0` como límite inferior, todas las esferas se acumulan en una sola esquina.
El juego no se detiene, pero el reparto se ve mal.

## 4. Crear la copia

```csharp
Quaternion enemy_rotation = Quaternion.identity;

GameObject nuevoEnemigo = Instantiate(
    enemigo, enemy_pos, enemy_rotation);

nuevoEnemigo.name = "EnemigoClon_" + i;
```

`Instantiate` recibe el molde, la posición y la rotación. Devuelve una copia nueva.
El molde original sigue en la escena.

`Quaternion.identity` significa sin rotación. La esfera no necesita un giro
inicial.

## 5. Por qué va en Start

`Start` se ejecuta una vez. Si el bucle estuviera en `Update`, se crearían 50
enemigos en cada fotograma. La escena se llenaría de copias y el juego se
volvería lento.

## 6. Código completo

```csharp
using UnityEngine;

public class S4_Spawner : MonoBehaviour
{
    // GameObject que se va spawnear.
    [SerializeField] private GameObject enemigo;

    public int numeroEnemigos = 50;
    public int radio = 50;

    // genera un numero aleatorio de enemigos alrededor del spawner
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
```
