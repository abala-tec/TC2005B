"""Convierte las constantes de SMB3 (píxeles y cuadros) a unidades de Unity.

1 tile = 16 píxeles y el juego corre a 60 cuadros por segundo.
  velocidad:   px/cuadro   * 60   / 16 = tiles/s
  aceleración: px/cuadro²  * 3600 / 16 = tiles/s²
"""

FPS = 60
TILE = 16

# nombre: (valor en px/cuadro, es aceleración)
SMB3 = {
    "walkSpeed": (0x18 / 16, False),        # $18 = 1.5
    "runSpeed": (0x28 / 16, False),         # $28 = 2.5
    "acceleration": (0.0546875, True),
    "braking": (0.0546875, True),
    "jumpSpeed": (0x38 / 16, False),        # $38 = 3.5
    "gravity": (5 / 16, True),
    "jumpGravity": (1 / 16, True),
    "jumpHoldLimit": (0x20 / 16, False),    # $20 = 2
    "maxFallSpeed": (0x40 / 16, False),     # $40 = 4
}

UNITY = {  # valores escritos en S5_VelmaWalk_2D.cs
    "walkSpeed": 5.625, "runSpeed": 9.375, "acceleration": 12.3046875,
    "braking": 12.3046875, "jumpSpeed": 13.125, "gravity": 70.3125,
    "jumpGravity": 14.0625, "jumpHoldLimit": 7.5, "maxFallSpeed": 15.0,
}


def a_unity(px_cuadro, aceleracion):
    factor = FPS * FPS if aceleracion else FPS
    return px_cuadro * factor / TILE


if __name__ == "__main__":
    for nombre, (valor, acel) in SMB3.items():
        u = a_unity(valor, acel)
        assert abs(u - UNITY[nombre]) < 1e-9, nombre
        print(f"{nombre:14s} {valor:<10} px/cuadro -> {u} unidades")
    print("Todas las constantes coinciden con el script.")
