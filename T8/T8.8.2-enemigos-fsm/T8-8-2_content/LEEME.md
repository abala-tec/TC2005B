# T8.8.2 · Enemigos con máquina de estados finitos

Presentación `../T8.8.2-Enemigos-FSM.pptx` (portada + 25 diapositivas de contenido).

El tema explica la FSM del enemigo de `escena7_fsm`: los estados Patrullar,
Perseguir y Muerto; la visión con cono y raycast; la animación y detección del
hachazo de Velma; y el material físico sin fricción de las paredes.

> **Actualización (combate con hachazo):** las diapositivas 2, 3, 4, 5, 11, 21, 22,
> 23, 26 y 27 (y sus notas) se editaron directamente en el PPTX, sin regenerar el
> deck. `snippets.py`, `make_figures.py`, `codigo/`, `figuras/fsm_diagrama.png` y
> `csharp/` ya tienen la versión nueva. **`build_deck.py` NO está actualizado**:
> si se corre, vuelve a generar el deck con el texto viejo (patada / cono).
> Ver `Unity_Sample/Sample_Game/Assets/Scripts/escena9_final/CAMBIOS_COMBATE.md`.

## Contenido

- `csharp/`: copia exacta de los scripts usados en la escena.
  - `IEnemyState.cs`
  - `EnemyStateMachine.cs`
  - `EnemigoCilindro.cs`
  - `EPatrolState.cs`
  - `EPerseguirState.cs`
  - `EMuertoState.cs`
  - `S7_VelmaWalk_3D.cs`
  - `S7_Grid.cs`
- `img/`: capturas de Unity de la escena, del Inspector, del Animator, del
  Animation window, del Sprite Editor y de la consola.
- `codigo/`: imágenes del código que aparecen en las diapositivas. Son recortes
  de los scripts, ajustados para caber en la diapositiva; el mismo fragmento está
  en las notas de cada diapositiva. Los archivos completos y sin cambios están
  en `csharp/`.
- `figuras/`: diagramas de la FSM, del cono de visión, de los seis sprites de
  la patada y de la fricción.
- `ParedesMaterial.physicMaterial`: copia del material físico de las paredes,
  con fricción dinámica y estática en 0.
- `snippets.py`: texto de los fragmentos de código.
- `make_code_images.py`: genera `codigo/`.
- `make_figures.py`: genera `figuras/`.
- `build_deck.py`: construye y valida el PPTX con la plantilla del curso.

## Regenerar

```bash
cd T8/T8.8.2-enemigos-fsm/T8-8-2_content
python3 make_code_images.py
python3 make_figures.py
python3 build_deck.py   # ¡ojo! build_deck.py tiene el texto viejo (ver arriba)
```

El build usa `video-juegos/template/deck_style.py` y
`video-juegos/template/validate_deck.py`. Si el validador estricto falla, no
reemplaza el PPTX final.

## Notas de la escena

- La escena es `Assets/Scenes/escena7_fsm.unity`.
- El enemigo usa `EnemigoCilindro`; la FSM no es un componente, se crea en
  `Start()`.
- La visión usa `vision_rango = 8`, `vision_angulo = 90` y un `Physics.Raycast`.
- El hachazo (tecla F) dispara el trigger `hack` del Animator y activa una
  esfera (`Physics.OverlapSphere`) enfrente de Velma durante 0.25 s; solo
  cuenta la capa `Enemigos`. Ya no hay impulso hacia adelante.
- El enemigo muere de 1 hachazo si patrulla y de 3 (`golpes_persiguiendo`) si
  persigue; si no muere, retrocede. Al morir se apagan su collider y su
  Rigidbody.
- Las paredes usan `ParedesMaterial` con fricción dinámica y estática en 0 y
  `Friction Combine = Minimum`.
