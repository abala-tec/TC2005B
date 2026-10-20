partida_activa = True

while partida_activa:
    dt = tiempo_del_frame()
    leer_controles()
    actualizar(dt)
    dibujar()
