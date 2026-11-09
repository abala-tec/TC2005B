"""Dibuja las figuras de T8.8.1 con la réplica de S6_Grid (sim_bfs.py)."""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import sim_bfs as sim

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "figuras"
REG, SEM = str(ROOT / "fonts/Neuromax-Regular.otf"), str(ROOT / "fonts/Neuromax-SemiBold.otf")
INK, BODY, GRID = (19, 19, 21), (79, 83, 97), (205, 211, 224)
ORANGE, BLUE, PINK, GREEN = (240, 138, 60), (59, 111, 212), (232, 56, 109), (46, 139, 87)
WALL, WALL_LINE, FREE, YELLOW = (240, 150, 170), (190, 30, 80), (255, 255, 255), (255, 196, 0)
LIGHT_BLUE = (214, 228, 250)
S = 2


def F(p, n):
    return ImageFont.truetype(p, n * S)


def canvas(w, h):
    im = Image.new("RGB", (w * S, h * S), "white")
    return im, ImageDraw.Draw(im)


def save(im, name):
    im.resize((im.width // S, im.height // S), Image.LANCZOS).save(OUT / name)


def arrow(d, p0, p1, color, w=3, head=11):
    d.line([p0, p1], fill=color, width=w * S)
    a = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    pts = [p1] + [(p1[0] - head * S * math.cos(a + s), p1[1] - head * S * math.sin(a + s)) for s in (0.45, -0.45)]
    d.polygon(pts, fill=color)


class G:
    """Cuadrícula dibujada con z hacia arriba."""

    def __init__(self, d, ox, oy, cs, nx, nz):
        self.d, self.ox, self.oy, self.cs, self.nx, self.nz = d, ox * S, oy * S, cs * S, nx, nz

    def box(self, c):
        x0 = self.ox + c[0] * self.cs
        y1 = self.oy + (self.nz - c[1]) * self.cs
        return x0, y1 - self.cs, x0 + self.cs, y1

    def ctr(self, c):
        a, b, c2, d2 = self.box(c)
        return (a + c2) / 2, (b + d2) / 2

    def cell(self, c, fill=FREE, line=GRID, w=1):
        self.d.rectangle(self.box(c), fill=fill, outline=line, width=w * S)

    def text(self, c, t, font, fill=INK):
        self.d.text(self.ctr(c), t, font=font, fill=fill, anchor="mm")


# ------------------------------------------------------------- mapa de juguete
TOY_NX, TOY_NZ = 6, 4
TOY_WALLS = {(2, 0), (2, 1), (2, 2)}
TOY_S, TOY_M = (0, 1), (4, 1)
TOY_BLOQ = [[(x, z) in TOY_WALLS for z in range(TOY_NZ)] for x in range(TOY_NX)]


def toy_dist(limite=None):
    d = sim.distancias(TOY_S, TOY_BLOQ, TOY_M)   # se detiene al sacar M, como el código
    if limite is None:
        limite = d[TOY_M]   # no se dibuja nada más lejos que M
    return {c: v for c, v in d.items() if v <= limite}


def toy_grid(d, ox, oy, cs, numeros=None, vino=False, camino=None, coords=False, resaltar=None):
    g = G(d, ox, oy, cs, TOY_NX, TOY_NZ)
    fnt, fsm = F(SEM, int(cs * 0.42)), F(REG, int(cs * 0.22))
    for x in range(TOY_NX):
        for z in range(TOY_NZ):
            c = (x, z)
            if c in TOY_WALLS:
                g.cell(c, WALL, WALL_LINE, 2)
                continue
            fill = FREE
            if numeros is not None and c in numeros:
                fill = LIGHT_BLUE
            if camino and c in camino:
                fill = (255, 232, 150)
            if resaltar and c in resaltar:
                fill = (255, 214, 170)
            g.cell(c, fill)
            if numeros is not None and c in numeros and c not in (TOY_S, TOY_M):
                g.text(c, str(numeros[c]), fnt, BLUE)
            if coords:
                g.text(c, f"({x},{z})", fsm, BODY)
    for c, name, col in ((TOY_S, "S", ORANGE), (TOY_M, "M", PINK)):
        a, b, c2, d2 = g.box(c)
        g.d.rectangle((a, b, c2, d2), fill=col, outline=col)
        g.text(c, name + ("" if numeros is None else ("0" if name == "S" else (str(numeros[c]) if c in numeros else ""))), fnt, (255, 255, 255))
    return g


def label_axes(g, f):
    for x in range(g.nx):
        g.d.text((g.ox + (x + .5) * g.cs, g.oy + g.nz * g.cs + 6 * S), str(x), font=f, fill=BODY, anchor="mt")
    for z in range(g.nz):
        g.d.text((g.ox - 8 * S, g.oy + (g.nz - z - .5) * g.cs), str(z), font=f, fill=BODY, anchor="rm")


def fig_toy_inicial():
    im, d = canvas(720, 470)
    g = toy_grid(d, 70, 30, 100, coords=True)
    label_axes(g, F(SEM, 20))
    d.text((70 * S - 44 * S, 20 * S), "z", font=F(SEM, 22), fill=INK)
    d.text((70 * S + 6 * 100 * S + 6 * S, 30 * S + 4 * 100 * S + 6 * S), "x", font=F(SEM, 22), fill=INK, anchor="lt")
    save(im, "toy_inicial.png")


def fig_toy_olas():
    im, d = canvas(1500, 400)
    for i, lim in enumerate((0, 1, 2)):
        ox = 20 + i * 495
        toy_grid(d, ox, 56, 76, numeros=toy_dist(lim))
        d.text(((ox + 6 * 38) * S, 20 * S), f"Después de {lim} pasos" if lim != 1 else "Después de 1 paso",
               font=F(SEM, 24), fill=INK, anchor="mm")
    save(im, "toy_olas.png")


def fig_toy_completo():
    im, d = canvas(760, 470)
    nums = toy_dist()
    g = toy_grid(d, 80, 30, 100, numeros=nums)
    label_axes(g, F(SEM, 20))
    save(im, "toy_completo.png")


def fig_toy_vinode():
    im, d = canvas(760, 470)
    nums = toy_dist()
    path = sim.buscar_camino(TOY_S, TOY_M, TOY_BLOQ)
    vino = {}
    cola = [TOY_S]
    seen = {TOY_S}
    while cola:
        a = cola.pop(0)
        if a == TOY_M:
            break
        for dd in sim.DIRECCIONES:
            v = (a[0] + dd[0], a[1] + dd[1])
            if 0 <= v[0] < TOY_NX and 0 <= v[1] < TOY_NZ and v not in TOY_WALLS and v not in seen:
                seen.add(v); vino[v] = a; cola.append(v)
    g = toy_grid(d, 80, 30, 100, numeros=nums)
    for v, a in vino.items():
        if v not in nums:
            continue
        p0, p1 = g.ctr(v), g.ctr(a)
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        L = math.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        arrow(d, (p0[0] + ux * 16 * S, p0[1] + uy * 16 * S), (p0[0] + ux * 42 * S, p0[1] + uy * 42 * S), BODY, 3, 10)
    save(im, "toy_vinode.png")
    return vino


def fig_toy_camino():
    im, d = canvas(760, 470)
    path = sim.buscar_camino(TOY_S, TOY_M, TOY_BLOQ)
    g = toy_grid(d, 80, 30, 100, camino=set(path))
    pts = [g.ctr(TOY_S)] + [g.ctr(c) for c in path]
    for a, b in zip(pts[:-1], pts[1:]):
        d.line([a, b], fill=YELLOW, width=6 * S)
    # números de reconstrucción: de M hacia atrás
    rev = [TOY_M] + path[::-1][1:]
    for i, c in enumerate(rev):
        if c != TOY_M:
            d.text(g.ctr(c), str(i), font=F(SEM, 34), fill=(120, 60, 0), anchor="mm", stroke_width=4 * S, stroke_fill=(255, 232, 150))
    for c, name, col in ((TOY_S, "S", ORANGE), (TOY_M, "M", PINK)):
        a, b, c2, d2 = g.box(c)
        d.rectangle((a, b, c2, d2), fill=col)
        g.text(c, name, F(SEM, 42), (255, 255, 255))
    save(im, "toy_camino.png")


def fig_toy_recta():
    im, d = canvas(760, 470)
    g = toy_grid(d, 80, 30, 100)
    d.line([g.ctr(TOY_S), g.ctr(TOY_M)], fill=PINK, width=6 * S)
    x, y = g.ctr((2, 1))
    d.text((x, y), "✕", font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60 * S), fill=WALL_LINE, anchor="mm")
    save(im, "toy_recta.png")


# ------------------------------------------------------------- mapa real
def real_geom(cs):
    """Convierte coordenadas del mundo (0..25) a píxeles (z hacia arriba)."""
    ox, oy = 20 * S, 20 * S
    w = lambda x, z: (ox + x / sim.CELDA * cs * S, oy + (sim.ALTO - z / sim.CELDA) * cs * S)
    return ox, oy, w


def wall_polygon(p, w):
    px, pz, sx, sz, ang = p
    a = math.radians(ang)
    ux, uz = (math.cos(a), -math.sin(a)), (math.sin(a), math.cos(a))
    pts = []
    for sa, sb in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        x = px + sa * sx / 2 * ux[0] + sb * sz / 2 * uz[0]
        z = pz + sa * sx / 2 * ux[1] + sb * sz / 2 * uz[1]
        pts.append(w(x, z))
    return pts


def real_map(cs=14, celdas=False, heat=None, camino=None, marcas=True, paredes=True):
    n = sim.ANCHO
    im, d = canvas(40 + n * cs, 40 + n * cs)
    ox, oy, w = real_geom(cs)
    d.rectangle((ox, oy, ox + n * cs * S, oy + n * cs * S), fill=(247, 249, 252), outline=BODY, width=2 * S)
    maxd = max(heat.values()) if heat else 1
    for x in range(n):
        for z in range(n):
            x0, y1 = ox + x * cs * S, oy + (n - z) * cs * S
            box = (x0, y1 - cs * S, x0 + cs * S, y1)
            if celdas and sim.BLOQ[x][z]:
                d.rectangle(box, fill=WALL)
            elif heat is not None and (x, z) in heat:
                t = heat[(x, z)] / maxd
                col = (int(255 - t * 205), int(205 - t * 95), int(120 + t * 135))
                col = (int(255 * (1 - t) + 59 * t), int(214 * (1 - t) + 111 * t), int(150 * (1 - t) + 212 * t))
                d.rectangle(box, fill=col)
            if celdas or heat is not None:
                d.rectangle(box, outline=(220, 224, 232), width=1)
    if paredes:
        for p in sim.PAREDES:
            d.polygon(wall_polygon(p, w), outline=WALL_LINE, width=3 * S, fill=None if (celdas or heat) else WALL)
    if camino:
        pts = [w(*sim.celda_a_mundo(c)) for c in camino]
        d.line(pts, fill=YELLOW, width=4 * S, joint="curve")
    if marcas:
        e, j = w(22, 22), w(0.54, 0.44)
        r = 9 * S
        d.ellipse((e[0] - r, e[1] - r, e[0] + r, e[1] + r), fill=ORANGE, outline="white", width=2 * S)
        d.rectangle((j[0] - r, j[1] - r, j[0] + r, j[1] + r), fill=PINK, outline="white", width=2 * S)
    return im, d, w


def fig_real_sin_bfs():
    im, d, w = real_map(14, paredes=True)
    e, j = w(22, 22), w(0.54, 0.44)
    d.line([e, j], fill=PINK, width=4 * S)
    # marca donde la recta cruza una pared
    for t in [i / 400 for i in range(401)]:
        x, z = 22 + (0.54 - 22) * t, 22 + (0.44 - 22) * t
        if any(sim._toca(x, z, 0.01, p) for p in sim.PAREDES):
            px = w(x, z)
            r = 9 * S
            d.ellipse((px[0] - r, px[1] - r, px[0] + r, px[1] + r), outline=WALL_LINE, width=3 * S)
            break
    r = 9 * S
    d.ellipse((e[0] - r, e[1] - r, e[0] + r, e[1] + r), fill=ORANGE, outline="white", width=2 * S)
    d.rectangle((j[0] - r, j[1] - r, j[0] + r, j[1] + r), fill=PINK, outline="white", width=2 * S)
    save(im, "real_sin_bfs.png")


def fig_real_cuadricula():
    im, d, w = real_map(14, celdas=True)
    save(im, "real_cuadricula.png")


def fig_real_onda():
    cam = sim.buscar_camino(sim.mundo_a_celda(22, 22), sim.mundo_a_celda(0.54, 0.44))
    heat = sim.distancias(sim.mundo_a_celda(22, 22), meta=sim.mundo_a_celda(0.54, 0.44))
    im, d, w = real_map(14, celdas=True, heat=heat)
    save(im, "real_onda.png")


def fig_real_camino():
    ini, fin = sim.mundo_a_celda(22, 22), sim.mundo_a_celda(0.54, 0.44)
    cam = sim.buscar_camino(ini, fin)
    im, d, w = real_map(14, celdas=True, camino=[ini] + cam)
    save(im, "real_camino.png")


# ------------------------------------------------------------- conceptos
def fig_conversion():
    im, d = canvas(760, 520)
    nx, nz, cs = 6, 4, 100
    g = G(d, 80, 40, cs, nx, nz)
    for x in range(nx):
        for z in range(nz):
            g.cell((x, z), FREE)
    g.cell((3, 2), (255, 214, 170), ORANGE, 3)
    f = F(SEM, 20)
    for x in range(nx + 1):
        d.text((g.ox + x * g.cs, g.oy + nz * g.cs + 8 * S), f"{x * .5:g}", font=f, fill=BODY, anchor="mt")
    for z in range(nz + 1):
        d.text((g.ox - 10 * S, g.oy + (nz - z) * g.cs), f"{z * .5:g}", font=f, fill=BODY, anchor="rm")
    d.text((g.box((3, 2))[0] + 8 * S, g.box((3, 2))[1] + 6 * S), "casilla (3, 2)", font=F(SEM, 17), fill=(150, 70, 0), anchor="la")
    p = (g.ox + 1.8 / .5 * g.cs, g.oy + (nz - 1.3 / .5) * g.cs)
    r = 8 * S
    d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=PINK, outline="white", width=2 * S)
    d.text((g.box((3, 2))[2] + 14 * S, p[1] - 22 * S), "jugador\n(1.8, 1.3)", font=F(SEM, 20), fill=PINK, anchor="la")
    c = g.ctr((3, 2))
    d.ellipse((c[0] - 5 * S, c[1] + 28 * S - 5 * S, c[0] + 5 * S, c[1] + 28 * S + 5 * S), fill=BLUE)
    d.text((c[0] + 12 * S, c[1] + 28 * S), "centro (1.75, 1.25)", font=F(REG, 17), fill=BLUE, anchor="lm")
    d.text((g.ox + nx * g.cs / 2, 488 * S), "x del mundo (metros)", font=F(SEM, 20), fill=INK, anchor="mt")
    d.text((8 * S, 8 * S), "z del mundo", font=F(SEM, 20), fill=INK, anchor="lt")
    save(im, "conversion.png")


def fig_onda_abierta():
    im, d = canvas(660, 660)
    n, c0, cs = 9, (4, 4), 66
    g = G(d, 33, 33, cs, n, n)
    cols = [(255, 214, 170), (255, 232, 150), (200, 232, 205), (200, 222, 250), (225, 205, 245)]
    for x in range(n):
        for z in range(n):
            k = abs(x - c0[0]) + abs(z - c0[1])
            g.cell((x, z), cols[k] if k < 5 else FREE)
            if k < 5:
                g.text((x, z), str(k), F(SEM, 26), INK)
    save(im, "onda_abierta.png")


def fig_cola():
    im, d = canvas(1000, 330)
    f, fs = F(SEM, 26), F(REG, 21)
    d.text((10 * S, 22 * S), "COLA (Queue)", font=F(SEM, 24), fill=ORANGE, anchor="lm")
    items = ["(1,1)", "(1,2)", "(0,0)"]
    x0 = 150
    d.rounded_rectangle((x0 * S, 55 * S, (x0 + 560) * S, 125 * S), radius=14 * S, fill=(244, 247, 250), outline=BODY, width=2 * S)
    for i, t in enumerate(items):
        xx = x0 + 14 + i * 175
        d.rounded_rectangle((xx * S, 66 * S, (xx + 160) * S, 114 * S), radius=10 * S, fill=LIGHT_BLUE, outline=BLUE, width=2 * S)
        d.text(((xx + 80) * S, 90 * S), t, font=f, fill=INK, anchor="mm")
    arrow(d, (x0 * S - 100 * S, 90 * S), (x0 * S - 8 * S, 90 * S), GREEN, 4)
    arrow(d, ((x0 + 570) * S, 90 * S), ((x0 + 650) * S, 90 * S), PINK, 4)
    d.text((x0 * S - 104 * S, 130 * S), "SALE\n(Dequeue)", font=fs, fill=GREEN, anchor="ma", align="center")
    d.text(((x0 + 660) * S, 130 * S), "ENTRA\n(Enqueue)", font=fs, fill=PINK, anchor="ma", align="center")
    d.text((490 * S, 262 * S), "El primero que entra es el primero que sale (FIFO).", font=F(SEM, 24), fill=INK, anchor="mm")
    save(im, "cola.png")


def fig_diccionario():
    im, d = canvas(520, 330)
    d.text((10 * S, 22 * S), "DICCIONARIO vinoDe", font=F(SEM, 24), fill=BLUE, anchor="lm")
    rows = [("casilla", "vino de"), ("(0,1)", "(0,1)  (es el inicio)"), ("(1,1)", "(0,1)"), ("(0,0)", "(0,1)"), ("(1,2)", "(1,1)")]
    y = 52
    for i, (a, b) in enumerate(rows):
        fill = (43, 41, 61) if i == 0 else ((255, 255, 255) if i % 2 else (244, 247, 250))
        col = (255, 255, 255) if i == 0 else INK
        d.rectangle((10 * S, y * S, 510 * S, (y + 46) * S), fill=fill, outline=GRID, width=S)
        d.text((30 * S, (y + 23) * S), a, font=F(SEM, 22), fill=col, anchor="lm")
        d.text((200 * S, (y + 23) * S), b, font=F(REG if i else SEM, 22), fill=col, anchor="lm")
        y += 48
    save(im, "diccionario.png")


def fig_tiempo():
    im, d = canvas(1100, 300)
    f = F(SEM, 22)
    d.line([(40 * S, 150 * S), (1060 * S, 150 * S)], fill=BODY, width=3 * S)
    for i in range(5):
        x = 80 + i * 240
        d.ellipse(((x - 16) * S, 134 * S, (x + 16) * S, 166 * S), fill=ORANGE if i % 2 == 0 else BLUE)
        d.text((x * S, 205 * S), f"{i * .25:.2f} s", font=f, fill=INK, anchor="mt")
        if i % 1 == 0 and i < 4:
            pass
        d.text((x * S, 100 * S), "BFS" if True else "", font=f, fill=ORANGE if i % 2 == 0 else BLUE, anchor="mm")
        if i < 4:
            arrow(d, ((x + 30) * S, 150 * S), ((x + 210) * S, 150 * S), BODY, 3, 10)
            d.text(((x + 120) * S, 120 * S), "1 casilla", font=F(REG, 20), fill=BODY, anchor="mm")
    d.text((550 * S, 260 * S), "Cada 0.25 s: BFS recalcula y el enemigo avanza una casilla.", font=F(SEM, 22), fill=INK, anchor="mm")
    save(im, "tiempo.png")


def fig_vecinos():
    im, d = canvas(760, 340)
    for k, (ox, dirs, t) in enumerate(((60, sim.DIRECCIONES, "4 vecinos (el código)"),
                                       (420, sim.DIRECCIONES + [(1, 1), (1, -1), (-1, 1), (-1, -1)], "8 vecinos (extensión)"))):
        g = G(d, ox, 50, 80, 3, 3)
        for x in range(3):
            for z in range(3):
                g.cell((x, z), FREE)
        for dd in dirs:
            c = (1 + dd[0], 1 + dd[1])
            g.cell(c, (200, 232, 205), GREEN, 2)
            arrow(d, g.ctr((1, 1)), (g.ctr(c)[0] * .72 + g.ctr((1, 1))[0] * .28, g.ctr(c)[1] * .72 + g.ctr((1, 1))[1] * .28), GREEN, 3, 9)
        g.cell((1, 1), (255, 214, 170), ORANGE, 3)
        d.text(((ox + 120) * S, 310 * S), t, font=F(SEM, 22), fill=INK, anchor="mm")
    save(im, "vecinos.png")


def fig_checkbox():
    """Zoom a pared_6 (girada) con las casillas que BuscarCamino considera pared."""
    x0, z0, n, cs = 26, 26, 16, 40
    im, d = canvas(n * cs + 40, n * cs + 40)
    ox, oy = 20 * S, 20 * S
    w = lambda x, z: (ox + (x / sim.CELDA - x0) * cs * S, oy + (n - (z / sim.CELDA - z0)) * cs * S)
    for i in range(n):
        for j in range(n):
            cx, cz = x0 + i, z0 + j
            xx, yy = ox + i * cs * S, oy + (n - j) * cs * S
            fill = WALL if sim.BLOQ[cx][cz] else FREE
            d.rectangle((xx, yy - cs * S, xx + cs * S, yy), fill=fill, outline=GRID, width=S)
    d.polygon(wall_polygon(sim.PAREDES[5], w), outline=WALL_LINE, width=4 * S)
    save(im, "checkbox.png")


def fig_gizmos_leyenda():
    pass


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for fn in (fig_toy_inicial, fig_toy_olas, fig_toy_completo, fig_toy_vinode, fig_toy_camino, fig_toy_recta,
               fig_real_sin_bfs, fig_real_cuadricula, fig_real_onda, fig_real_camino, fig_conversion,
               fig_onda_abierta, fig_cola, fig_diccionario, fig_tiempo, fig_vecinos, fig_checkbox):
        fn()
    print("figuras listas")
