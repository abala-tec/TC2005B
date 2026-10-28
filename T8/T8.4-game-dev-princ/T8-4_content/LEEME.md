# T8.4 · id Software: Game Development Principles

Presentación del tema 8.4 del curso TC2005B: historia de id Software, el BSP de Doom, la raíz cuadrada inversa de Quake III y cinco principios de desarrollo.

## Contenido

- `T8.4-id-Software-Game-Development-Principles.pptx`: presentación de 20 diapositivas, formato 16:9, con notas del presentador en todas las diapositivas.
- `T8-4_content/`: imágenes, diagramas, código, tipografía y recursos usados en la presentación.
  - `img/`: capturas de juegos, retratos y una captura del editor de mapas.
  - `diagramas/`: diagramas del BSP, del vector unitario, de la tubería de la raíz cuadrada inversa, de barras y de error.
  - `codigo/`: imagen del código usada en la diapositiva 11.
  - `template/`: fondos y pixel art de la plantilla del curso.
  - `fonts/`: tipografía Neuromax (Regular y SemiBold) y su licencia.
  - `fast_inv_sqrt.c`: implementación portable del algoritmo de Quake III, sin comentarios y con líneas cortas.
  - `bsp_demo.py`: demo simplificada del recorrido de un árbol BSP.
  - `build_deck.py`: script que genera la presentación con python-pptx.
  - `make_diagrams.py`: script que genera los diagramas con matplotlib.
  - `make_code_images.py`: script que genera la imagen del código con Pygments y Pillow.
  - `creditos.md`: fuentes, licencias y enlaces completos.

## Estructura de la presentación

1. Portada y recorrido.
2. Historia de id Software y línea del tiempo (1990–2021).
3. BSP de Doom en tres diapositivas: el problema, la idea y el recorrido del árbol.
4. Raíz cuadrada inversa de Quake III: motivación, código, ejemplo paso a paso y comparación con otros métodos.
5. Cinco principios de desarrollo de id Software.
6. Síntesis, créditos y preguntas.

## Código

`fast_inv_sqrt.c` es una versión portable del código histórico. Usa `int32_t` y `memcpy` para evitar los problemas de `long` y de los punteros en máquinas de 64 bits. La función no lleva comentarios y respeta la indentación de 4 espacios usada en las otras presentaciones.

La diapositiva 11 muestra la función como imagen para que se lea bien en proyección. Las notas de esa diapositiva contienen el mismo código con espacios, listo para copiar y pegar. El archivo incluye además un `main` de prueba que imprime algunos valores.

La función supone un `float` de 32 bits IEEE 754 y `x > 0`. Es una adaptación didáctica del código histórico, no una rutina de producción.

`bsp_demo.py` no construye el árbol desde cero: usa un árbol pequeño ya definido y muestra el orden de recorrido para una cámara en cada zona. Es una demo didáctica del recorrido que se explica en las diapositivas 6 a 8, no un reemplazo del node builder de Doom.

## Tipografía

La presentación usa Neuromax (Regular y SemiBold). Para verla como está diseñada, instala los archivos de `T8-4_content/fonts/` en tu sistema. Si no está instalada, PowerPoint puede sustituirla y cambiar los saltos de línea.

Los tamaños siguen la plantilla `FINAL-plantilla-videojuegos.pptx`: títulos de 36 pt, títulos de bloque de 48 pt, subtítulos de 16 a 18 pt, cuerpos de 12 a 13 pt y código con tamaño legible en proyección.

## Cómo regenerar la presentación

```bash
cd T8-4_content
python3 make_diagrams.py
python3 make_code_images.py
python3 build_deck.py
```

Requiere `python-pptx`, `Pillow`, `Pygments`, `matplotlib` y `numpy`.

## Notas y fuentes

Todas las diapositivas tienen notas para el presentador. Las notas de la diapositiva de código incluyen el código completo y la ruta del archivo. Las notas de la diapositiva de créditos incluyen los enlaces completos.

Los datos, versiones y enlaces son de octubre de 2026. Las capturas de juegos son material con derechos de autor: se usan en baja resolución con fines educativos y sin fines comerciales. Las marcas pertenecen a sus dueños.
