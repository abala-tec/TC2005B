# Guía corta: sprite 2D, sombra y volteo

Esta guía resume los pasos de las capturas del bloque 04. Todos los pasos se hacen
en Unity 6, con el proyecto `Sample_Game`.

## 1. Instalar 2D Sprite

1. Abre `Window > Package Management > Package Manager`.
2. Elige `Unity Registry`.
3. Busca `2D Sprite`.
4. Presiona `Install` y espera a que Unity termine.

## 2. Convertir la imagen en sprite

1. Selecciona `Assets/Images/velma_sprite_walk_2.png`.
2. En el Inspector, cambia `Texture Type` a `Sprite (2D and UI)`.
3. Cambia `Sprite Mode` a `Multiple`.
4. Presiona `Apply`.

## 3. Cortar la hoja

1. Presiona `Open Sprite Editor`.
2. Elige `Slice > Grid By Cell Size`.
3. Escribe `48` en X y `75` en Y.
4. Elige `Pivot Center`.
5. Presiona `Slice` y después `Apply`.

La hoja queda dividida en siete cuadros:

- `velma_sprite_walk_2_0`
- `velma_sprite_walk_2_1`
- ...
- `velma_sprite_walk_2_6`

## 4. Crear el objeto del sprite

1. Crea un objeto hijo del `Cube`.
2. Renómbralo `velma_sprite_walk`.
3. Agrega un `Sprite Renderer`.
4. Asigna el sprite `velma_sprite_walk_2_0`.
5. Agrega un `Animator` y asigna el controlador `velma_sprite_walk_2_0`.

El objeto es hijo del cubo. Cuando el cubo se mueve, el sprite se mueve con él.

## 5. Ajustar tamaño y posición

En el Transform del sprite:

| Campo | Valor |
|---|---|
| Position | `(0, 0.348, 0)` |
| Scale | `(2.47, 2.47, 2.47)` |

La altura `0.348` coloca los pies cerca del piso. La escala `2.47` hace que el
sprite cubra la caja.

## 6. Sombra

1. En el `Sprite Renderer`, activa `Cast Shadows`.
2. Activa `Receive Shadows`.
3. Crea un material `SpriteMaterial` en `Assets/Materiales`.
4. Cambia su shader a `Universal Render Pipeline / Lit`.
5. Asigna el material al `Sprite Renderer`.
6. Activa `Alpha Clipping` con umbral `0.5`.
7. Cambia `Render Face` a `Both`.

La `Directional Light` de la escena debe estar activa para que la sombra se vea.

## 7. Volteo con flipX

En el `Sprite Renderer`, la casilla `Flip X` refleja el sprite:

- `Flip X` desactivado: el personaje mira a la derecha.
- `Flip X` activado: el personaje mira a la izquierda.

El código del cubo cambia `sprite.flipX` cuando se presionan las flechas o las
teclas A y D.
