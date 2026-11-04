# Algoritmo: cámara que sigue al jugador

El script `S4_CameraFollower.cs` mueve la cámara hacia una meta calculada con la
posición del cubo. No cambia la rotación ni el campo de visión.

## 1. Calcular la meta

```csharp
Vector3 goalPosition = target.position + offset;
```

`target` es el Transform del cubo. `offset` es la distancia entre la cámara y el
cubo. En la escena se usa `(0, 5, -10)`:

- 5 unidades arriba.
- 10 unidades detrás.

La meta se mueve con el cubo. Si el cubo camina, la meta también camina.

## 2. Acercar la cámara a la meta

```csharp
Vector3 smoothedPosition = Vector3.Lerp(
    transform.position, goalPosition, followspeed);

transform.position = smoothedPosition;
```

`Vector3.Lerp` recibe:

1. La posición actual de la cámara.
2. La meta.
3. Un factor entre 0 y 1.

Devuelve un punto intermedio. Con `followspeed = 0.2`, la cámara recorre el 20 %
de la distancia que le falta en ese fotograma. En el siguiente fotograma vuelve a
calcular y recorre otro 20 % del espacio restante.

El factor no es una velocidad en metros por segundo. Es una proporción.

## 3. Ejecutar en LateUpdate

```csharp
void LateUpdate()
{
    Vector3 goalPosition = target.position + offset;
    Vector3 smoothedPosition = Vector3.Lerp(
        transform.position, goalPosition, followspeed);
    transform.position = smoothedPosition;
}
```

`LateUpdate` se ejecuta después de `Update`. El cubo se mueve en `Update`, así que
la cámara lee su posición nueva en el mismo fotograma.

## 4. Errores comunes

- **Target vacío:** `target.position` lanza `NullReferenceException`.
- **Followspeed en 0:** la cámara no se mueve.
- **Followspeed en 1:** la cámara salta a la meta y el movimiento se ve brusco.
- **Offset en píxeles:** el offset se escribe en unidades de la escena.

## 5. Código completo

```csharp
using UnityEngine;

public class S4_CameraFollower : MonoBehaviour
{
    public Transform target;  // El gameobject a seguir

    public Vector3 offset = new Vector3(0,5,-10);  // el ofset del objecto a la camara

    public float followspeed = 0.2f;   // la velocidad de seguimiento

    // Usamos LateUpdate para seguir los objetos despues de
    // haber sido afectados por fuerzas durante Update()
    void LateUpdate()
    {
        Vector3 goalPosition = target.position + offset;

        // Lerp interpola entre la posicion actual de la camara y la meta
        Vector3 smoothedPosition = Vector3.Lerp(
            transform.position, goalPosition, followspeed);

        transform.position = smoothedPosition;
    }
}
```
