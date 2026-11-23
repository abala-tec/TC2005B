"""Fragmentos de código de escena7_fsm que se ven como imagen.

El mismo texto se copia en las notas de la diapositiva. Los archivos
completos están en csharp/.
"""

# nombre: (código, tamaño de letra, alto de línea)
SNIPPETS = {
    "code_iface": ("""public interface IEnemyState
{
    void Enter();       // entra al estado
    void Execute();     // lógica de cada frame
    void Exit();        // sale del estado
    void DibujarGizmos(); // dibuja el cono
}""", 32, 46),

    "code_esm": ("""public class EnemyStateMachine
{
    private IEnemyState currentState;

    public void Initialize(IEnemyState primerEstado)
    {
        currentState = primerEstado;
        currentState.Enter();
    }

    public void ChangeState(IEnemyState nuevoEstado)
    {
        currentState.Exit();
        currentState = nuevoEstado;
        currentState.Enter();
    }

    public void Update() { currentState?.Execute(); }
    public void DibujarGizmos() { currentState.DibujarGizmos(); }
}""", 28, 40),

    "code_enemigo_campos": ("""public Transform jugador;          // Velma
public float chace_vel = 5.0f;
public float chace_check_time = 0.25f;
public float vision_rango = 8.0f;
public float vision_angulo = 90.0f;
public bool muerto = false;
private EnemyStateMachine esm;""", 30, 44),

    "code_enemigo_start": ("""void Start()
{
    esm = new EnemyStateMachine();
    esm.Initialize(new EPatrolState(this, esm));
}

void Update()
{
    esm.Update();
}

void OnDrawGizmos()
{
    esm?.DibujarGizmos();
}""", 30, 44),

    "code_patrulla": ("""S7_Grid grid = S7_Grid.Instancia;
patrullaGoal =
    grid.MundoACelda(enemy.transform.position);
camino = grid.BuscarCamino(patrullaGoal,
                           grid.GetRandomCelda());
// ...
Vector3 objetivo = grid.CeldaAMundo(camino[0]);
enemy.transform.position = Vector3.MoveTowards(
    enemy.transform.position, objetivo,
    enemy.chace_vel * Time.deltaTime);
if (enemy.transform.position == objetivo)
    camino.RemoveAt(0);""", 32, 46),

    "code_perseguir": ("""tiempoRecalculo -= Time.deltaTime;
if (tiempoRecalculo <= 0f)
{
    tiempoRecalculo = enemy.chace_check_time;
    camino = grid.BuscarCamino(
        grid.MundoACelda(enemy.transform.position),
        grid.MundoACelda(enemy.jugador.position));
}
// ...
Vector3 objetivo = grid.CeldaAMundo(camino[0]);
enemy.transform.position = Vector3.MoveTowards(
    enemy.transform.position, objetivo,
    enemy.chace_vel * Time.deltaTime);""", 32, 46),

    "code_muerto": ("""public void Enter()
{
    Debug.Log("Estado: Bien Muerto");

    if (enemy.muerto == false)
    {
        Transform t = enemy.transform;
        t.Rotate(t.right, -90f, Space.World);
        t.position += Vector3.down *
            (t.localScale.y - t.localScale.x / 2f);
        enemy.muerto = true;
        enemy.DesactivarFisica();
    }
}""", 30, 44),

    "code_vision": ("""public bool VeJugador()
{
    Vector3 origen = transform.position + Vector3.up;
    Vector3 dir = jugador.position + Vector3.up - origen;
    Vector3 plano = new Vector3(dir.x, 0, dir.z);

    if (dir.magnitude > vision_rango ||
        Vector3.Angle(transform.forward, plano) >
        vision_angulo / 2)
        return false;

    return !Physics.Raycast(origen, dir.normalized,
               out RaycastHit hit, dir.magnitude)
           || hit.transform.IsChildOf(jugador);
}""", 30, 43),

    "code_cono": ("""public void ConoVisionGizmo()
{
    Gizmos.color = VeJugador() ? Color.red : Color.green;
    Vector3 o = transform.position + Vector3.up;
    Vector3 izq = o + Quaternion.AngleAxis(
        -vision_angulo / 2, Vector3.up)
        * transform.forward * vision_rango;
    Vector3 der = o + Quaternion.AngleAxis(
        vision_angulo / 2, Vector3.up)
        * transform.forward * vision_rango;
    Gizmos.DrawLine(o, izq);
    Gizmos.DrawLine(izq, der);
    Gizmos.DrawLine(der, o);
}""", 25, 37),

    "code_patada_trigger": ("""if (grounded && kb.fKey.wasPressedThisFrame)
{
    sprite_animator.SetTrigger("hack");

    Vector2 dir = input != Vector2.zero
        ? input.normalized
        : new Vector2(sprite_render.flipX ? -1f : 1f, 0f);

    hachazoTimer = hachazoDuracion;
    hachazoDir = new Vector3(dir.x, 0f, dir.y);
    golpeadosPorHachazo.Clear();
}""", 28, 41),

    "code_check_hit": ("""void RevisarHachazo()
{
    Collider[] golpeados = Physics.OverlapSphere(CentroHachazo(),
        hachazoRadio, LayerMask.GetMask("Enemigos"));

    foreach (Collider c in golpeados)
    {
        EnemigoCilindro enemigo = c.GetComponent<EnemigoCilindro>();
        if (enemigo == null || golpeadosPorHachazo.Contains(enemigo))
            continue;   // una sola vez por hachazo
        golpeadosPorHachazo.Add(enemigo);

        enemigo.RecibirHachazo(transform.position);
    }
}""", 28, 41),

    "code_oncollision": ("""void OnCollisionEnter(Collision collision)
{
    CheckGround(collision);
    CheckEnemyHit(collision);
}

void OnCollisionStay(Collision collision)
{
    CheckGround(collision);
    CheckEnemyHit(collision);
}""", 28, 41),

    "code_recibir_patada": ("""public bool RecibirHachazo(Vector3 origenHachazo)
{
    if (muerto) return false;

    bool persiguiendo = esm.EstadoActual is EPerseguirState;
    golpes_recibidos++;

    if (!persiguiendo || golpes_recibidos >= golpes_persiguiendo)
    {
        esm.ChangeState(new EMuertoState(this, esm));
        return true;
    }
    // ... no murio: retrocede (codigo completo en las notas)
    return true;
}""", 28, 41),

    "code_player_start": ("""rb = GetComponent<Rigidbody>();
sprite_render = GetComponent<SpriteRenderer>();
sprite_animator = GetComponent<Animator>();
rb.useGravity = false;
rb.interpolation = RigidbodyInterpolation.Interpolate;
rb.collisionDetectionMode = CollisionDetectionMode.Continuous;
rb.constraints = RigidbodyConstraints.FreezeRotation;""", 28, 41),
}
