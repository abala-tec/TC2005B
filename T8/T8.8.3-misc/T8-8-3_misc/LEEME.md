# T8.8.3 · Audio, piedras arrastrables y Animator

Presentación `../T8.8.3-Miscelaneos.pptx` (portada + 25 diapositivas).

El tema cubre tres sistemas de `Assets/Scripts/escena8_misc`:

1. **Audio**: GameObject `Sonidos`, componentes `AudioSource` y
   `S8_SoundControl`, música en `Awake`, efectos con `PlayOneShot`.
2. **Piedras arrastrables**: `Physics.Raycast` con `ScreenPointToRay`,
   `Rigidbody` kinematic mientras se arrastra, teclado para mover y
   recálculo de `S8_Grid` al caer.
3. **Animator y knockback**: el Animator Controller como máquina de estados,
   sus parámetros (`Bool` y `Trigger`), `Exit Time`, el hachazo de Velma
   (timer + esfera) y el empuje que recibe Velma cuando el enemigo la golpea.

> **Actualización (combate con hachazo):** las diapositivas 2, 6, 8, 17, 18,
> 19, 20, 21, 22, 23, 24 y 25 (y sus notas) se editaron directamente en el
> PPTX, sin regenerar el deck. Se respetaron los recortes y los textos que se
> habían puesto encima de las figuras (por ejemplo "Background music" en la
> diapositiva 8). `snippets.py`, `make_figures.py`, las imágenes afectadas de
> `codigo/` y `figuras/`, y `csharp/` ya tienen la versión nueva.
> **`build_deck.py` y los `manifest.json` NO están actualizados**: si se corre
> el build, vuelve a generar el deck con el texto viejo (patada / cono /
> kickBack) y se pierden las ediciones hechas a mano en el PPTX.
> Ver `Unity_Sample/Sample_Game/Assets/Scripts/escena9_final/CAMBIOS_COMBATE.md`.

## Estructura

- `csharp/`: copia exacta de los scripts usados en la escena.
  - `S8_SoundControl.cs`
  - `S8_RockDragDrop.cs`
  - `S8_VelmaWalk_3D.cs`
  - `S8_Grid.cs`
  - `S8_EnemigoCilindro.cs`
- `animator/velma_sprite_walk_2_0.controller`: controlador real que se
  explica en las diapositivas 19-22.
- `img/`: capturas de Unity del proceso de importar, colocar y configurar
  la piedra.
- `figuras/`: diagramas de audio, raycast, estados de la piedra, grid,
  máquina de estados del Animator, vector de empuje y línea de tiempo.
- `codigo/`: imágenes del código que aparece en las diapositivas. El mismo
  fragmento está en las notas de cada diapositiva.
- `snippets.py`: texto de los fragmentos de código.
- `make_code_images.py`: genera `codigo/`.
- `make_figures.py`: genera `figuras/`.
- `build_deck.py`: construye el PPTX, audita el texto de los PNG y valida
  la plantilla del curso.
- `figuras/manifest.json` y `codigo/manifest.json`: tamaño mínimo de fuente
  y dimensiones de cada PNG.

## Regenerar

```bash
cd T8/T8.8.3-misc/T8-8-3_misc
python3 make_code_images.py
python3 make_figures.py
python3 build_deck.py   # ¡ojo! sobrescribe el PPTX editado a mano (ver arriba)
```

El build usa `video-juegos/template/deck_style.py` y
`video-juegos/template/validate_deck.py`. Si el validador estricto falla, no
reemplaza el PPTX final.

## Notas de la escena

- Escena: `Assets/Scenes/escena8_misc.unity`.
- Audio: GameObject `Sonidos` con `AudioSource` y `S8_SoundControl`.
  `Play On Awake` y `Loop` están apagados en el Inspector. La música se
  asigna en `Awake` y se reproduce con `Play()`.
- El campo `won` está declarado y asignado a
  `metal-slug-mission-complete.mp3`, pero el código actual no lo reproduce.
- Piedras: `piedra_1`, `piedra_2` y `piedra_3`, capa `Paredes`, con
  `BoxCollider`, `Rigidbody` kinematic y `S8_RockDragDrop`.
- El grid usa celdas de `0.5`; `rockStep = 2.0` es un múltiplo de la celda.
- Animator: capa `Base Layer`, estado por defecto `VelmaWalking`, parámetros
  `isRunning`, `isJumping`, `isDucking` (Bool), `hack` y `push` (Trigger).
  (Antes el trigger era `kick` y el estado `VelmaKick`.)
- `VelmaHack` y `VelmaDrop` vuelven a `VelmaWalking` con `Exit Time = 1` y
  sin condiciones.
- Hachazo (tecla F): `SetTrigger("hack")` y `hachazoTimer = 0.25 s`; mientras
  dura, `RevisarHachazo()` usa `Physics.OverlapSphere` enfrente de Velma
  (capa `Enemigos`). Ya no se consulta el Animator con `IsName` y ya no hay
  impulso hacia adelante. El enemigo muere de 1 hachazo si patrulla y de 3
  si persigue; si no muere, retrocede. Al morir se apagan collider y
  Rigidbody.
- Knockback: `CheckEnemyHit` (en Enter y Stay) ignora golpes durante
  `invulnerableTiempo = 1 s`; `GolpeVelma` usa `golpe_angulo = 120°` (ya no
  el cono de visión). Velma calcula `away`, lo aplana en Y, lo normaliza,
  activa `velma_empujada` y la invulnerabilidad. El `Update` aplica
  `empuje_dir * knockBack` de inmediato (ya no espera el suelo) y dispara
  el trigger `push`.

## Texto de los PNG

Cada figura y cada imagen de código declara su fuente mínima en un
`manifest.json`. `build_deck.py` calcula el tamaño efectivo con el ancho real
de la imagen en la diapositiva y **falla el build si algún PNG queda por
debajo de 12 pt**. La salida muestra una línea `OK` o `FAIL` por imagen.

Para mantener el mínimo, las figuras usan menos etiquetas y textos más
cortos que en una versión de escritorio. Si una figura se coloca más angosta,
la auditoría la rechaza.

La auditoría cubre los diagramas y las imágenes de código generados. Las
capturas de Unity (`img/`) son evidencia de la escena y no se auditan: su
texto pertenece a la interfaz del editor.

## Código en las imágenes

Las líneas largas se parten para que se lean en la diapositiva. Los
comentarios largos se omiten de las imágenes y del fragmento de las notas.
En `S8_SoundControl.cs` la imagen muestra `play_jump` y `play_airWush`; el
marcador `// ...` indica que `play_hit` y `play_hachazo` se omitieron. La lógica
y los tokens mostrados son los mismos. Los archivos completos y sin cambios
están en `csharp/`.

## Referencias

- `AudioSource.PlayOneShot`:
  https://docs.unity3d.com/ScriptReference/AudioSource.PlayOneShot.html
- Parámetros del Animator:
  https://docs.unity3d.com/Manual/AnimationParameters.html
- Animator Controller:
  https://docs.unity3d.com/Manual/AnimatorControllers.html
