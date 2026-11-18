# T8.8.3 · Audio, piedras arrastrables y Animator

Presentación `../T8.8.3-Miscelaneos.pptx` (portada + 25 diapositivas).

El tema cubre tres sistemas de `Assets/Scripts/escena8_misc`:

1. **Audio**: GameObject `Sonidos`, componentes `AudioSource` y
   `S8_SoundControl`, música en `Awake`, efectos con `PlayOneShot`.
2. **Piedras arrastrables**: `Physics.Raycast` con `ScreenPointToRay`,
   `Rigidbody` kinematic mientras se arrastra, teclado para mover y
   recálculo de `S8_Grid` al caer.
3. **Animator y kickback**: el Animator Controller como máquina de estados,
   sus parámetros (`Bool` y `Trigger`), `Exit Time`, `IsName`, y el empuje
   que recibe Velma cuando el enemigo la golpea.

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
python3 build_deck.py
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
  `isRunning`, `isJumping`, `isDucking` (Bool), `kick` y `push` (Trigger).
- `VelmaKick` y `VelmaDrop` vuelven a `VelmaWalking` con `Exit Time = 1` y
  sin condiciones.
- Kickback: `CheckEnemyHit` calcula `away`, lo aplana en Y, lo normaliza y
  activa `velma_empujada`. El `Update` aplica `empuje_dir * kickBack` y
  dispara el trigger `push`.

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
marcador `// ...` indica que `play_hit` y `play_kick` se omitieron. La lógica
y los tokens mostrados son los mismos. Los archivos completos y sin cambios
están en `csharp/`.

## Referencias

- `AudioSource.PlayOneShot`:
  https://docs.unity3d.com/ScriptReference/AudioSource.PlayOneShot.html
- Parámetros del Animator:
  https://docs.unity3d.com/Manual/AnimationParameters.html
- Animator Controller:
  https://docs.unity3d.com/Manual/AnimatorControllers.html
