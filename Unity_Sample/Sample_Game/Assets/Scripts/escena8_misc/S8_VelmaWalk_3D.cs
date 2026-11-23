using UnityEngine;
using UnityEngine.InputSystem;   // para leer el input del teclados
using TMPro;
using System.Collections.Generic;
using UnityEngine.Serialization;   // FormerlySerializedAs: renombrar variables sin perder su valor en el Inspector

public class S8_VelmaWalk_3D : MonoBehaviour
{
    [Header("Velocidades SMB3 (1 unidad = 1 tile)")]
    public float walkSpeed = 5.625f;          // $18 = 1.5 px/frame
    public float runSpeed = 9.375f;           // $28 = 2.5 px/frame
    public float acceleration = 12.3046875f;  // 0.0546875 px/frame²
    public float braking = 12.3046875f;       // rate de frenado

    [Header("Salto y gravedad")]
    public float jumpSpeed = 13.125f;         // $38 = 3.5 px/frame
    public float gravity = 70.3125f;          // 5/16 px/frame²
    public float jumpGravity = 14.0625f;      // 1/16 px/frame²
    public float jumpHoldLimit = 7.5f;        // $20 = 2 px/frame
    public float maxFallSpeed = 15f;          // $40 = 4 px/frame
    public float maxHorizontalSpeed = 15f;    // $40 = 4 px/frame
    [FormerlySerializedAs("kickBack")]
    public float knockBack = 10f;             // la velocidad de empuje cuando el enemigo toca a velma

    [Header("Combate")]
    public float hachazoDuracion = 0.25f;     // cuanto tiempo el hachazo esta "activo" (puede pegar)
    public float hachazoAlcance = 0.8f;       // que tan enfrente de Velma esta la esfera del hachazo
    public float hachazoRadio = 0.6f;         // tamaño de la esfera del hachazo
    public float invulnerableTiempo = 1f;     // segundos sin recibir golpes despues de un golpe

    private float hachazoTimer = 0f;          // > 0 = el hachazo esta activo
    private Vector3 hachazoDir;               // direccion del hachazo (en el suelo XZ)
    private HashSet<S8_EnemigoCilindro> golpeadosPorHachazo = new HashSet<S8_EnemigoCilindro>();  // a quien ya le pego este hachazo
    private float invulnerableTimer = 0f;     // > 0 = Velma no recibe golpes
    

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
        bool jumpPressed = kb.spaceKey.wasPressedThisFrame || kb.zKey.wasPressedThisFrame;
        bool jumpHeld = kb.spaceKey.isPressed || kb.zKey.isPressed;

        // El suelo se detecta con Unity y los Rigidbodies OnCollisionEnter/Stay/Exit
        if (grounded && vy <= 0f) vy = 0f; // tope para vy, cuando se toca el suelo y la velocidad vertical is negativa

        // Re-deefine la velocidad maxima si se esta precionando RUN o no. (en X y Z)
        // si presiona run topSpeed = runSpeed, si no topSpeed = walspeed
        float topSpeed = runHeld ? runSpeed : walkSpeed;

        sprite_animator.SetBool("isRunning", runHeld && input != Vector2.zero);
        sprite_animator.SetBool("isJumping", !grounded);

        if (grounded && kb.fKey.wasPressedThisFrame)
        {
            sprite_animator.SetTrigger("hack");  // trigerea la animacion del hachazo (trigger "hack" del controller, se ejecuta una sola vez)

            // dir es la direcion normalizada del velma en ese momento
            Vector2 dir = input != Vector2.zero ? input.normalized : new Vector2(sprite_render.flipX ? -1f : 1f, 0f);
            S8_SoundControl.play_airWush();  // sonido del hachazo al aire

            // activa el hachazo: durante hachazoDuracion la esfera enfrente de Velma puede pegarle a enemigos
            hachazoTimer = hachazoDuracion;
            hachazoDir = new Vector3(dir.x, 0f, dir.y);
            golpeadosPorHachazo.Clear();
        }

        // el hachazo se revisa ANTES de las colisiones: si mata al zombie, el zombie ya no puede golpear
        if (hachazoTimer > 0f)
        {
            hachazoTimer -= Time.deltaTime;
            RevisarHachazo();
        }

        if (invulnerableTimer > 0f) invulnerableTimer -= Time.deltaTime;

        if (velma_empujada)  // cuando el enemigo empuja a velma (se aplica de inmediato, no espera el suelo)
        {
            sprite_animator.SetTrigger("push");  // trigerea la animacion de velma cuando cae (trigger se ejecuta una sola vez)

            horizontal += empuje_dir * knockBack;   // suma: empuje_dir ya apunta lejos del enemigo
            velma_empujada = false;
            S8_SoundControl.play_hit();  // plays the hit sound
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

        // Inicio del evento del boton de salto 
        // siempre empieza estando en el suelo
        if (jumpPressed && grounded)
        {
            vy = jumpSpeed;  // velocidad del salto (en Y obvimente)
            grounded = false; // se baja la bandera de ground (por que salto)
            S8_SoundControl.play_jump();
        }

        // Calculo de la gravedad (cuando no esta en el suelo)
        if (!grounded)
        {
            // lightgravity es TRUE si jump se esta presionando y se esta subiendo.
            // (primera fase de la parabola del salto)
            bool lightGravity = jumpHeld && vy > jumpHoldLimit;

            // si lightGravity es true usa jumpGravity. 
            // si lightGravity es false usa gravity. 
            // resta jumpgravity o gravity por cada unidad de tiempo en vy = vy - (G * time delta)
            vy -= (lightGravity ? jumpGravity : gravity) * Time.deltaTime;

            // Esto define un tope maximo para la velocidad en Y (maxFallSpeed)
            vy = Mathf.Max(vy, -maxFallSpeed);
        }

        // Aplicar el resultado final la velocidad del rigid body del cubo. 
        rb.linearVelocity = new Vector3(horizontal.x, vy, horizontal.y);

    }

    public void DisableControls(bool value)
    {
        Debug.Log($"duck {value}");
        controls_disabled = value;
        sprite_animator.SetBool("isDucking", value);
    }

    void OnCollisionEnter(Collision collision)
    {
        CheckGround(collision);
        CheckEnemyHit(collision);
    }

    void OnCollisionStay(Collision collision)
    {
        CheckGround(collision);
        CheckEnemyHit(collision);   // si se queda pegada al zombie y ya paso la invulnerabilidad, vuelve a recibir golpe
    }

    void FixedUpdate()
    {
        grounded = false;   // Enter/Stay lo vuelven a poner en true si sigue tocando el piso
    }

    // funcion que checa si hay colision con el suelo.
    // detectando si al rigid body del personaje lo esta tocando una fuerza por abajo.
    void CheckGround(Collision collision)
    {
        if (vy > 0f) return;  // si esta subiendo o saltando: no cuenta como colision en el suelo

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

    // centro de la esfera del hachazo: enfrente de Velma, en la direccion del hachazo
    Vector3 CentroHachazo()
    {
        return transform.position + hachazoDir * hachazoAlcance;
    }

    // el hachazo es una esfera invisible enfrente de Velma (como el filo del hacha).
    // si un enemigo esta dentro, se le avisa. El enemigo decide si muere (segun su estado).
    void RevisarHachazo()
    {
        Collider[] golpeados = Physics.OverlapSphere(CentroHachazo(), hachazoRadio, LayerMask.GetMask("Enemigos"));
        foreach (Collider c in golpeados)
        {
            S8_EnemigoCilindro enemigo = c.GetComponent<S8_EnemigoCilindro>();
            if (enemigo == null || golpeadosPorHachazo.Contains(enemigo)) continue;   // una sola vez por hachazo
            golpeadosPorHachazo.Add(enemigo);

            if (enemigo.RecibirHachazo(transform.position)) { S8_SoundControl.play_hachazo(); }
        }
    }

    // dibuja la esfera del hachazo en la escena (seleccionar a Velma) para ajustar alcance y radio
    void OnDrawGizmosSelected()
    {
        Vector3 dir = hachazoDir != Vector3.zero ? hachazoDir : Vector3.right;
        Gizmos.color = hachazoTimer > 0f ? Color.red : Color.yellow;
        Gizmos.DrawWireSphere(transform.position + dir * hachazoAlcance, hachazoRadio);
    }

    // revisamos si velma fue tocada por el enemigo
    bool CheckEnemyHit(Collision collision)
    {
        if (invulnerableTimer > 0f) return false;   // recien golpeada: no recibe otro golpe

        if (collision.gameObject.layer == LayerMask.NameToLayer("Enemigos"))
        {
            // el enemigo decide si hubo golpe: solo si Velma esta enfrente de el (golpe_angulo)
            bool huboGolpe = collision.gameObject.GetComponent<S8_EnemigoCilindro>().GolpeVelma(transform.position);

            if (huboGolpe)
            {
                Vector3 away = transform.position - collision.transform.position;  // vector entre el enemigo y el jugador
                away.y = 0f;  // y is not important here

                if (away.sqrMagnitude > 0.0001f)  // evita normalizar un vector zero (intestable por punto floante)
                {
                    empuje_dir = new Vector2(away.x, away.z).normalized;
                    velma_empujada = true;
                    invulnerableTimer = invulnerableTiempo;
                    return true;
                }
            }
        }
        return false;
    }
}
