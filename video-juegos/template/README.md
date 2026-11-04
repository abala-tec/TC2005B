# Kit de presentaciones TC2005B

La plantilla `FINAL-plantilla-videojuegos.pptx` es la fuente de verdad para
tamaños, fuentes y proporción de diapositiva. Los decks nuevos se construyen
con `deck_style.py`, no con tamaños escritos a mano.

## Regla principal

Cada texto declara un rol. El rol fija tamaño, fuente y peso.

| Rol | Tamaño | Uso |
|---|---:|---|
| `label` | 9.5 | Etiquetas de sección, pasos, kicker |
| `caption` | 14 | Pie de imagen o nota breve |
| `note` | 14 | Texto secundario |
| `body` | 16 | Cuerpo principal |
| `subtitle` | 20 | Subtítulo |
| `card_title_sm` | 20 | Título de tarjeta pequeño |
| `card_title` | 24 | Título de tarjeta |
| `title` | 36 | Título de diapositiva |
| `section` | 48 | Título de sección |
| `closing` | 80 | Cierre o pregunta final |
| `table_head` | 20 | Encabezado de tabla |
| `table_body` | 16 | Cuerpo de tabla |

Si un texto no cabe a 16 pt, no se baja la fuente. Se recorta el texto o se
parte la diapositiva. Las excepciones se declaran como un rol nuevo en
`deck_style.py`, con su razón.

## Construir un deck

1. Copia `build_deck_template.py` a la carpeta del tema.
2. Usa `new_deck()`, `add_slide()` y `add_text(..., role="body")`.
3. Guarda en un archivo temporal.
4. Ejecuta el validador en modo estricto.
5. Solo si pasa, reemplaza el `.pptx` final.

```python
from deck_style import add_slide, add_text, new_deck
from validate_deck import validate

prs = new_deck()
s = add_slide(prs)
add_text(s, 0.62, 1.18, 11.95, 0.40, "Una idea.", role="body")

tmp = OUT.with_suffix(".tmp.pptx")
prs.save(tmp)
report = validate(tmp, strict=True)
if report.errors:
    print(report.format())
    raise SystemExit(1)
tmp.replace(OUT)
```

## Validar

```bash
# Deck generado con el kit: falla si hay tamaños fuera de escala
python video-juegos/template/validate_deck.py --strict deck.pptx

# Deck viejo o editado a mano: solo reporta
python video-juegos/template/validate_deck.py --audit deck.pptx
```

El modo estricto comprueba:

- proporción 13.333 × 7.5;
- tema Neuromax;
- rol, tamaño, fuente y peso de cada run;
- ausencia de `normAutofit` y `spAutoFit`;
- desbordamiento estimado con la fuente real;
- formas dentro de la diapositiva;
- tamaños de tabla.

## Revisión visual

El validador no detecta solapamientos ni problemas de composición. Para eso:

```bash
python video-juegos/template/render_deck.py deck.pptx T8/<tema>/review
```

Eso genera `slide-001.png`, ... y `contact-sheet.jpg` dentro del workspace.
Después se lanza un subagente de revisión con la rúbrica de
`.opencode/agents/deck-reviewer.md` sobre esas imágenes. Su reporte es
consultivo; no bloquea el build. La carpeta `review/` está en `.gitignore`.

## Archivos

```text
video-juegos/template/
  FINAL-plantilla-videojuegos.pptx
  deck_style.py
  validate_deck.py
  render_deck.py
  build_deck_template.py
  fonts/
```

## Límites

La medición de desbordamiento usa las métricas de Neuromax y una tolerancia de
0.05 in. PowerPoint y LibreOffice pueden partir líneas distinto. La revisión
visual final sigue siendo necesaria.
