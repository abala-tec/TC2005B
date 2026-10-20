# Temario — TC2005B Construcción de Software y Toma de Decisiones

## Datos generales

| Dato | Valor |
|---|---|
| Clave | TC2005B |
| Créditos | 8 UDC |
| Duración | 16 semanas |
| Horas totales | 160 h (≈10 h por semana: clase + trabajo independiente) |
| Requisitos | Haber cursado TI1015 y haber cursado TC1004B |
| Evaluación | Módulos de aprendizaje 60% (exámenes 20% · actividades en clase 15% · tareas y casos 25%) · Reto integrador 40% |

> El desglose 60/40 proviene del plan de estudios; los porcentajes internos son una propuesta para organizar la evaluación. Cada tema indica sus horas de clase y de trabajo independiente (tarea).

## Calendario de temas

| Semana | Tema | Horas |
|---|---|---|
| 1 | T1. Metodologías ágiles (3 h) + inicio T2 | 10 |
| 2 | T2. Análisis y diseño | 10 |
| 3 | T2. Análisis y diseño | 10 |
| 4 | T2. Análisis y diseño | 10 |
| 5 | T2. Análisis y diseño | 10 |
| 6 | T2 (cierre) + T3. Calidad en el software | 10 |
| 7 | T4. Despliegue + inicio T5. Desarrollo Web | 10 |
| 8 | T5. Desarrollo Web | 10 |
| 9 | T5. Desarrollo Web | 10 |
| 10 | T5 (cierre) + inicio T6. Sistema transaccional | 10 |
| 11 | T6. Sistema transaccional | 10 |
| 12 | T6. Sistema transaccional | 10 |
| 13 | T6 (cierre) + T7. Toma de decisiones + inicio T8 | 10 |
| 14 | T8. Desarrollo de videojuegos | 10 |
| 15 | T8. Desarrollo de videojuegos | 10 |
| 16 | T8 (cierre) + Evaluación final | 10 |

Total: 160 horas.

## Temas, actividades y tareas

### T1. Metodologías ágiles en el desarrollo de software — 3 h (semana 1)
- **Contenido:**
  - 1.1 Iteraciones en el desarrollo ágil: sprint (meta, duración e incremento), backlog de producto y de sprint, historias de usuario («Como… quiero… para…»), criterios de aceptación y velocidad del equipo.
  - 1.2 Actores: responsabilidades del Product Owner, el Scrum Master y el equipo de desarrollo; relación con los stakeholders y usuarios.
  - 1.3 Ejemplos de metodologías: Scrum (planeación, daily, revisión, retrospectiva), Kanban (tablero, límite de trabajo en progreso) y XP (programación en pares, TDD); criterios para elegir la adecuada.
  - 1.4 Proceso completo de desarrollo de software: fases (requerimientos, diseño, construcción, pruebas, despliegue, mantenimiento); cascada vs. iterativo; relación con el reto del semestre.
  - 1.5 Especificación de requerimientos con un estándar propietario: funcionales, de información y no funcionales; estructura del documento; atributos de un buen requerimiento (completo, consistente, verificable, no ambiguo).
  - 1.6 Casos de uso y diagramas de actividad: actores, escenario principal y alternativos, precondiciones y postcondiciones; decisiones y carriles (swimlanes).
  - 1.7 Importancia de la especificación orientada al usuario: costo de corregir un error según la fase en que se detecta; validación con el cliente.
- **Objetivo:** adaptar un marco ágil al equipo y redactar la primera versión de los requerimientos del reto con un estándar.
- **En clase (1 h):** mapear los roles y ceremonias de Scrum sobre un caso; definir el protocolo de equipo (roles, tablero, acuerdos) y redactar en conjunto la primera historia de usuario del sistema.
- **Tarea (2 h):** redactar 3 historias de usuario con criterios de aceptación y el borrador de requerimientos funcionales y no funcionales; entregarlo en el repositorio del equipo (mismo que se usará todo el curso).
- **Evaluación:** aporta al documento de requerimientos (Reto, 4%) y al portafolio de equipo; sin examen.

### T2. Análisis y diseño del software — 50 h (semanas 1–6)
- **Contenido:**
  - 2.1 Design thinking:
    - 2.1.1 Proceso (empatizar, definir, idear, prototipar, evaluar) aplicado al desarrollo de software.
    - 2.1.2 Especificaciones de usabilidad: eficacia, eficiencia, satisfacción y accesibilidad.
    - 2.1.3 Perfil del usuario: técnicas de observación y encuestas.
    - 2.1.4 Personas, ambientes de trabajo y escenarios de uso.
    - 2.1.5 Diseño de interfaz, heurísticas de Nielsen y storyboard de pantallas.
  - 2.2 Herramientas de generación automática de código a partir de modelos: ingeniería directa e inversa, generación desde diagramas de clases y ORM (Hibernate, Entity Framework, Sequelize); alcances y límites.
  - 2.3 Diagramas de UML:
    - 2.3.1 Secuencia: líneas de vida, mensajes, activaciones.
    - 2.3.2 Interacción: visión general y de comunicación.
    - 2.3.3 Clases: atributos, métodos, visibilidad, relaciones, herencia y multiplicidad.
    - 2.3.4 Estados: estados, transiciones y eventos.
    - 2.3.5 Componentes: interfaces y dependencias.
    - 2.3.6 Objetos: instancias y enlaces de un escenario.
  - 2.4 Patrón Modelo-Vista-Controlador: responsabilidades de cada capa, flujo de una petición y ventajas de mantenibilidad.
  - 2.5 Arquitectura cliente-servidor: capas, separación front-end/back-end, la API como contrato y comunicación por red.
  - 2.6 Modelo relacional:
    - 2.6.1 Conceptos: PK, FK, grado, cardinalidad y reglas de integridad (entidad, referencial y de dominio).
    - 2.6.2 Mapeo de diagramas de clases a tablas relacionales (normalización hasta tercera forma normal).
    - 2.6.3 Álgebra relacional (selección, proyección, unión, intersección, diferencia, producto cartesiano y joins) y su equivalencia con SQL.
    - 2.6.4 SQL DDL: CREATE/ALTER/DROP, tipos de datos y restricciones (PK, FK, UNIQUE, CHECK, NOT NULL).
    - 2.6.5 SQL DML: INSERT/UPDATE/DELETE; SELECT con joins, GROUP BY/HAVING, subconsultas y vistas.
    - 2.6.6 Procedimientos almacenados y triggers: sintaxis, parámetros y casos de uso (auditoría, validación, cálculos).
    - 2.6.7 Transacciones: propiedades ACID, COMMIT/ROLLBACK y savepoints.
    - 2.6.8 Control de concurrencia (bloqueos y niveles de aislamiento) y recuperación (bitácora, respaldo y restauración).
- **Objetivo:** modelar el sistema del reto (interfaz, clases, arquitectura y base de datos) y demostrar su base de datos funcionando con SQL.
- **En clase (15 h):** entrevista al cliente y elaboración de personas y escenarios (2 h); storyboard de las pantallas principales validado con heurísticas (2 h); talleres de UML sobre el caso del reto — secuencia e interacción (1 h), clases (2 h), estados, componentes y objetos (2 h); generación automática de código desde el modelo (1 h); laboratorios de base de datos — DDL (1 h), DML (2 h), trigger y procedimiento (1 h), transacciones y concurrencia (1 h).
- **Tarea (35 h):** investigación del usuario y modelado del sistema: requerimientos, personas y storyboard (6 h); diagramas de UML completos del sistema (10 h); modelo relacional y normalización (4 h); script DDL (3 h); consultas y reportes con DML (5 h); trigger, procedimiento y pruebas de transacciones (4 h); práctica de generación de código con herramienta (3 h).
- **Evaluación:** diagramas de UML (Reto, 5%), storyboard y diseño de interfaz (Reto, 3%), modelo relacional con DDL y DML (Reto, 6%); Examen 1 (semana 6: T1–T2, metodologías, design thinking y UML).

### T3. Calidad en el software — 7 h (semana 6)
- **Contenido:**
  - 3.1 Generación de casos de prueba: definir qué quiere probar el usuario; criterios de aceptación; trazabilidad requerimiento → caso de prueba; estructura del caso (ID, precondición, datos, pasos y resultado esperado).
  - 3.2 Pruebas estáticas y manuales: revisión de código e inspecciones; análisis estático con linters; pruebas exploratorias y de aceptación ejecutadas a mano.
  - 3.3 Pruebas de caja blanca: caminos de ejecución, cobertura de líneas y ramas, complejidad ciclomática para elegir qué caminos probar.
  - 3.4 Pruebas unitarias: frameworks por lenguaje (JUnit, Jest, NUnit), ciclo TDD (rojo-verde-refactor) y uso de mocks y stubs.
  - 3.5 Pruebas funcionales: caja negra, particiones de equivalencia, valores límite y pruebas de regresión.
- **Objetivo:** diseñar y ejecutar pruebas que demuestren el cumplimiento de los requerimientos del sistema.
- **En clase (2 h):** taller de casos de prueba de un módulo del reto con trazabilidad a los requerimientos; ejercicio de particiones de equivalencia y valores límite sobre un formulario; demostración del framework de pruebas unitarias del lenguaje elegido.
- **Tarea (5 h):** escribir y ejecutar pruebas unitarias de dos módulos del sistema y medir su cobertura; elaborar el manual de pruebas del reto (casos funcionales de punta a punta con criterios de aceptación).
- **Evaluación:** manual de pruebas (Reto, 3%, se entrega con el sistema en la semana 13); reporte de cobertura (tarea); parte del Examen 2 (semana 10).

### T4. Despliegue de software — 4 h (semana 7)
- **Contenido:**
  - 4.1 Manual de usuario: estructura (índice, guías por tarea, capturas y solución de dudas frecuentes); redacción para público no técnico.
  - 4.2 Manual de instalación: requisitos de hardware y software, pasos reproducibles, configuración, respaldo y solución de problemas comunes.
  - 4.3 Control de versiones: Git (repositorio, commits, ramas, merge, resolución de conflictos, pull request) y GitHub (README, issues, historial); buenas prácticas de mensajes de commit.
- **Objetivo:** desplegar el software en un entorno de operación y documentar su instalación y su uso.
- **En clase (2 h):** taller de Git/GitHub sobre el repositorio del reto: rama por funcionalidad, un merge con conflicto resuelto y un pull request revisado; redacción del manual de instalación de un sistema conocido siguiendo la plantilla del curso.
- **Tarea (2 h):** instalar el sistema de otro equipo siguiendo su manual y reportar los pasos confusos; iniciar el manual de instalación del sistema propio.
- **Evaluación:** repositorio en GitHub con historial y ramas (parte del sistema web del Reto, 6%); manuales de instalación y usuario (Reto, 4%); parte del Examen 2.

### T5. Desarrollo Web — 30 h (semanas 7–10)
- **Contenido:**
  - 5.1 Front-end:
    - 5.1.1 HTML5: estructura semántica (header, nav, main, section, footer), tablas, formularios con validación nativa y atributos de accesibilidad.
    - 5.1.2 CSS3: selectores, box model, unidades, flexbox, grid, media queries y diseño mobile-first.
    - 5.1.3 JavaScript: DOM (selección y manipulación), eventos, validación en cliente, fetch con promesas/async-await y manejo de JSON.
    - 5.1.4 Marcos y herramientas responsivas: Bootstrap (grid y componentes) y jQuery (selectores y eventos).
  - 5.2 Back-end:
    - 5.2.1 Servicios REST: recursos, URIs, verbos HTTP, códigos de estado y JSON; diseño de endpoints.
    - 5.2.2 Lenguaje de alto nivel (Node.js/Express, Java/Spring, C#/ASP.NET, PHP o Ruby): rutas, controladores, middleware, validación de entrada y conexión a la base de datos.
    - 5.2.3 Marcos y herramientas para servicios REST: Postman/Thunder Client (colecciones y entornos), CORS y consumo de la API desde el front-end.
- **Objetivo:** construir el front-end responsivo y el back-end REST del sistema del reto y conectarlos.
- **En clase (10 h):** laboratorio de maquetación responsiva con HTML y CSS (2 h); laboratorio de JavaScript: validación de formulario y consumo de API con fetch (2 h); laboratorio de Bootstrap/jQuery (1 h); laboratorio de API REST con conexión a base de datos (3 h); laboratorio de Postman, CORS e integración front-back (2 h).
- **Tarea (20 h):** maquetación de las pantallas del storyboard (6 h); lógica del front-end con fetch (4 h); endpoints REST del sistema (6 h); integración, corrección de errores y demo de avance (4 h).
- **Evaluación:** sistema web en GitHub (Reto, 6%); demos de sprint (actividades en clase); parte del Examen 3 (semana 15).

### T6. Sistema transaccional — 30 h (semanas 10–13)
- **Contenido:**
  - 6.1 Definición de requerimientos del sistema responsivo con estándar propietario:
    - 6.1.1 Requerimientos funcionales: operaciones transaccionales (altas, bajas, cambios, consultas y reportes).
    - 6.1.2 Requerimientos de información: entidades, atributos, volúmenes y retención de datos.
    - 6.1.3 Requerimientos no funcionales: tiempos de respuesta, disponibilidad, usabilidad y seguridad.
  - 6.2 Diseño de la aplicación web:
    - 6.2.1 Diagrama de clases que satisface los requerimientos de información.
    - 6.2.2 Base de datos creada a partir del modelo relacional normalizado.
    - 6.2.3 Datos de prueba y reportes generados con DML.
    - 6.2.4 Back-end: servicios REST con acceso a datos, validaciones y seguridad básica.
    - 6.2.5 Front-end: pantallas responsivas conectadas al back-end.
  - 6.3 Despliegue y pruebas: puesta en operación con el manual de instalación, ejecución del manual de pruebas y corrección de defectos.
- **Objetivo:** integrar el sistema transaccional completo (requerimientos, diseño, implementación, pruebas y despliegue) y validarlo con el cliente.
- **En clase (12 h):** planeación y revisión de sprints (2 h); asesorías de requerimientos, diagrama de clases y modelo relacional (2 h); asesorías de back-end (2 h); asesorías de front-end (2 h); prueba de integración con el manual de pruebas (2 h); ensayo de despliegue con el manual de instalación (2 h).
- **Tarea (18 h):** correcciones de requerimientos y diseño (4 h); base de datos, datos y reportes (3 h); back-end (5 h); front-end (4 h); documentación y preparación de la demostración (2 h).
- **Evaluación:** documento de requerimientos (Reto, 4%); arquitectura del sistema (Reto, 3%); demos por sprint (actividades); validación del cliente y despliegue (Reto, 4%).

### T7. Proceso de toma de decisiones — 3 h (semana 13)
- **Contenido:**
  - 7.1 Identificación de indicadores de desempeño: qué es un KPI (medible, relevante y periódico) y cómo derivarlo de los procesos del sistema.
  - 7.2 Reportes que generan estadísticas: consultas de agregación (COUNT, SUM, AVG) que alimentan cada indicador.
  - 7.3 Métodos matemáticos: regresión lineal simple (ajuste por mínimos cuadrados, pendiente y coeficiente de correlación) para identificar patrones y tendencias.
  - 7.4 Interacciones causa-efecto entre indicadores: análisis de correlación y la precaución de no confundir correlación con causalidad.
  - 7.5 Visualización gráfica: tipo de gráfica según el dato (líneas para tendencia, barras para comparación, dispersión para correlación) y tablero (dashboard) que apoye la decisión.
- **Objetivo:** obtener indicadores del sistema, encontrar patrones con regresión y sustentar una decisión con visualizaciones.
- **En clase (1 h):** taller con datos del sistema del reto: calcular un KPI, ajustar una regresión lineal en hoja de cálculo e interpretarla en parejas.
- **Tarea (2 h):** reporte breve con 3 KPIs del sistema, una regresión con su interpretación y 2 visualizaciones que sustenten una decisión.
- **Evaluación:** reporte de indicadores (actividad en clase); parte del Examen 3.

### T8. Proceso de desarrollo de videojuegos — 30 h (semanas 13–16)
- **Contenido:**
  - 8.1 Conceptos básicos: mecánicas, dinámicas y estética; reglas, retos y recompensas; el ciclo de juego (game loop).
  - 8.2 Tipos de juegos: géneros (acción, aventura, arcade, puzzle, simulación) y plataformas (PC, móvil, consola, web).
  - 8.3 Industria de videojuegos: roles (diseñador, programador, artista, QA, productor), modelos de negocio (premium, free-to-play, suscripción) y mercado nacional y global.
  - 8.4 Elementos básicos de un juego 2D o 3D: escenas, sprites/modelos, cámara, sistema de coordenadas, HUD, menús, vidas y niveles.
  - 8.5 Conceptos de ciencias básicas:
    - 8.5.1 Matemáticas: cálculo de distancia (euclidiana y Manhattan), cálculo de ángulos con atan2 y vectores (suma y normalización) para movimiento y persecución.
    - 8.5.2 Física: gravedad, rigidez, fricción, volumen y masa aplicados con cuerpos rígidos (rigid bodies) y su efecto en el movimiento.
  - 8.6 Motores para el desarrollo de videojuegos:
    - 8.6.1 Motores actuales: Unity, Unreal, Godot, Phaser y otros.
    - 8.6.2 Selección del motor: criterios (2D/3D, lenguaje, licencia y costo, plataforma destino, curva de aprendizaje) y elección justificada para el juego del equipo.
  - 8.7 Interacción humano-computadora en videojuegos:
    - 8.7.1 Definición de requerimientos del videojuego (mecánicas y reglas esperadas).
    - 8.7.2 Modelación de usuarios: perfiles de jugador, habilidades y motivaciones.
    - 8.7.3 Escenarios y casos de uso del videojuego.
    - 8.7.4 Especificaciones de usabilidad: retroalimentación, controles, dificultad y tutorial.
  - 8.8 Diseño de un videojuego 2D o 3D:
    - 8.8.1 Casos de uso del videojuego (iniciar partida, perder, guardar).
    - 8.8.2 Diagramas de clase del videojuego (entidades, relaciones y responsabilidades).
  - 8.9 Desarrollo e implementación:
    - 8.9.1 Elementos básicos de la interfaz gráfica: menús, HUD y pantallas.
    - 8.9.2 Distribución de los elementos según la resolución (layout y puntos de anclaje).
    - 8.9.3 Detección y manejo de colisiones (AABB y círculos).
    - 8.9.4 Interacción con el usuario: controles de teclado, ratón y táctiles.
    - 8.9.5 Hilos de ejecución: game loop y temporización.
    - 8.9.6 Uso de música y efectos de sonido.
    - 8.9.7 Retroalimentación al usuario a través de hápticos (vibración).
  - 8.10 Derechos de autor:
    - 8.10.1 Imágenes y audio: dominio público, licencias Creative Commons y atribución.
    - 8.10.2 Licencias de software: MIT, GPL y propietarias; licencias de motores y recursos.
- **Objetivo:** diseñar, construir e implantar un videojuego 2D o 3D con física, colisiones, controles y audio básicos.
- **En clase (10 h):** taller de matemáticas aplicadas al juego — distancia, ángulos y persecución (1 h); laboratorio del motor: escena, sprites, cámara y HUD (2 h); laboratorio de física: gravedad, masa, fricción y rigidez (2 h); taller de diseño: requerimientos, casos de uso y diagramas de clase del juego (2 h); laboratorio de mecánicas: colisiones, controles, game loop, audio y hápticos (2 h); playtesting entre equipos y auditoría de licencias (1 h).
- **Tarea (20 h):** escena y personaje con controles (4 h); física y colisiones (5 h); interfaz, retroalimentación y dificultad (4 h); audio y pulido (3 h); pruebas con usuarios y ajustes (2 h); documentación de diseño y licencias (2 h).
- **Evaluación:** juego jugable en la demostración final (Reto, 6%, incluye el documento de diseño con casos de uso y diagramas de clase); playtesting (actividad en clase); parte del Examen 3.

## Evaluación

### Módulos de aprendizaje — 60%
| Componente | Descripción | Valor |
|---|---|---|
| Exámenes | 3 exámenes parciales (ver tabla) | 20% |
| Actividades en clase | Una actividad evaluada por semana: ejercicios cortos, quizzes de 10 min, talleres y demos de avance | 15% |
| Tareas y casos | Tareas por tema: UML, SQL, Git, front-end/back-end y videojuego | 25% |

### Exámenes — 20%
| Examen | Semana | Temas | Valor |
|---|---|---|---|
| Examen 1 | 6 | T1 y T2 (metodologías, design thinking y UML) | 6% |
| Examen 2 | 10 | T2 (modelo relacional, DDL, DML y transacciones), T3 y T4 | 7% |
| Examen 3 | 15 | T5, T7 y T8 | 7% |

### Reto integrador — 40%
| Evidencia | Entrega | Valor |
|---|---|---|
| Documento de requerimientos | Semana 6 (versión final: semana 11) | 4% |
| Storyboard y diseño de interfaz | Semana 7 | 3% |
| Diagramas de UML (clases, secuencia y estados) | Semana 8 | 5% |
| Modelo relacional, DDL y DML | Semana 10 | 6% |
| Arquitectura del sistema | Semana 11 | 3% |
| Sistema web (código en GitHub) | Semana 13 | 6% |
| Manual de pruebas | Semana 13 | 3% |
| Videojuego (diseño + demo jugable) | Semana 16 | 6% |
| Despliegue del software + manuales de instalación y usuario | Semanas 13–16 | 4% |

La semana 16 incluye 3 h de evaluación final: demostración del sistema transaccional y del videojuego ante el grupo y el cliente, con rúbrica global del reto.

## Bibliografía
- I. Sommerville, *Software Engineering*, 10th ed., Pearson, 2016.
- T. M. Connolly, *Database Systems: A Practical Approach to Design, Implementation and Management*, 5th ed., Addison-Wesley, 2010.
- J. Hocking, *Unity in Action: Multiplatform Game Development in C#*, Manning, 2015.
- J. Duckett, *Web Design with HTML, CSS, JavaScript and jQuery Set*, Wiley, 2014 (consulta).
