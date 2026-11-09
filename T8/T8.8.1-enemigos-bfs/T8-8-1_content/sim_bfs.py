"""Réplica en Python de S6_Grid.cs con los datos reales de escena6_enemigos.

Sirve para dibujar las figuras y para comprobar el algoritmo (python3 sim_bfs.py).
"""
import math
from collections import deque

ANCHO, ALTO, CELDA, MARGEN = 50, 50, 0.5, 0.1      # valores de la escena
ORIGEN = (12.5 - ANCHO * CELDA / 2, 12.5 - ALTO * CELDA / 2)  # Plane en (12.5, 12.5)

# (x, z, escala_x, escala_z, giro_y en grados) de pared_1 ... pared_6
PAREDES = [(6.13, 4.45, 10, 1, 0), (15.84, 9.38, 8, 1, 0), (5.85, 19.43, 8, 1, 0),
           (9.38, 16.31, 1, 5, 0), (19.34, 6.29, 1, 5, 0), (16.95, 16.71, 8, 1, 55.727)]
DIRECCIONES = [(1, 0), (-1, 0), (0, 1), (0, -1)]   # derecha, izquierda, arriba, abajo


def mundo_a_celda(x, z):
    return (math.floor((x - ORIGEN[0]) / CELDA), math.floor((z - ORIGEN[1]) / CELDA))


def celda_a_mundo(c):
    return (ORIGEN[0] + (c[0] + 0.5) * CELDA, ORIGEN[1] + (c[1] + 0.5) * CELDA)


def _toca(cx, cz, h, pared):
    """Caja alineada (centro, mitad h) contra rectángulo girado: prueba SAT en 2D."""
    px, pz, sx, sz, ang = pared
    a = math.radians(ang)
    ejes = [(1, 0), (0, 1), (math.cos(a), -math.sin(a)), (math.sin(a), math.cos(a))]
    ux, uz = ejes[2], ejes[3]
    for ex, ez in ejes:
        r1 = h * (abs(ex) + abs(ez))
        r2 = (sx / 2) * abs(ex * ux[0] + ez * ux[1]) + (sz / 2) * abs(ex * uz[0] + ez * uz[1])
        if abs((px - cx) * ex + (pz - cz) * ez) > r1 + r2:
            return False
    return True


def crear_bloqueada(ancho=ANCHO, alto=ALTO, margen=MARGEN):
    h = CELDA / 2 + margen
    return [[any(_toca(*celda_a_mundo((x, z)), h, p) for p in PAREDES)
             for z in range(alto)] for x in range(ancho)]


BLOQ = crear_bloqueada()


def libre(c, bloq=BLOQ):
    return 0 <= c[0] < len(bloq) and 0 <= c[1] < len(bloq[0]) and not bloq[c[0]][c[1]]


def buscar_camino(inicio, meta, bloq=BLOQ, traza=None):
    """Igual que S6_Grid.BuscarCamino: devuelve la lista sin 'inicio', o None."""
    if not libre(inicio, bloq) or not libre(meta, bloq):
        return None
    cola, vino_de = deque([inicio]), {inicio: inicio}
    while cola:
        actual = cola.popleft()
        if traza is not None:
            traza.append((actual, list(cola)))
        if actual == meta:
            break
        for d in DIRECCIONES:
            v = (actual[0] + d[0], actual[1] + d[1])
            if not libre(v, bloq) or v in vino_de:
                continue
            vino_de[v] = actual
            cola.append(v)
    if meta not in vino_de:
        return None
    camino, c = [], meta
    while c != inicio:
        camino.append(c)
        c = vino_de[c]
    return camino[::-1]


def distancias(inicio, bloq=BLOQ, meta=None):
    """Distancia de cada casilla descubierta. Con 'meta' se detiene igual que BuscarCamino
    (al sacar la meta de la cola), así que solo incluye lo que BFS realmente visitó."""
    dist = {inicio: 0}
    cola = deque([inicio])
    while cola:
        a = cola.popleft()
        if a == meta:
            break
        for d in DIRECCIONES:
            v = (a[0] + d[0], a[1] + d[1])
            if libre(v, bloq) and v not in dist:
                dist[v] = dist[a] + 1
                cola.append(v)
    return dist


if __name__ == "__main__":
    # comprobaciones
    assert mundo_a_celda(*celda_a_mundo((7, 9))) == (7, 9)
    assert mundo_a_celda(0.54, 0.44) == (1, 0)
    enemigo, jugador = mundo_a_celda(22, 22), mundo_a_celda(0.54, 0.44)
    assert libre(enemigo) and libre(jugador)
    cam = buscar_camino(enemigo, jugador)
    assert cam and cam[-1] == jugador and enemigo not in cam
    assert len(cam) == distancias(enemigo)[jugador]           # BFS = camino más corto
    assert all(abs(a[0]-b[0]) + abs(a[1]-b[1]) == 1 for a, b in zip([enemigo]+cam, cam))
    assert buscar_camino((0, 0), (0, 0)) == []
    cerrado = [[False] * 3 for _ in range(3)]
    cerrado[1] = [True] * 3
    assert buscar_camino((0, 0), (2, 2), cerrado) is None     # pared total: sin camino
    print("casillas bloqueadas:", sum(map(sum, BLOQ)), "de", ANCHO * ALTO)
    print("enemigo", enemigo, "jugador", jugador, "pasos", len(cam))
    print("OK")
