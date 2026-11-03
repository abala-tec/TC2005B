# T8.6.1 · Matemáticas para enemigos

Presentación de 35 diapositivas (30 de contenido, portada y cuatro separadores) del tema 8.6.1 del curso TC2005B. Explica la distancia, los vectores, la patrulla entre esquinas, el pisotón con `atan2` y la persecución del jugador.

## Archivo principal

`../T8.6.1-Matematicas-para-enemigos.pptx`

## Contenido de esta carpeta

| Carpeta o archivo | Contenido |
|---|---|
| `bg.png` | Fondo pixel art de la plantilla |
| `decor/` | Sprites decorativos de la plantilla |
| `fonts/` | Tipografías Neuromax, su licencia y las fuentes incrustadas en el `.pptx` |
| `figuras/` | Diagramas de distancia, vectores, patrulla, ángulo y persecución |
| `img/` | Capturas de pantalla del proceso en Unity |
| `codigo/` | Imágenes de código y copias de los scripts |
| `make_code_images.py` | Genera las imágenes de código con resaltado de sintaxis |
| `make_diagrams.py` | Genera las figuras |
| `build_deck.py` | Construye el archivo `.pptx` |

## Código

- `codigo/EnemigoEsfera.cs`: copia del script usado en la escena.
- `codigo/CubeMoveMath.cs`: copia del script del cubo, con el salto.
- `codigo/algoritmo_persecucion.md`: explicación de la persecución, que no estaba en la guía original.

## Notas de la presentación

Cada diapositiva tiene notas. En las diapositivas que muestran código, las notas incluyen el código correspondiente y una explicación breve.

## Cómo regenerar

```bash
python3 make_code_images.py
python3 make_diagrams.py
python3 build_deck.py
```

El último comando escribe el `.pptx` en la carpeta padre.

## Fuentes

- `guia-enemigo-esfera.md`
- `T8/Unity_Sample/Sample_Game/Assets/Scripts/escena3_math/EnemigoEsfera.cs`
- `T8/Unity_Sample/Sample_Game/Assets/Scripts/escena3_math/CubeMoveMath.cs`
- Capturas de pantalla de `screenshots/`
- Plantilla `video-juegos/template/FINAL-plantilla-videojuegos.pptx`
