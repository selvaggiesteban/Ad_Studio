# ad_studio

Generador de contenido visual para redes sociales usando IA. CLI en español.

## Motores de generación

| Motor | Uso | Costo |
|-------|-----|-------|
| NVIDIA NIM FLUX.1-schnell | Imágenes (primario) | Gratis (1000 credits) |
| NVIDIA NIM FLUX.1-dev | Imágenes (mayor calidad) | Gratis (1000 credits) |
| Pollinations.ai | Imágenes (fallback) | Gratis (sin key) |
| MoneyPrinterTurbo | Videos cortos | Gratis (Edge TTS) |

## Instalación

```bash
cd scripts/ad_studio
pip install -r requirements.txt
cp .env.example .env
# Editar .env con tu NVIDIA_API_KEY
```

## Uso

```bash
# Generar imagen individual
python main.py imagen --tipo instagram_post --prompt "oferta 20% off en pizzas"

# Generar imagen con brand manual
python main.py imagen --tipo instagram_post --prompt "oferta 20% off" --marca brand_manuals/ejemplo_pizzeria.json

# Generar carrusel
python main.py carrusel --titulo "5 secretos de la pizza" --puntos "Masa fresca" "Horno leña" "Queso mozzarella" "Salsa pomodoro" "Tiempo coccion"

# Generar miniatura YouTube
python main.py thumbnail --titulo "Como hacer pizza en casa"

# Generar batch desde JSON
python main.py lote --archivo posts.json --marca brand_manuals/marca.json

# Generar video (requiere MoneyPrinterTurbo)
python main.py video --prompt "promo fin de semana pizzeria" --duracion 15

# Listar formatos
python main.py formatos

# Verificar motores
python main.py verificar

# Gestionar brand manuals
python main.py marca --crear "Mi Marca"
python main.py marca --listar
```

## Formatos soportados

| Formato | Resolución | Plataformas |
|---------|-----------|-------------|
| instagram_post | 1080x1080 | Instagram |
| instagram_story | 1080x1920 | Instagram |
| instagram_carousel | 1080x1350 | Instagram, LinkedIn |
| youtube_thumbnail | 1280x720 | YouTube |
| youtube_banner | 2560x1440 | YouTube |
| facebook_post | 1200x630 | Facebook |
| facebook_ad | 1200x628 | Facebook, Instagram |
| linkedin_post | 1200x627 | LinkedIn |
| linkedin_carousel | 1080x1350 | LinkedIn |
| google_ads | 1200x628 | Google |
| twitter_post | 1600x900 | Twitter/X |
| tiktok_cover | 1080x1920 | TikTok |
| pinterest_pin | 1000x1500 | Pinterest |
| flyer_a4 | 2480x3508 | Impresión |

## Brand Manual (JSON)

```json
{
  "nombre": "Mi Marca",
  "colores": {
    "primario": "#FF0000",
    "secundario": "#00FF00",
    "acento": "#0000FF",
    "fondo": "#FFFFFF",
    "texto": "#000000"
  },
  "tipografia": {
    "titulares": "Arial Bold",
    "cuerpo": "Arial"
  },
  "tono": "profesional, moderno",
  "estilo": "minimalista, colores sólidos, mucho espacio en blanco",
  "prohibido": ["textos largos", "fondos abarrotados"]
}
```

## Estructura del proyecto

```
ad_studio/
├── main.py                    # CLI principal
├── config.py                  # Configuración
├── brand/
│   ├── __init__.py            # Utilidades de formato
│   ├── loader.py              # Carga brand manual JSON
│   └── prompt_builder.py      # Genera prompts optimizados
├── generators/
│   ├── __init__.py            # Exporta generadores
│   ├── image_generator.py     # NVIDIA NIM + Pollinations
│   ├── carousel_generator.py  # Carrusel slide-by-slide
│   ├── thumbnail_generator.py # Miniaturas YouTube
│   └── video_generator.py     # Wrapper MoneyPrinterTurbo
├── formats/                   # Templates de formato (14 JSON)
├── brand_manuals/             # Manuales de marca
├── output/                    # Archivos generados
├── requirements.txt
├── .env.example
└── README.md
```
