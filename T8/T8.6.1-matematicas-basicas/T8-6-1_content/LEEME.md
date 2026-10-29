# T8.6.1 · Matemáticas básicas para videojuegos

Presentación del tema 8.6.1 del curso TC2005B. El objetivo es usar distancia, vectores y ángulos con `atan2` para mover una esfera enemiga y detectar cuándo el cubo cae sobre ella.

## Contenido

- `../T8.6.1-Matematicas-basicas.pptx`: presentación de 28 diapositivas en formato 16:9, con notas del presentador en todas las diapositivas.
- `EnemigoEsfera.cs`: código final del enemigo, copiado del proyecto `Unity_Intro_3`.
- `CubeMove.cs`: código base del cubo, copiado del proyecto `Unity_Intro_3`.
- `codigo/`: imágenes del código usadas en las diapositivas. Cada diapositiva con código tiene el fragmento correspondiente en sus notas.
- `img/`: capturas del proceso recortadas y diagramas de distancia y ángulo.
- `template/`: fondos y pixel art de la plantilla del curso.
- `fonts/`: tipografía Neuromax (Regular y SemiBold) y su licencia.
- `build_deck.py`: script que genera la presentación con `python-pptx`.
- `make_code_images.py`: script que genera las imágenes del código con Pygments.

Las capturas originales se conservan en `../screenshots/`.

## Tipografía

La presentación usa Neuromax (Regular y SemiBold). Para verla como está diseñada, instala los archivos de `fonts/` en tu sistema. Si la tipografía no está instalada, PowerPoint puede sustituirla y cambiar los saltos de línea.

Los tamaños siguen la plantilla `FINAL-plantilla-videojuegos.pptx`: títulos de 36 pt, títulos de bloque de 48 pt, subtítulos de 16 a 18 pt, cuerpos de 12 a 16 pt, etiquetas de 9.5 a 10.5 pt y código como imagen para que se lea en proyección.

## Proyecto de Unity

El proyecto de ejemplo está en `../Unity_Intro_3/Unity_Intro_3/`. Se creó con Unity 6.3 LTS y la plantilla Universal 3D (URP).

La escena de trabajo está en `Assets/Scenes/SampleScene.unity`. El script del enemigo está en `Assets/EnemigoEsfera.cs` y el script base del cubo está en `Assets/CubeMove.cs`.

La jerarquía principal es:

```text
Plane
Cube
Enemigo
Canvas
  GamePanel
    Text (TMP)
    Caidas
    Button
```

El cubo conserva el movimiento, el salto y el contador de caídas de T8.5.2. El enemigo es una esfera con `Rigidbody` en modo `Is Kinematic` y un `Sphere Collider` de radio 0.5.

## Cómo regenerar la presentación

```bash
cd T8-6-1_content
python3 make_code_images.py
python3 build_deck.py
```

El script requiere `python-pptx`, `Pillow` y `Pygments`. Las imágenes de código usan DejaVu Sans Mono.

## Fuentes

- Capturas de Unity 6.3 y VS Code: elaboradas para este curso.
- Proyecto `Unity_Intro_3` y código `EnemigoEsfera.cs`: material del curso TC2005B.
- Guía `guia-enemigo-esfera.md`, figuras y diagramas: material del curso.
- Unity Manual:
  - https://docs.unity3d.com/ScriptReference/Vector3.html
  - https://docs.unity3d.com/ScriptReference/Mathf.Atan2.html
  - https://docs.unity3d.com/ScriptReference/MonoBehaviour.InvokeRepeating.html
  - https://docs.unity3d.com/Manual/class-Rigidbody.html
