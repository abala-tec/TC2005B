# Algoritmo de persecución del enemigo esfera

Este documento explica la parte que no aparece en `guia-enemigo-esfera.md`: el código que hace que la esfera persiga al jugador. El código completo está en `codigo/EnemigoEsfera.cs`.

## Idea general

La esfera ya sabe moverse hacia una esquina. Para perseguir, no hace falta otro algoritmo de movimiento: basta con cambiar el punto de destino.

1. Se mide la distancia entre la esfera y el cubo.
2. Si la distancia es menor o igual a `radioDeteccion`, el objetivo es el cubo.
3. Si la distancia es mayor, el objetivo vuelve a ser la esquina actual.
4. El movimiento usa la misma resta, longitud, normalización y suma que la patrulla.

## Código implementado

```csharp
public float radioDeteccion = 3.0f;

void MoverEsfera()
{
    // si la longitud de la esfera al cubo es menor a radioDeteccion,
    // persiguiendo es true
    bool persiguiendo = Longitud(cubo.position - transform.position) <= radioDeteccion;

    Vector3 objetivo;
    if (persiguiendo)
    {
        objetivo = cubo.position;
    }
    else
    {
        objetivo = esquinas[indiceObjetivo];
    }

    Vector3 hacia = objetivo - transform.position;
    float distancia = Longitud(hacia);

    if (distancia < 0.1f && !persiguiendo)
    {
        // Elige otra esquina distinta: suma 1, 2 o 3 y da la vuelta
        indiceObjetivo = (indiceObjetivo + UnityEngine.Random.Range(1, 4)) % 4;
        return;
    }

    Vector3 direccion = Normalizar(hacia);
    float paso = velocidad * Time.deltaTime;

    transform.position = new Vector3(
        transform.position.x + direccion.x * paso,
        transform.position.y,                       // la altura no cambia
        transform.position.z + direccion.z * paso
    );
}
```

## Paso a paso

### 1. Medir la distancia al cubo

```csharp
bool persiguiendo = Longitud(cubo.position - transform.position) <= radioDeteccion;
```

`cubo.position - transform.position` es el vector que va de la esfera al cubo. `Longitud` aplica la fórmula de la distancia:

```text
d = raíz(dx*dx + dy*dy + dz*dz)
```

La comparación devuelve `true` o `false` y se guarda en la variable `persiguiendo`.

### 2. Elegir el objetivo

```csharp
Vector3 objetivo;
if (persiguiendo)
{
    objetivo = cubo.position;
}
else
{
    objetivo = esquinas[indiceObjetivo];
}
```

Si `persiguiendo` es verdadero, el destino es el cubo. Si es falso, el destino es la esquina que marca `indiceObjetivo`.

### 3. Mantener el movimiento de la patrulla

```csharp
Vector3 hacia = objetivo - transform.position;
float distancia = Longitud(hacia);
```

El resto del movimiento es idéntico al de la patrulla. La única diferencia está en el valor de `objetivo`.

### 4. Evitar el cambio de esquina mientras persigue

```csharp
if (distancia < 0.1f && !persiguiendo)
{
    indiceObjetivo = (indiceObjetivo + UnityEngine.Random.Range(1, 4)) % 4;
    return;
}
```

La condición `!persiguiendo` impide que la esfera elija otra esquina cuando está persiguiendo. Si está persiguiendo y llega cerca del cubo, el código no hace `return`; sigue calculando el movimiento.

### 5. Avanzar y conservar la altura

```csharp
Vector3 direccion = Normalizar(hacia);
float paso = velocidad * Time.deltaTime;

transform.position = new Vector3(
    transform.position.x + direccion.x * paso,
    transform.position.y,
    transform.position.z + direccion.z * paso
);
```

La altura `y` se copia sin cambios. La esfera se traslada en el plano XZ, aunque el cubo esté en el aire.

## Detalles importantes

- **El radio se mide en 3D.** Incluye la altura. Si el cubo salta, `dy` crece y la distancia también. Por eso el radio horizontal efectivo se reduce cuando el cubo está alto.
- **El temporizador sigue activo.** `InvokeRepeating("NewRandom", 0f, 5f)` puede cambiar `indiceObjetivo` mientras la esfera persigue. Cuando el cubo sale del radio, la esfera va a la esquina que esté marcada en ese momento.
- **No hay búsqueda de caminos.** La esfera va en línea recta. No evita obstáculos ni paredes.
- **No hay límite del plano.** Si el cubo sale del plano, la esfera puede seguirlo fuera del plano.
- **No hay giro visual.** La esfera se traslada sin rodar.
- **No hay victoria ni derrota.** El pisotón solo escribe `PISOTON` en la Console y reubica la esfera.

## Pruebas sugeridas

| Prueba | Cómo | Resultado esperado |
|---|---|---|
| Detección | Acércate al cubo a menos de 3 unidades | La esfera deja la esquina y va hacia el cubo |
| Salida | Aléjate a más de 3 unidades | La esfera vuelve a la esquina actual |
| Altura | Salta cerca de la esfera | La distancia 3D cambia y el radio efectivo se reduce |
| Esquina | Espera 5 segundos sin acercarte | Cambia el índice objetivo |
| Límites | Lleva el cubo fuera del plano | La esfera puede salir persiguiéndolo |
