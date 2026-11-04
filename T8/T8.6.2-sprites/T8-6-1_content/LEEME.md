# T8.6.2 · Cámara, materiales y sprites

Presentación de 49 diapositivas del tema 8.6.2 del curso TC2005B. Explica cómo
seguir al cubo con la cámara, agrandar el plano, crear un spawner de esferas,
cambiar el material del piso y convertir al personaje en un sprite 2D con sombra
y volteo.

## Archivo principal

`../T8.6.2-Camara-Materiales-Sprites.pptx`

## Orden de los bloques

1. **Cámara:** crear `S4_CameraFollower`, agregarlo a Main Camera, asignar el
   Target y explicar `LateUpdate` con `Vector3.Lerp`.
2. **Escenario:** escalar el plano a 100 × 100, moverlo a `(-45, 0, -45)`, crear
   el objeto `Spawner` y generar 50 esferas con `Instantiate` y `Random.Range`.
3. **Materiales:** crear `Grass`, elegir el color base verde y asignarlo al
   `Mesh Renderer` del plano.
4. **Sprites:** instalar el paquete 2D Sprite, cortar la hoja en siete cuadros,
   crear el objeto hijo del cubo, activar la sombra y voltear con `flipX`.

## Contenido de esta carpeta

| Carpeta o archivo | Contenido |
|---|---|
| `bg.png` | Fondo pixel art de la plantilla |
| `decor/` | Sprites decorativos de la plantilla |
| `fonts/` | Tipografías Neuromax, su licencia y las fuentes incrustadas en el `.pptx` |
| `figuras/` | Diagramas de escala, Lerp y radio del spawner |
| `img/` | Capturas de pantalla del proceso en Unity y assets del sprite |
| `codigo/` | Imágenes de código, scripts y explicaciones de los algoritmos |
| `make_code_images.py` | Genera las imágenes de código con resaltado de sintaxis |
| `make_diagrams.py` | Genera las figuras |
| `build_deck.py` | Construye el archivo `.pptx` |

## Código

- `codigo/S4_CameraFollower.cs`: script de la cámara.
- `codigo/S4_Spawner.cs`: script del spawner.
- `codigo/S4_CubeMove.cs`: script del cubo con la referencia al sprite y el
  cambio de `flipX`.
- `codigo/algoritmo_camara.md`: explicación del offset y de `Lerp`.
- `codigo/algoritmo_spawner.md`: explicación de `Instantiate`, del bucle y de
  `Random.Range`.
- `codigo/algoritmo_flip.md`: explicación de `SpriteRenderer.flipX`.
- `codigo/guia_sprite_2d.md`: pasos para importar, cortar, iluminar y voltear el
  sprite.

## Notas de la presentación

Cada diapositiva tiene notas. En las diapositivas que muestran código, las notas
incluyen el código correspondiente y una explicación breve.

## Cómo regenerar

```bash
python3 make_code_images.py
python3 make_diagrams.py
python3 build_deck.py
```

El último comando escribe el `.pptx` en la carpeta padre.

El build usa la escala de `video-juegos/template/deck_style.py` y valida el
archivo en modo estricto antes de reemplazar el `.pptx`. Si hay un tamaño fuera
de escala, una fuente incorrecta o una caja desbordada, el build se detiene y
deja intacto el archivo anterior.

Para revisar el resultado:

```bash
python3 ../../../video-juegos/template/validate_deck.py --strict \
  ../T8.6.2-Camara-Materiales-Sprites.pptx

python3 ../../../video-juegos/template/render_deck.py \
  ../T8.6.2-Camara-Materiales-Sprites.pptx ../review
```

## Fuentes

- `docs/TC2005B-T8_editado.md`, tema 8.6.2.
- `T8/Unity_Sample/Sample_Game/Assets/Scripts/escena4_hash_grid/`.
- `T8/Unity_Sample/Sample_Game/Assets/Scenes/escena4_sprites.unity`.
- Capturas de pantalla del proceso en Unity.
- Plantilla `video-juegos/template/FINAL-plantilla-videojuegos.pptx`.
- Documentación de Unity: `Vector3.Lerp`, `LateUpdate`, `Instantiate`,
  `Random.Range` y `SpriteRenderer.flipX`.

## Nota sobre derechos

El sprite de Velma se usa como ejemplo educativo dentro del proyecto del curso.
Los personajes y las marcas pertenecen a sus dueños. La tipografía Neuromax se
distribuye con su propia licencia en `fonts/1001fonts-neuromax-eula.txt`.
