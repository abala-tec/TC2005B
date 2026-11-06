"""Réplica en Python de la parte horizontal de Update() de S5_VelmaWalk_3D.cs.

Sirve para dibujar las figuras de la presentación y para comprobar las cuentas
sin abrir Unity. Usa un paso fijo de 1/60 s. Un vector es una tupla (x, z).
Ejecuta el archivo para correr las comprobaciones.
"""
import math

WALK, RUN = 5.625, 9.375
ACC = BRAKE = 12.3046875
MAXH = 15.0
DT = 1 / 60


def length(v):
    return math.hypot(v[0], v[1])


def normalizar(v):
    """Igual que Vector2.Normalize cuando la longitud es mayor que 1."""
    n = length(v)
    return (v[0] / n, v[1] / n) if n > 1 else v


def move_towards(cur, target, delta):
    """Igual que Vector2.MoveTowards: avanza en línea recta hacia target."""
    dx, dz = target[0] - cur[0], target[1] - cur[1]
    dist = math.hypot(dx, dz)
    if dist <= delta or dist == 0:
        return target
    return (cur[0] + dx / dist * delta, cur[1] + dz / dist * delta)


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def paso(h, inp, run, grounded, normalize=True):
    """Un cuadro del movimiento horizontal. Devuelve la nueva velocidad (x, z)."""
    if normalize:
        inp = normalizar(inp)
    top = RUN if run else WALK
    if inp != (0, 0):
        target = (inp[0] * top, inp[1] * top)
        n = length(h)
        same = n * n > 0.01 and dot((h[0] / n, h[1] / n), inp) > 0.1
        if same and n > top:
            if grounded:
                h = move_towards(h, target, BRAKE * DT)
        else:
            h = move_towards(h, target, ACC * DT)
    elif grounded:
        h = move_towards(h, (0, 0), BRAKE * DT)
    if length(h) > MAXH:
        h = (h[0] / length(h) * MAXH, h[1] / length(h) * MAXH)
    return h


def correr(frames, inp, run=False, grounded=True, normalize=True, h=(0.0, 0.0)):
    """Lista de velocidades (x, z), una por cuadro."""
    out = []
    for _ in range(frames):
        h = paso(h, inp, run, grounded, normalize)
        out.append(h)
    return out


if __name__ == "__main__":
    # La diagonal sin normalizar mide 1.414; normalizada mide 1.
    assert abs(length((1, 1)) - math.sqrt(2)) < 1e-9
    assert abs(length(normalizar((1, 1))) - 1) < 1e-9
    # Caminando en diagonal se llega a walkSpeed, no a 41 % más.
    assert abs(length(correr(120, (1, 1))[-1]) - WALK) < 1e-6
    # Sin normalizar, la velocidad real sería 7.95 u/s (el tope solo aplica al correr).
    assert abs(length(correr(120, (1, 1), normalize=False)[-1]) - WALK * math.sqrt(2)) < 1e-6
    # Tarda 5.625 / 12.3046875 = 0.457 s en llegar a walkSpeed.
    assert abs(WALK / ACC - 0.4571) < 1e-3
    # Soltar las teclas: en el suelo frena, en el aire conserva la velocidad.
    h = correr(60, (1, 0))[-1]
    assert correr(60, (0, 0), h=h, grounded=True)[-1] == (0, 0)
    assert correr(60, (0, 0), h=h, grounded=False)[-1] == h
    # Correr en diagonal sin pasar del tope absoluto de 15 u/s.
    assert length(correr(300, (1, 1), run=True)[-1]) <= MAXH
    print("simulacion_control_3d: todo bien")
