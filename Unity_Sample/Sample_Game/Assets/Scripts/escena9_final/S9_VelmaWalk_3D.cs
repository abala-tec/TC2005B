using UnityEngine;
using UnityEngine.InputSystem;   // para leer el input del teclados
using TMPro;
using UnityEditor.U2D;
using UnityEngine.VFX;
using UnityEditor;

public class S9_VelmaWalk_3D : MonoBehaviour
{
    [Header("Velocidades estilo survival zombie (1 unidad = 1 tile)")]
    public float walkSpeed = 2.5f;            // caminata lenta y cautelosa
    public float runSpeed = 4.5f;             // sprint corto, apenas mas rapido que un zombie
    public float acceleration = 18f;          // arranca rapido pero a velocidad baja
    public float braking = 30f;               // frena casi en seco, sin patinar

    [Header("Gravedad")]
    public float gravity = 70.3125f;          // 5/16 px/frame²
    public float maxFallSpeed = 15f;          // $40 = 4 px/frame
    public float maxHorizontalSpeed = 6f;     // tope bajo, ni los empujones la lanzan lejos
    public float kickImpulse = 1.5f;          // empujon corto al patear (shove)
    public float kickBack = 5f;               // retroceso al ser golpeada por un zombie
    

    private Rigidbody rb;
    private Vector2 horizontal;
    private float vy;
    private bool grounded;
    private bool cayendo;
    private SpriteRenderer sprite_render = null;
    private Animator sprite_animator = null;
    private bool controls_disabled = false;
    private Vector2 empuje_dir;   // bandera para darle el empujon a velma
    private bool velma_empujada = false;
    public bool atrapada = false;  // true = tiene una piedra encima (no se mueve hasta que se la quiten)


    void Start()
    {
        rb = GetComponent<Rigidbody>();
        sprite_render = GetComponent<SpriteRenderer>(); 
        sprite_animator = GetComponent<Animator>();
        rb.useGravity = false;    // la gravedad se calcula con el script no con Unity
        rb.interpolation = RigidbodyInterpolation.Interpolate;
        rb.collisionDetectionMode = CollisionDetectionMode.Continuous;
        rb.constraints = RigidbodyConstraints.FreezeRotation;  // el sprite es 2D no rota
        
    }
    
    // Resetea la posicion del cubo para empezar de nuevo
    public void ResetButtonClick()
    {
        rb.constraints = RigidbodyConstraints.FreezeAll;
        rb.rotation = Quaternion.identity;  // reseata la orientacion del cubo callendo
        rb.position = new Vector3(0.0f,1.0f,0.0f);  // resetea la poscion del cubo en el espacio
        rb.constraints = RigidbodyConstraints.FreezeRotation; 
    }


    void Update()
    {
        // con la piedra encima: agachada y quieta (el rigidbody esta en kinematic, no se calcula fisica)
        if (atrapada) return;

        Keyboard kb = Keyboard.current;
        if (kb == null) return;

        // Se leer entrada del teclado  
        float inputX = 0f;  // Para derecha izquierda
        if (kb.dKey.isPressed || kb.rightArrowKey.isPressed) 
        {
            inputX += 1f;
            if (sprite_render != null) { sprite_render.flipX = false; } // flipea el sprite
        }
        if (kb.aKey.isPressed || kb.leftArrowKey.isPressed)
        {
            inputX -= 1f;
            if (sprite_render != null) { sprite_render.flipX = true; }  // flipea el sprite
        }

        float inputZ = 0f;  // Para arriba y abajo (profundidad Z)
        if (kb.wKey.isPressed || kb.upArrowKey.isPressed) inputZ += 1f;
        if (kb.sKey.isPressed || kb.downArrowKey.isPressed) inputZ -= 1f;

        // Vector con los 2 inputs
        Vector2 input = new Vector2(inputX, inputZ); 

        if (controls_disabled == true) // if controls is disabled kill movemnt and finish
        {
            horizontal = Vector2.zero;
            rb.linearVelocity = new Vector3(0f, rb.linearVelocity.y, 0f);
            sprite_animator.SetBool("isRunning", false);
            return;
        }   

        // Si el vector es mayor a 1, normalizalo. 
        if (input.sqrMagnitude > 1f) input.Normalize();

        // banderas para checar que botones estan presionados
        bool runHeld = kb.leftShiftKey.isPressed || kb.xKey.isPressed;

        // El suelo se detecta con Unity y los Rigidbodies OnCollisionEnter/Stay/Exit
        if (grounded && vy <= 0f) vy = 0f; // tope para vy, cuando se toca el suelo y la velocidad vertical is negativa

        // Re-deefine la velocidad maxima si se esta precionando RUN o no. (en X y Z)
        // si presiona run topSpeed = runSpeed, si no topSpeed = walspeed
        float topSpeed = runHeld ? runSpeed : walkSpeed;

        sprite_animator.SetBool("isRunning", runHeld && input != Vector2.zero);

        if (grounded && kb.fKey.wasPressedThisFrame)
        {
            sprite_animator.SetTrigger("hack");  // trigerea la animacion del hack (trigger se ejecuta una sola vez)

            // dir es la direcion normalizada del velma en ese momento
            Vector2 dir = input != Vector2.zero ? input.normalized : new Vector2(sprite_render.flipX ? -1f : 1f, 0f);
            horizontal = horizontal + (dir * kickImpulse);  // horizontal + el impulso del kick en esa direccion
            S9_SoundControl.play_airWush();  // play velma kick sound
        }

        if (grounded && velma_empujada)  // cuando el enemigo empuja  a velma 
        {
            sprite_animator.SetTrigger("push");  // trigerea la animacion de velma cuando cae (trigger se ejecuta una sola vez)

            horizontal += empuje_dir * kickBack;   // suma: empuje_dir ya apunta lejos del enemigo
            velma_empujada = false;
            S9_SoundControl.play_hit();  // plays the hit sound
        }

        // si se presiono AWSD o arrows
        if (input != Vector2.zero)  // si el Vector de movimiento NO es zero
        {
            Vector2 target = input * topSpeed;

            bool sameDirection = horizontal.sqrMagnitude > 0.01f &&
                                 Vector2.Dot(horizontal.normalized, input) > 0.1f;

            // Si va en la misma dirección Y rápido que la tope de velocidad (frena)
            if (sameDirection && horizontal.magnitude > topSpeed)
            {
                // si va por el suelo frena, 
                if (grounded)
                    horizontal = Vector2.MoveTowards(horizontal, target, braking * Time.deltaTime);
                // si va por el aire no hacer nada (conserva el momento)
            }
            else
            {
                // Si va en la direccion contraria O mas lento que el tope (acelera)
                horizontal = Vector2.MoveTowards(horizontal, target, acceleration * Time.deltaTime);
            }
        }
        else if (grounded)
        {
            // Sin input y en el suelo se frena. 
            // Pero si esta en el conserva la velocidad y esto no se ejecuta
            horizontal = Vector2.MoveTowards(horizontal, Vector2.zero, braking * Time.deltaTime);
        }

        if (horizontal.magnitude > maxHorizontalSpeed)
            horizontal = horizontal.normalized * maxHorizontalSpeed;

        // Calculo de la gravedad (cuando no esta en el suelo)
        if (!grounded)
        {
            // resta gravity por cada unidad de tiempo en vy = vy - (G * time delta)
            vy -= gravity * Time.deltaTime;

            // Esto define un tope maximo para la velocidad en Y (maxFallSpeed)
            vy = Mathf.Max(vy, -maxFallSpeed);
        }

        // Aplicar el resultado final la velocidad del rigid body del cubo. 
        rb.linearVelocity = new Vector3(horizontal.x, vy, horizontal.y);

    }

    public void DisableControls(bool value)
    {
        if (atrapada) value = true;   // con una piedra encima nadie le regresa los controles
        controls_disabled = value;
        sprite_animator.SetBool("isDucking", value);
    }

    // la piedra cae encima de Velma (true) o se la quitan de encima (false).
    // Atrapada: sin collider (la piedra la atraviesa y toca el suelo), congelada y agachada (isDucking).
    public void Atrapar(bool value)
    {
        atrapada = value;

        horizontal = Vector2.zero;
        vy = 0f;
        rb.isKinematic = value;   // sin collider caeria por el piso: la congelamos
        if (!value) rb.linearVelocity = Vector3.zero;   // al salir empieza quieta

        foreach (Collider c in GetComponents<Collider>()) c.enabled = !value;

        controls_disabled = true;                    // al salir sigue agachada hasta que suelten la piedra
        sprite_animator.SetBool("isDucking", true);
        sprite_animator.SetBool("isRunning", false);
    }

    void OnCollisionEnter(Collision collision)
    {
        CheckGround(collision);
        if (CheckEnemyHit(collision) == true) {return;}
        CheckVelmaKick(collision);
    }

    void OnCollisionStay(Collision collision)
    {
        CheckGround(collision);
        CheckVelmaKick(collision);
    }

    void FixedUpdate()
    {
        grounded = false;   // Enter/Stay lo vuelven a poner en true si sigue tocando el piso
    }

    // funcion que checa si hay colision con el suelo.
    // detectando si al rigid body del personaje lo esta tocando una fuerza por abajo.
    void CheckGround(Collision collision)
    {
        if (vy > 0f) return;  // si esta subiendo: no cuenta como colision en el suelo

        // checa con todos los objetos colisionado con el rigidbody
        foreach (ContactPoint contact in collision.contacts)
        {
            if (contact.normal.y > 0.5f) // si el contacto viene de abajo
            {
                grounded = true;
                return;
            }
        }
    }

    // revisa si velma pateo a un enemigo y envia el evento al enemigo
    void CheckVelmaKick(Collision collision)
    {
        if (collision.gameObject.layer != LayerMask.NameToLayer("Enemigos")) return;
        bool pateando = sprite_animator.GetCurrentAnimatorStateInfo(0).IsName("VelmaHack");

        // la patada pega en cualquier direccion, el enemigo decide por donde le llego
        if (pateando){
            bool hit = collision.gameObject.GetComponent<S9_EnemigoCilindro>().RecibirPatada(transform.position);
            if (hit) { S9_SoundControl.play_kick(); }
        }
    }

    // revisamos si velma fue tocada por el enemigo
    bool CheckEnemyHit(Collision collision)
    {
        if (collision.gameObject.layer == LayerMask.NameToLayer("Enemigos")) 
        { 
            // el enemigo decide si hubo golpe: solo si Velma esta enfrente de el
            bool huboGolpe = collision.gameObject.GetComponent<S9_EnemigoCilindro>().GolpeVelma(transform.position);

            if (huboGolpe)
            {
                Vector3 away = transform.position - collision.transform.position;  // vector entre el enemigo y el jugador
                away.y = 0f;  // y is not important here

                if (away.sqrMagnitude > 0.0001f)  // evita normalizar un vector zero (intestable por punto floante)
                {
                    empuje_dir = new Vector2(away.x, away.z).normalized;
                    velma_empujada = true;
                    return true;
                }
            }
        }
        return false;
    }
}
