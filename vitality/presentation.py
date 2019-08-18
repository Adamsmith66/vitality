from types import SimpleNamespace

from . import Error

DEFAULTS = SimpleNamespace(

    # Dimensions
    height=1080,
    width=1920,

    # Spacing
    bullets_padding_left=100,
    heading_padding_left=50,
    heading_padding_top=80,

    # Layout
    background_color="black",
    color="white",
    font="sans-serif",

    # Font Sizes
    heading_font_size=80,
    section_font_size=100,
    subtitle_font_size=60,
    text_font_size=55,
    title_font_size=120,

    # Bullets
    bullet=chr(8226)+" ",
    bullet_spacing=30
)

def presentation_data(config):
    """Converts YML presentation representation into instructions object."""
    defaults = config.get("defaults", {})
    data = {
        "title": config.get("title"),
        "defaults": {

            # Spacing
            "bullets_padding_left": defaults.get("bullets_padding_left", DEFAULTS.bullets_padding_left),
            "heading_padding_left": defaults.get("heading_padding_left", DEFAULTS.heading_padding_left),
            "heading_padding_top": defaults.get("heading_padding_top", DEFAULTS.heading_padding_top),

            # Layout
            "background_color": defaults.get("background_color", DEFAULTS.background_color),
            "color": defaults.get("color", DEFAULTS.color),
            "font": defaults.get("font", DEFAULTS.font),

            # Font Sizes
            "heading_font_size": defaults.get("heading_font_size", DEFAULTS.heading_font_size),
            "section_font_size": defaults.get("section_font_size", DEFAULTS.section_font_size),
            "subtitle_font_size": defaults.get("subtitle_font_size", DEFAULTS.subtitle_font_size),
            "text_font_size": defaults.get("text_font_size", DEFAULTS.text_font_size),
            "title_font_size": defaults.get("title_font_size", DEFAULTS.title_font_size),

            # Bullets
            "bullet": defaults.get("bullet", DEFAULTS.bullet),
            "bullet_spacing": defaults.get("bullet_spacing", DEFAULTS.bullet_spacing)
        },
        "fonts": config.get("fonts", []),
        "size": {
            "width": config.get("size", {}).get("width", DEFAULTS.width),
            "height": config.get("size", {}).get("height", DEFAULTS.height)
        },
        "slides": []
    }
    for slide in config.get("slides", []):

        if slide is None:
            slide = {}
            result = blank_slide(slide, data)

        # Just string is a section slide
        elif isinstance(slide, str):
            slide = {"text": slide}
            result = section_slide(slide, data)

        elif slide["type"] == "section":
            result = section_slide(slide, data)

        elif slide["type"] == "title":
            result = title_slide(slide, data)

        elif slide["type"] == "blank":
            result = blank_slide(slide, data)

        elif slide["type"] == "bullets":
            result = bullets_slide(slide, data)

        else:
            result = blank_slide(slide, data)

        # TODO: deal with custom objects here
        if slide.get("objects") is not None:
            pass

        data["slides"].append(result)
    return data


def base_slide(slide, data):
    """Basic elements on every slide."""
    return {
        "backgroundColor": slide.get("background_color", data["defaults"]["background_color"]),
    }


def blank_slide(slide, data):
    """Empty slide with no content."""
    result = base_slide(slide, data)
    result.update({
        "layout": "blank"
    })
    return result


def bullets_slide(slide, data):
    """Slide with title and bullets."""
    result = base_slide(slide, data)

    # Handle empty title, or title as single string
    if "title" not in slide:
        slide["title"] = {}
    elif isinstance(slide["title"], str):
        slide["title"] = {"text": slide["title"]}

    if "bullets" not in slide:
        slide["bullets"] = []
    if isinstance(slide["bullets"], str):
        slide["bullets"] = {
            "text": [slide["bullets"]]
        }
    elif isinstance(slide["bullets"], list):
        slide["bullets"] = {
            "text": slide["bullets"]
        }
    if not isinstance(slide["bullets"].get("text", []), list):
        slide["bullets"]["text"] = [slide["bullets"]["text"]]

    # Allow specifying color and font for entire slide
    for prop in ["color", "font", "padding_left"]:
        if slide.get(prop):
            slide["title"][prop] = slide["title"].get(prop, slide[prop])
            slide["bullets"][prop] = slide["bullets"].get(prop, slide[prop])

    result.update({
        "layout": "bullets",
        "title": {
            "color": slide["title"].get("color", data["defaults"]["color"]),
            "content": slide["title"].get("text", ""),
            "font": slide["title"].get("font", data["defaults"]["font"]),
            "padding_left": slide["title"].get("padding_left", data["defaults"]["heading_padding_left"]),
            "padding_top": slide["title"].get("padding_top", data["defaults"]["heading_padding_top"]),
            "size": slide["title"].get("size", data["defaults"]["heading_font_size"])
        },
        "bullets": {
            "bullet": slide["bullets"].get("bullet", data["defaults"]["bullet"]),
            "color": slide["bullets"].get("color", data["defaults"]["color"]),
            "content": slide["bullets"].get("text", []),
            "font": slide["bullets"].get("font", data["defaults"]["font"]),
            "padding_left": slide["title"].get("padding_left", data["defaults"]["bullets_padding_left"]),
            "size": slide["bullets"].get("size", data["defaults"]["text_font_size"]),
            "spacing": slide["bullets"].get("spacing", data["defaults"]["bullet_spacing"])
        }
    })
    return result

def section_slide(slide, data):
    """Section divider slide, just a single heading."""
    result = base_slide(slide, data)
    result.update({
        "layout": "section",
        "color": slide.get("color", data["defaults"]["color"]),
        "content": slide.get("text", ""),
        "font": slide.get("font", data["defaults"]["font"]),
        "size": slide.get("size", data["defaults"]["section_font_size"])
    })
    return result


def title_slide(slide, data):
    """Title slide, with title and multi-line subtitle."""
    result = base_slide(slide, data)

    # Allow string literals as title and subtitle
    if isinstance(slide["title"], str):
        slide["title"] = {
            "text": slide["title"]
        }
    if isinstance(slide["subtitle"], str):
        slide["subtitle"] = {
            "text": [slide["subtitle"]]
        }
    elif isinstance(slide["subtitle"], list):
        slide["subtitle"] = {
            "text": slide["subtitle"]
        }
    if not isinstance(slide["subtitle"].get("text", []), list):
        slide["subtitle"]["text"] = [slide["subtitle"]["text"]]

    # Allow specifying color and font for entire slide
    for prop in ["color", "font"]:
        if slide.get(prop):
            slide["title"][prop] = slide["title"].get(prop, slide[prop])
            slide["subtitle"][prop] = slide["subtitle"].get(prop, slide[prop])

    result.update({
        "layout": "title",
        "title": {
            "color": slide["title"].get("color", data["defaults"]["color"]),
            "content": slide["title"].get("text", ""),
            "font": slide["title"].get("font", data["defaults"]["font"]),
            "size": slide["title"].get("size", data["defaults"]["title_font_size"])
        },
        "subtitle": {
            "color": slide["subtitle"].get("color", data["defaults"]["color"]),
            "content": slide["subtitle"].get("text", []),
            "font": slide["subtitle"].get("font", data["defaults"]["font"]),
            "size": slide["subtitle"].get("size", data["defaults"]["subtitle_font_size"])
        }
    })
    return result


