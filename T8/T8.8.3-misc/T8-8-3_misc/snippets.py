"""Fragmentos de escena8_misc que se muestran como imagen.

Los archivos completos estan en csharp/. Los comentarios largos se
omitieron de las imagenes para que el codigo se lea en la diapositiva.
"""

SNIPPETS = {
    "code_audio_fields": {
        "code": """[RequireComponent(typeof(AudioSource))]
public class S8_SoundControl : MonoBehaviour
{
    public AudioClip jump;
    public AudioClip hit;
    public AudioClip won;
    [FormerlySerializedAs("kick")]
    public AudioClip hachazo;
    public AudioClip airWush;
    public AudioClip background;

    private AudioSource asource;
    private static S8_SoundControl instancia;""",
        "size": 26,
        "line": 34,
        "file": "S8_SoundControl.cs",
        "note": "lineas 5-17, sin comentarios",
    },
    "code_audio_awake": {
        "code": """    void Awake()
    {
        instancia = this;
        asource = GetComponent<AudioSource>();

        if (background != null)
        {
            asource.clip = background;
            asource.loop = true;
            asource.Play();
        }
    }""",
        "size": 26,
        "line": 34,
        "file": "S8_SoundControl.cs",
        "note": "lineas 17-28",
    },
    "code_audio_methods": {
        "code": """    public static void play_jump() 
    { 
        instancia.asource.PlayOneShot(
            instancia.jump); 
    }

    // ...

    public static void play_airWush()
    {
        instancia.asource.PlayOneShot(
            instancia.airWush);
    }""",
        "size": 24,
        "line": 32,
        "file": "S8_SoundControl.cs",
        "note": "lineas 30-33 y 46-49; hit y hachazo omitidos",
    },
    "code_rock_click": {
        "code": """        if (mouse.leftButton.wasPressedThisFrame)
        {
            Ray rayo =
                mainCamera.ScreenPointToRay(pos);
            if (Physics.Raycast(
                    rayo, out RaycastHit hit)
                && hit.transform == transform)
            {
                arrastrando = true;
                alturaArrastre =
                    transform.position.y
                    + liftHeight;
                rigdbody.isKinematic = true;
            }
        }""",
        "size": 24,
        "line": 32,
        "file": "S8_RockDragDrop.cs",
        "note": "lineas 37-51, sin comentarios",
    },
    "code_rock_move": {
        "code": """        if (arrastrando)
        {
            velma3D.DisableControls(true);
            transform.position = new Vector3(
                transform.position.x,
                alturaArrastre,
                transform.position.z);
            if (arrastrando &&
                (keyboard.upArrowKey
                    .wasPressedThisFrame ||
                 keyboard.wKey
                    .wasPressedThisFrame))
            {
                transform.position = new Vector3(
                    transform.position.x,
                    alturaArrastre,
                    transform.position.z + rockStep);
            }
        }""",
        "size": 22,
        "line": 27,
        "file": "S8_RockDragDrop.cs",
        "note": "lineas 60-70; W/S en Z; A/D repiten el patron en X",
    },
    "code_rock_release": {
        "code": """        if (mouse.leftButton.wasReleasedThisFrame
            && arrastrando)
        {
            velma3D.DisableControls(false);
            arrastrando = false;
            dropped = true;
            rigdbody.isKinematic = false;
        }""",
        "size": 24,
        "line": 32,
        "file": "S8_RockDragDrop.cs",
        "note": "lineas 53-58, sin comentarios",
    },
    "code_rock_collision": {
        "code": """    void OnCollisionEnter(Collision collision)
    {
        int piso = LayerMask.NameToLayer("Piso");
        int paredes = LayerMask.NameToLayer("Paredes");

        if (dropped == true &&
            (collision.gameObject.layer == piso ||
             collision.gameObject.layer == paredes))
        {
            dropped = false;
            rigdbody.linearVelocity = Vector3.zero;
            rigdbody.angularVelocity = Vector3.zero;
            rigdbody.isKinematic = true;

            S8_Grid.Instancia.calculaGrid();
        }
    }""",
        "size": 24,
        "line": 32,
        "file": "S8_RockDragDrop.cs",
        "note": "lineas 87-104, sin comentarios",
    },
    "code_anim_set": {
        "code": """        sprite_animator.SetBool("isRunning", runHeld && input != Vector2.zero);
        sprite_animator.SetBool("isJumping", !grounded);""",
        "size": 24,
        "line": 32,
        "file": "S8_VelmaWalk_3D.cs",
        "note": "lineas 109-110",
    },
    "code_anim_duck": {
        "code": """    public void DisableControls(bool value)
    {
        Debug.Log($"duck {value}");
        controls_disabled = value;
        sprite_animator.SetBool(
            "isDucking", value);
    }""",
        "size": 26,
        "line": 34,
        "file": "S8_VelmaWalk_3D.cs",
        "note": "lineas 193-198",
    },
    "code_anim_kick": {
        "code": """        if (grounded && kb.fKey.wasPressedThisFrame)
        {
            sprite_animator.SetTrigger("hack");

            Vector2 dir = input != Vector2.zero
                ? input.normalized
                : new Vector2(
                    sprite_render.flipX ? -1f : 1f, 0f);
            S8_SoundControl.play_airWush();

            hachazoTimer = hachazoDuracion;
            hachazoDir = new Vector3(dir.x, 0f, dir.y);
            golpeadosPorHachazo.Clear();
        }""",
        "size": 22,
        "line": 30,
        "file": "S8_VelmaWalk_3D.cs",
        "note": "lineas 122-134, sin comentarios",
    },
    "code_anim_check": {
        "code": """void RevisarHachazo()
{
    Collider[] golpeados = Physics.OverlapSphere(
        CentroHachazo(), hachazoRadio,
        LayerMask.GetMask("Enemigos"));
    foreach (Collider c in golpeados)
    {
        S8_EnemigoCilindro enemigo =
            c.GetComponent<S8_EnemigoCilindro>();
        if (enemigo == null ||
            golpeadosPorHachazo.Contains(enemigo))
            continue;
        golpeadosPorHachazo.Add(enemigo);
        if (enemigo.RecibirHachazo(transform.position))
            S8_SoundControl.play_hachazo();
    }
}""",
        "size": 22,
        "line": 28,
        "file": "S8_VelmaWalk_3D.cs",
        "note": "lineas 265-276, sin comentarios",
    },
    "code_enemy_hit": {
        "code": """    bool CheckEnemyHit(Collision collision)
    {
        if (invulnerableTimer > 0f) return false;
        if (collision.gameObject.layer ==
            LayerMask.NameToLayer("Enemigos")) 
        { 
            bool huboGolpe = collision.gameObject
                .GetComponent<S8_EnemigoCilindro>()
                .GolpeVelma(transform.position);

            if (huboGolpe)
            {""",
        "size": 24,
        "line": 32,
        "file": "S8_VelmaWalk_3D.cs",
        "note": "lineas 287-297, sin comentarios",
    },
    "code_kick_away": {
        "code": """            Vector3 away = transform.position
                - collision.transform.position;
            away.y = 0f;

            if (away.sqrMagnitude > 0.0001f)
            {
                empuje_dir = new Vector2(
                    away.x, away.z).normalized;
                velma_empujada = true;
                invulnerableTimer = invulnerableTiempo;
                return true;
            }""",
        "size": 24,
        "line": 32,
        "file": "S8_VelmaWalk_3D.cs",
        "note": "lineas 298-307, sin comentarios",
    },
    "code_push": {
        "code": """        if (velma_empujada)
        {
            sprite_animator.SetTrigger(
                "push");
            horizontal +=
                empuje_dir * knockBack;
            velma_empujada = false;
            S8_SoundControl.play_hit();
        }""",
        "size": 26,
        "line": 34,
        "file": "S8_VelmaWalk_3D.cs",
        "note": "lineas 145-153, sin comentarios",
    },
}
