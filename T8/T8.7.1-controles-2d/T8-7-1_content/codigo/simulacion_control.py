"""Réplica en Python de la lógica de Update() de S5_VelmaWalk_2D.cs.

Sirve para dibujar las gráficas de la presentación sin abrir Unity.
Usa un paso fijo de 1/60 s. No simula colisiones: el suelo está en y = 0.
"""

WALK, RUN = 5.625, 9.375
ACC = BRAKE = 12.3046875
JUMP, GRAV, JGRAV, HOLD, MAXFALL = 13.125, 70.3125, 14.0625, 7.5, 15.0
DT = 1 / 60


def sign(x):
    return (x > 0) - (x < 0)


def move_towards(cur, target, delta):
    """Igual que Mathf.MoveTowards."""
    if abs(target - cur) <= delta:
        return target
    return cur + sign(target - cur) * delta


def paso(st, inp, run, jump_pressed, jump_held):
    """Un cuadro de Update(). st = dict con vx, vy, y, grounded."""
    vx, vy, g = st["vx"], st["vy"], st["grounded"]
    if g and vy <= 0:
        vy = 0.0
    top = RUN if run else WALK
    if inp != 0:
        target = inp * top
        if sign(vx) == sign(inp) and abs(vx) > top:
            if g:
                vx = move_towards(vx, target, BRAKE * DT)
        else:
            vx = move_towards(vx, target, ACC * DT)
    elif g:
        vx = move_towards(vx, 0.0, BRAKE * DT)
    if jump_pressed and g:
        vy, g = JUMP, False
    if not g:
        light = jump_held and vy > HOLD
        vy -= (JGRAV if light else GRAV) * DT
        vy = max(vy, -MAXFALL)
    y = st["y"] + vy * DT
    if y <= 0 and vy <= 0:          # suelo simple
        y, g = 0.0, True
    return {"vx": vx, "vy": vy, "y": y, "grounded": g, "x": st["x"] + vx * DT}


def correr_caso(cuadros, entrada):
    """entrada(i) -> (inp, run, jump_pressed, jump_held). Devuelve la lista de estados."""
    st = {"vx": 0.0, "vy": 0.0, "y": 0.0, "x": 0.0, "grounded": True}
    out = [st]
    for i in range(cuadros):
        st = paso(st, *entrada(i))
        out.append(st)
    return out


if __name__ == "__main__":
    # Caminar 1 s: debe llegar a walkSpeed en unos 0.46 s.
    t = correr_caso(60, lambda i: (1, False, False, False))
    assert abs(t[-1]["vx"] - WALK) < 1e-9
    # Salto corto vs largo.
    corto = correr_caso(120, lambda i: (0, False, i == 0, False))
    largo = correr_caso(120, lambda i: (0, False, i == 0, True))
    h_corto = max(s["y"] for s in corto)
    h_largo = max(s["y"] for s in largo)
    assert h_largo > 3 * h_corto
    print(f"altura salto corto: {h_corto:.2f}  salto largo: {h_largo:.2f}")
