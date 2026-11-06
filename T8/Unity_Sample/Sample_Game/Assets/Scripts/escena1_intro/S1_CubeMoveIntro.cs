using System;
using UnityEngine;
using UnityEngine.InputSystem;   // para leer el input del teclados

public class CubeMoveIntro : MonoBehaviour
{
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    public float speed = 5.0f;

    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        // 1. Crea un vector para guardar la direccion del movimiento
        Vector3 movement = Vector3.zero;

        // 2. Objecto para controlar el teclado
        Keyboard keyboard = Keyboard.current;

        if (keyboard != null)
        {
            // Lee eje en X con las fechas derecha izquierda
            if (keyboard.dKey.isPressed || keyboard.rightArrowKey.isPressed) {
                movement.x = 1f;
            }
            if (keyboard.aKey.isPressed || keyboard.leftArrowKey.isPressed) {
                movement.x = -1f;
            }

            // Define eje en Z con las flechas arriba abajo
            if (keyboard.wKey.isPressed || keyboard.upArrowKey.isPressed) {
                movement.z = 1f;
            }
            if (keyboard.sKey.isPressed || keyboard.downArrowKey.isPressed) {
                movement.z = -1f;
            }

            if (keyboard.spaceKey.isPressed) {
                transform.rotation = Quaternion.identity;  // reseata la orientacion del cubo callendo
                transform.position = new Vector3(0.0f,1.0f,0.0f);  // resetea la poscion del cubo en el espacio
            }
        }

        // 3. Normalizar el vector para que no camine más rápido en diagonal
        if (movement.magnitude > 1f)
        {
            movement.Normalize();
        }

        // 4. Mueve el cubo teniendo en cuenta el dt, la velocidad, el vector de direccion
        transform.Translate(movement * speed * Time.deltaTime);


        // 1. Mueve al objeto hacia SU propio "adelante" (Space.Self es el valor por defecto)
        // transform.Translate(movement * speed * Time.deltaTime); 
        // O de forma explícita:
        // transform.Translate(movement * speed * Time.deltaTime, Space.Self);

        // 2. Mueve al objeto hacia el "adelante" del MUNDO (hacia el Z global), sin importar cómo esté rotado el objeto
        // transform.Translate(movement * speed * Time.deltaTime, Space.World);

        // 3. Mueve al objeto hacia la dirección donde está mirando la CÁMARA
        // transform.Translate(movement * speed * Time.deltaTime, camaraTransform);
    }
}
