### T8. Proceso de desarrollo de videojuegos — 30 h (semanas 13–16)
- **Contenido:**
  - 8.1 Historia de los juegos y conceptos basicos
  - 8.1.2 Conceptos básicos: mecánicas, dinámicas, estética, gameplay, reglas, retos y recompensas; el ciclo de juego (game loop).
  - 8.1.3 Elementos básicos de un juego 2D o 3D: escenas, sprites/modelos, cámara, sistema de coordenadas, HUD, menús, vidas y niveles.
  - 8.1.4 Generos de juegos, accion, aventura, puzzles, rogelike, etc etc..  
  - 8.1.5 Gameplay, el control es 90% del gameplay (interface humano computadora) (ultra breve introduccion al 8.8)
  
  - 8.2 Motores para el desarrollo de videojuegos
    - 8.2.1 Motores actuales: Unity, Unreal, Godot, Phaser y otros.
    - 8.2.2 Motores actuales: Unity (puntos fuertes y puntos debiles)
    - 8.2.3 Motores actuales: Godot (puntos fuertes y puntos debiles)
    - 8.2.4 Motores actuales: Unreal (puntos fuertes y puntos debiles)
    - 8.2.5 Selección del motor: criterios 2D/3D, lenguaje, licencia y costo, plataforma destino, curva de aprendizaje
    - 8.2.6 Por que en el curso vamos a usar Unity (flexible no solo sirve para hacer juegos, mas facil de usar, es mas ligero, usa codigo no BluePrints, Unity les puede servir para otras materias o trabajos (robotica, VR, control))
    - 8.2.7 Game Development en 2026. (AI asset driven games)

  - 8.3. GDD, Story Bible, Art Bible 
    - 8.3.1  Tecnicas de tradicionales de Ing de software y la verdadera manera en la que se disenan los juegos. (ing. de software tradicional, mata el proceso creativo) (comparar ing de Software para una Planta Electrica vs un juego que simula una planta electrica)
    - 8.3.2  What is a GDD (simple, hyperflexible, no-format document to ground down creativity)
    - 8.3.3  High-Level Pitch & Pillars (id software pilars a good example)
    - 8.3.4  Game Play Mechanics (progression, controls, win/loss conditions)
    - 8.3.5  World and Characters
    - 8.3.6  Game Art, Good game and animations enhance the gameplay an immersion (battletoads, pizza tower, cuphead, agregar videos de youtube de esos juegos )
    - 8.3.7  Technical tools definition. Definir las herramientas a usar y entender por que las estamos usando. (El elegir una herramienta mal es el veneno del Gamedev genera overengineer, dificulta de desarrollo, tiempos de desarrollo elevados, eleva costos tiempo=dinero )
    - 8.3.8. Actividad en clase. Hacer tu GDD, definir el genero del juego, el nombre, reglas, meta, historia, objetivo, gameloop, 

  - 8.4 Game Development Principles  
    - 8.4.1 Carmack y Romero  
    - 8.4.2 Carmack y Romero - modelo de distrubucion de Doom
    - 8.4.3 Carmack y Romero - 2 revoluciones tecnicaas Doom (tiempo real con hardware del carajo) Quake (3D que antecedio a los grandes)
    - 8.4.4 Id Software’s Core Development & Programming Principles. (No prototypes, KISS, Tools improve workflows, Dev is the Tester, Fix bug inmediately, Focus on the current game)

  - 8.5 Desarrollo e implementación:
    - 8.5.1 Unity basics, Escena, Gameobjects, Monobehaviour, game loop y temporización. (ejemplos con codigo en unity taller)
    - 8.5.2 Elementos básicos de la interfaz gráfica: menús, HUD y pantallas en Unity (ejemplos con codigo en unity  taller )

  - 8.6 Detalles tecnicos basicos:
    - 8.6.1 Matemáticas: cálculo de distancia, cálculo de ángulos con atan2 y vectores (suma y normalización) para movimiento y persecución. (ejemplos en Unity, taller)
    - 8.6.2.1 script para seguir con la camara al jugador 
    - 8.6.2.2 escalar el juego, plano mas grandes y spawner de enemigos (gameobject instansing) 
    - 8.6.2.2.1 resolver bugs,  
    - 8.6.2.3 materiales introduccion (cambiar el color del piso)
    - 8.6.2.4 implementar efecto 2.5 D como paper mario

    - 8.6.3 Collisiones: collision de 2 rectangulos version naive y version optima.  (ejemplos en Unity, taller)
    - 8.6.4 Collisiones: collision de 2 cubos en 3d (solucion optima) (ejemplo con Unity, taller )
    - 8.6.5 Busqueda de collisiones: hash grid simple en 2D para busqueda y collision (ejemplo con Unity, taller) 
    
  - 8.9 Interacción humano-computadora en videojuegos:
    - 8.9.1 Controles, la interface entre el humano y la maquina.  (90% del Gameplay)
    - 8.9.2 Ejemplos de mecanicas (Quake 3 hyper rapido, controles tanque Redient Evil, proyect zomboid)
    - 8.9.3 Mecanica de movimiento de Mario Bros 3 en Unity (curva de acelaracion y salto, basado en Mario Bros 3) (ejemplo con Unity taller )
    - 8.9.4 Basic Enemies usando finite state machines. (taller unity)

  - 8.10 Generacion de assets. 
    - 8.10.1 Generacion de modelos 3d con herramientas de IA. (meshy.ai - Mixamo) (taller)


- **Objetivo:** diseñar, construir e implantar un videojuego 2D o 3D con física, colisiones, controles y audio básicos.

- **En clase (10 h):** 
- laboratorio de Unity: taller de diseño: Escribir GDD (1 h) LAPIZ Y PAPEL;
- laboratorio de Unity: gameloop, conceptos basicos, gameobjects, graficos y componentes (1 h).
- laboratorio de Unity: escena, sprites, gameloop, cámara (2 h)
- laboratorio de Unity  Mario Bros 3 controles en Unity (3 h)
- laboratorio de Unity: colisiones, controles, game loop (2 h)
- laboratorio de Unity: draft del primer juego (1 h).

- **Tarea (20 h):** escena y personaje con controles (4 h); física y colisiones (5 h); interfaz, retroalimentación y dificultad (4 h); audio y pulido (3 h); pruebas con usuarios y ajustes (2 h); documentación de diseño y licencias (2 h).

- **Evaluación:** juego jugable en la demostración final (Reto, 6%, incluye el documento de diseño con casos de uso y diagramas de clase); playtesting (actividad en clase); parte del Examen 3.




