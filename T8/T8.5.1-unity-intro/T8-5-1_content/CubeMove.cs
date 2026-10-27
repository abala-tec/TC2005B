using UnityEngine;
using UnityEngine.InputSystem;

public class CubeMove : MonoBehaviour
{
    public float speed = 5.0f;

    void Start()
    {
        // Aquí no hace falta inicializar nada.
    }

    void Update()
    {
        // 1. Vector que guarda la dirección.
        Vector3 movement = Vector3.zero;

        // 2. Teclado actual (Input System).
        Keyboard keyboard = Keyboard.current;

        if (keyboard != null)
        {
            // 3. Leer A/D y las flechas.
            if (keyboard.dKey.isPressed ||
                keyboard.rightArrowKey.isPressed)
            {
                movement.x = 1f;
            }

            if (keyboard.aKey.isPressed ||
                keyboard.leftArrowKey.isPressed)
            {
                movement.x = -1f;
            }

            // 4. Leer W/S y las flechas.
            if (keyboard.wKey.isPressed ||
                keyboard.upArrowKey.isPressed)
            {
                movement.z = 1f;
            }

            if (keyboard.sKey.isPressed ||
                keyboard.downArrowKey.isPressed)
            {
                movement.z = -1f;
            }

            // 5. Space: reiniciar posición y rotación.
            if (keyboard.spaceKey.isPressed)
            {
                transform.rotation = Quaternion.identity;
                transform.position = new Vector3(0f, 1f, 0f);
            }
        }

        // 6. Evitar más velocidad en diagonal.
        if (movement.magnitude > 1f)
        {
            movement.Normalize();
        }

        // 7. Mover en X y Z según el tiempo real.
        transform.Translate(movement * speed * Time.deltaTime);
    }
}
