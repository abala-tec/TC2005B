# Algoritmo: voltear el sprite al caminar

El script `S4_CubeMove.cs` guarda una referencia al `SpriteRenderer` y cambia su
propiedad `flipX` cuando el jugador camina a la izquierda o a la derecha.

## 1. Encontrar el sprite

```csharp
private SpriteRenderer sprite = null;

void Start()
{
    rb = GetComponent<Rigidbody>();
    GameObject goSprite = GameObject.Find("velma_sprite_walk");
    sprite = goSprite.GetComponent<SpriteRenderer>();
}
```

`GameObject.Find` busca un objeto por su nombre. Se usa una sola vez, en `Start`,
porque recorrer la jerarquía es lento.

El nombre debe coincidir exactamente con el objeto de la escena. En este caso,
`velma_sprite_walk`.

## 2. Cambiar flipX con el teclado

```csharp
if (keyboard.dKey.isPressed || keyboard.rightArrowKey.isPressed) {
    movement.x = 1f;
    sprite.flipX = false;
}
if (keyboard.aKey.isPressed || keyboard.leftArrowKey.isPressed) {
    movement.x = -1f;
    sprite.flipX = true;
}
```

- Derecha: el movimiento va hacia `+X` y el sprite mira a la derecha
  (`flipX = false`).
- Izquierda: el movimiento va hacia `-X` y el sprite mira a la izquierda
  (`flipX = true`).

`flipX` no rota el objeto. Solo dibuja el sprite reflejado en el eje X. El
collider y la posición no cambian.

## 3. Errores comunes

- **Nombre distinto:** `GameObject.Find` devuelve `null` y `sprite.flipX` lanza
  una excepción.
- **Buscar en Update:** `GameObject.Find` es lento; se usa en `Start`.
- **Cambiar la rotación:** para un sprite 2D conviene `flipX`, no `transform.Rotate`.
- **Sprite sin Animator:** el sprite se voltea, pero no camina.

## 4. Código completo

```csharp
using System;
using UnityEngine;
using UnityEngine.InputSystem;   // para leer el input del teclado
using TMPro;
using UnityEngine.UIElements;    // para poder acceder al HUD del juego

public class S4_CubeMove : MonoBehaviour
{
    public float speed = 5.0f;
    public float jumpForce = 5.0f;
    public int caidas = 0;
    public bool cayendo = false;
    [SerializeField] private TextMeshProUGUI textoCaidas;
    private bool estaEnSuelo = true;
    private Rigidbody rb = null;
    private SpriteRenderer sprite = null;

    void Start()
    {
        rb = GetComponent<Rigidbody>();
        GameObject goSprite = GameObject.Find("velma_sprite_walk");
        sprite = goSprite.GetComponent<SpriteRenderer>();
    }

    public void ButtonClick()
    {
        if (cayendo == true)
        {
            transform.rotation = Quaternion.identity;
            transform.position = new Vector3(0.0f,1.0f,0.0f);
            cayendo = false;
        }
    }

    private void OnCollisionEnter(Collision collision)
    {
        if (collision.gameObject.name == "Plane")
        {
            estaEnSuelo = true;
        }
    }

    void Update()
    {
        Vector3 movement = Vector3.zero;
        Keyboard keyboard = Keyboard.current;

        if (keyboard != null)
        {
            if (keyboard.dKey.isPressed || keyboard.rightArrowKey.isPressed) {
                movement.x = 1f;
                sprite.flipX = false;
            }
            if (keyboard.aKey.isPressed || keyboard.leftArrowKey.isPressed) {
                movement.x = -1f;
                sprite.flipX = true;
            }

            if (keyboard.wKey.isPressed || keyboard.upArrowKey.isPressed) {
                movement.z = 1f;
            }
            if (keyboard.sKey.isPressed || keyboard.downArrowKey.isPressed) {
                movement.z = -1f;
            }

            if (keyboard.spaceKey.wasPressedThisFrame && estaEnSuelo == true)
            {
                rb.AddForce(Vector3.up * jumpForce, ForceMode.Impulse);
                estaEnSuelo = false;
            }
        }

        if (movement.magnitude > 1f)
        {
            movement.Normalize();
        }

        if (transform.position.y <= -1.0f && cayendo == false)
        {
            cayendo = true;
            caidas++;
            Debug.Log($"Caidas: {caidas}");
            if (textoCaidas != null) { textoCaidas.text = caidas.ToString(); }
        }

        transform.Translate(movement * speed * Time.deltaTime);
    }
}
```
