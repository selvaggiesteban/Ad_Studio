def build_prompt(description, brand, format_data=None, language="en"):
    colors = brand.get("colores", {})
    style = brand.get("estilo", "")
    tone = brand.get("tono", "")
    typography = brand.get("tipografia", {})
    forbidden = brand.get("prohibido", [])

    parts = []

    parts.append(f"Create an image for {brand['nombre']}.")

    if description:
        parts.append(f"Content: {description}")

    if style:
        parts.append(f"Visual style: {style}")

    if tone:
        parts.append(f"Tone: {tone}")

    if colors:
        colors_str = ", ".join(
            f"{k}: {v}" for k, v in colors.items() if k in ["primario", "secundario", "acento"]
        )
        if colors_str:
            parts.append(f"Color palette: {colors_str}")

        if "fondo" in colors:
            parts.append(f"Background: {colors['fondo']}")

        if "texto" in colors:
            parts.append(f"Text color: {colors['texto']}")

    if typography:
        headers = typography.get("titulares", "")
        if headers:
            parts.append(f"Header typography: {headers}, bold, large, legible")

    if format_data:
        parts.append(f"Format: {format_data.get('ancho')}x{format_data.get('alto')} px")
        if "orientacion" in format_data:
            parts.append(f"Orientation: {format_data['orientacion']}")
        if "guia_composicion" in format_data:
            parts.append(f"Composition: {format_data['guia_composicion']}")

    if forbidden:
        parts.append("DO NOT include: " + ", ".join(forbidden))

    parts.append("No watermarks, no platform logos, professional high-quality image.")

    return " ".join(parts)


def build_carousel_prompts(title, points, brand, slides=5):
    prompts = []

    colors = brand.get("colores", {})
    style = brand.get("estilo", "")
    tone = brand.get("tono", "")

    cover_prompt = (
        f"Create the cover slide of a carousel for {brand['nombre']}. "
        f"Large and eye-catching title: '{title}'. "
        f"Style: {style}. Tone: {tone}. "
        f"Colors: primary {colors.get('primario', '#000')}, "
        f"secondary {colors.get('secundario', '#FFF')}. "
        f"Format 1080x1350 px. Modern, professional, no watermarks."
    )
    prompts.append({"slide": 1, "tipo": "portada", "prompt": cover_prompt})

    for i, point in enumerate(points[:slides - 2], start=2):
        slide_prompt = (
            f"Create slide {i} of a carousel for {brand['nombre']}. "
            f"Title: '{point}'. "
            f"One idea per slide, maximum 15 words of text. "
            f"Style: {style}. Colors: primary {colors.get('primario', '#000')}, "
            f"secondary {colors.get('secundario', '#FFF')}. "
            f"Format 1080x1350 px. Modern visual, no watermarks."
        )
        prompts.append({"slide": i, "tipo": "contenido", "prompt": slide_prompt})

    cta_prompt = (
        f"Create the final slide (CTA) of a carousel for {brand['nombre']}. "
        f"Invite to follow, share or visit. "
        f"Style: {style}. Colors: primary {colors.get('primario', '#000')}. "
        f"Format 1080x1350 px. Eye-catching, no watermarks."
    )
    prompts.append({"slide": slides, "tipo": "cta", "prompt": cta_prompt})

    return prompts


def build_thumbnail_prompt(title, brand, tone="professional"):
    colors = brand.get("colores", {})
    style = brand.get("estilo", "")

    return (
        f"Create a YouTube thumbnail for {brand['nombre']}. "
        f"Large text title (3-5 words): '{title}'. "
        f"Style: {style}. Tone: {tone}. "
        f"Colors: primary {colors.get('primario', '#000')}, "
        f"accent {colors.get('acento', '#FF0000')}. "
        f"Format 1280x720 px. Face occupies 30-50% of the frame if a person is present. "
        f"Text legible on mobile. No watermarks, no YouTube logos."
    )
