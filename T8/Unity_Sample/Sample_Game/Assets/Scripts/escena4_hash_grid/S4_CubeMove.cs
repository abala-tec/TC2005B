using System;
using UnityEngine;
using UnityEngine.InputSystem;   // para leer el input del teclados
using TMPro;
using UnityEngine.UIElements;    // para poder acceder al HUD del juego

public class S4_CubeMove : MonoBehaviour
{
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    public float speed = 5.0f;
    public float jumpForce = 5.0f;
    public int caidas = 0;
    public bool cayendo = false;
    [SerializeField] private TextMeshProUGUI textoCaidas;   //objeto serializable para conectar el texto de caidas del hub
    private bool estaEnSuelo = true; //bandera para evitar saltar en el aire
    private Rigidbody rb = null;

    void Start()
    {
        rb = GetComponent<Rigidbody>();
    }
    
    // Resetea la posicion del cubo para empezar de nuevo
    public void ButtonClick()
    {
        if (cayendo == true)
        {
            transform.rotation = Quaternion.identity;  // reseata la orientacion del cubo callendo
            transform.position = new Vector3(0.0f,1.0f,0.0f);  // resetea la poscion del cubo en el espacio
            cayendo = false;
        }
    }

    private void OnCollisionEnter(Collision collision)
    {
        if (collision.gameObject.name == "Plane")  // Si el cubo esta chocando con el suelo 
        {
            estaEnSuelo = true;
        }
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

            if (keyboard.spaceKey.wasPressedThisFrame && estaEnSuelo == true)
            {
                rb.AddForce(Vector3.up * jumpForce, ForceMode.Impulse);
                estaEnSuelo = false;
            }
        }

        // 3. Normalizar el vector para que no camine más rápido en diagonal
        if (movement.magnitude > 1f)
        {
            movement.Normalize();
        }

        if (transform.position.y <= -1.0f && cayendo == false)
        {   
            cayendo = true;   // bandera para contar una sola caida
            caidas++;   // cuenta las caidas
            Debug.Log($"Caidas: {caidas}");  
            if (textoCaidas != null) { textoCaidas.text = caidas.ToString(); } //muestra el numero de caidas en el hub
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
