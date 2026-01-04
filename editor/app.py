"""
Dotti Pixel Editor - FastAPI Backend
"""
import asyncio
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Optional

# Preset emoji patterns (8x8)
_ = [0, 0, 0]
R = [255, 0, 0]
G = [0, 255, 0]
B = [0, 0, 255]
Y = [255, 255, 0]
W = [255, 255, 255]
O = [255, 128, 0]
P = [255, 0, 255]
C = [0, 255, 255]

PRESETS = {
    "heart": {
        "name": "Herz",
        "pixels": [
            [_, R, R, _, _, R, R, _],
            [R, R, R, R, R, R, R, R],
            [R, R, R, R, R, R, R, R],
            [R, R, R, R, R, R, R, R],
            [_, R, R, R, R, R, R, _],
            [_, _, R, R, R, R, _, _],
            [_, _, _, R, R, _, _, _],
            [_, _, _, _, _, _, _, _],
        ]
    },
    "smiley": {
        "name": "Smiley",
        "pixels": [
            [_, _, Y, Y, Y, Y, _, _],
            [_, Y, Y, Y, Y, Y, Y, _],
            [Y, Y, _, Y, Y, _, Y, Y],
            [Y, Y, Y, Y, Y, Y, Y, Y],
            [Y, Y, Y, Y, Y, Y, Y, Y],
            [Y, _, Y, Y, Y, Y, _, Y],
            [_, Y, _, _, _, _, Y, _],
            [_, _, Y, Y, Y, Y, _, _],
        ]
    },
    "star": {
        "name": "Stern",
        "pixels": [
            [_, _, _, Y, Y, _, _, _],
            [_, _, _, Y, Y, _, _, _],
            [Y, Y, Y, Y, Y, Y, Y, Y],
            [_, Y, Y, Y, Y, Y, Y, _],
            [_, _, Y, Y, Y, Y, _, _],
            [_, Y, Y, _, _, Y, Y, _],
            [Y, Y, _, _, _, _, Y, Y],
            [Y, _, _, _, _, _, _, Y],
        ]
    },
    "sun": {
        "name": "Sonne",
        "pixels": [
            [_, _, O, _, _, O, _, _],
            [_, _, _, O, O, _, _, _],
            [O, _, Y, Y, Y, Y, _, O],
            [_, O, Y, Y, Y, Y, O, _],
            [_, O, Y, Y, Y, Y, O, _],
            [O, _, Y, Y, Y, Y, _, O],
            [_, _, _, O, O, _, _, _],
            [_, _, O, _, _, O, _, _],
        ]
    },
    "ghost": {
        "name": "Geist",
        "pixels": [
            [_, _, W, W, W, W, _, _],
            [_, W, W, W, W, W, W, _],
            [W, W, _, W, W, _, W, W],
            [W, W, W, W, W, W, W, W],
            [W, W, W, W, W, W, W, W],
            [W, W, W, W, W, W, W, W],
            [W, W, W, W, W, W, W, W],
            [W, _, W, _, _, W, _, W],
        ]
    },
    "alien": {
        "name": "Alien",
        "pixels": [
            [_, G, _, _, _, _, G, _],
            [_, _, G, _, _, G, _, _],
            [_, G, G, G, G, G, G, _],
            [G, G, _, G, G, _, G, G],
            [G, G, G, G, G, G, G, G],
            [_, G, G, G, G, G, G, _],
            [_, G, _, _, _, _, G, _],
            [_, _, G, _, _, G, _, _],
        ]
    },
    "fire": {
        "name": "Feuer",
        "pixels": [
            [_, _, _, R, _, _, _, _],
            [_, _, R, R, R, _, _, _],
            [_, _, R, Y, R, _, _, _],
            [_, R, Y, Y, Y, R, _, _],
            [_, R, Y, Y, Y, R, _, _],
            [R, O, Y, Y, Y, O, R, _],
            [R, O, O, Y, O, O, R, _],
            [_, R, O, O, O, R, _, _],
        ]
    },
    "rainbow": {
        "name": "Regenbogen",
        "pixels": [
            [_, R, R, R, R, R, R, _],
            [R, O, O, O, O, O, O, R],
            [R, O, Y, Y, Y, Y, O, R],
            [_, O, Y, G, G, Y, O, _],
            [_, _, Y, G, G, Y, _, _],
            [_, _, _, G, G, _, _, _],
            [_, _, _, _, _, _, _, _],
            [_, _, _, _, _, _, _, _],
        ]
    },
}

from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

# Add parent directory to path for dotti import
sys.path.insert(0, str(Path(__file__).parent.parent))
from dotti import Dotti

from editor.database import init_db, get_db, Image

# Global state
dotti: Optional[Dotti] = None
current_pixels: list = [[[0, 0, 0] for _ in range(8)] for _ in range(8)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    global dotti
    init_db()

    # Try to connect to Dotti
    dotti = Dotti()
    try:
        connected = await dotti.connect(timeout=10)
        if connected:
            print("Dotti connected!")
            await dotti.turn_off()
        else:
            print("Dotti not found - running in preview mode")
            dotti = None
    except Exception as e:
        print(f"Dotti connection failed: {e} - running in preview mode")
        dotti = None

    yield

    # Cleanup
    if dotti and dotti.is_connected:
        await dotti.turn_off()
        await dotti.disconnect()


app = FastAPI(title="Dotti Pixel Editor", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB to hex color."""
    return f"#{r:02x}{g:02x}{b:02x}"


@app.get("/", response_class=HTMLResponse)
async def editor(request: Request, db: Session = Depends(get_db)):
    """Render the editor page."""
    images = db.query(Image).order_by(Image.created_at.desc()).all()
    return templates.TemplateResponse("editor.html", {
        "request": request,
        "pixels": current_pixels,
        "images": images,
        "presets": PRESETS,
        "dotti_connected": dotti is not None and dotti.is_connected,
    })


async def ensure_dotti_connected():
    """Ensure Dotti is connected, reconnect if needed."""
    global dotti
    if dotti is None:
        dotti = Dotti()

    if not dotti.is_connected:
        print("Dotti reconnecting...")
        try:
            await dotti.connect(timeout=10)
            print("Dotti reconnected!")
        except Exception as e:
            print(f"Dotti reconnect failed: {e}")
            return False
    return True


@app.post("/pixel/{x}/{y}", response_class=HTMLResponse)
async def set_pixel(x: int, y: int, color: str = Form(...), request: Request = None):
    """Set a single pixel and return updated grid."""
    if not (0 <= x < 8 and 0 <= y < 8):
        raise HTTPException(status_code=400, detail="Invalid coordinates")

    r, g, b = hex_to_rgb(color)
    current_pixels[y][x] = [r, g, b]

    # Send to Dotti if connected
    if await ensure_dotti_connected():
        try:
            await dotti.set_pixel(x, y, r, g, b)
        except Exception as e:
            print(f"Dotti error: {e}")

    # Return just the updated pixel div
    hex_color = rgb_to_hex(r, g, b)
    return f'''<div class="pixel"
        style="background-color: {hex_color};"
        data-x="{x}" data-y="{y}"
        hx-post="/pixel/{x}/{y}"
        hx-vals="js:{{color: document.getElementById('colorPicker').value}}"
        hx-swap="outerHTML"></div>'''


@app.post("/clear", response_class=HTMLResponse)
async def clear_grid(request: Request):
    """Clear all pixels."""
    global current_pixels
    current_pixels = [[[0, 0, 0] for _ in range(8)] for _ in range(8)]

    if await ensure_dotti_connected():
        try:
            await dotti.turn_off()
        except Exception as e:
            print(f"Dotti error: {e}")

    return templates.TemplateResponse("partials/grid.html", {
        "request": request,
        "pixels": current_pixels,
    })


@app.post("/random", response_class=HTMLResponse)
async def random_grid(request: Request):
    """Fill grid with random colors."""
    import random
    global current_pixels

    # Predefined vibrant colors for better results
    colors = [
        [255, 0, 0], [0, 255, 0], [0, 0, 255],
        [255, 255, 0], [255, 0, 255], [0, 255, 255],
        [255, 128, 0], [255, 255, 255], [0, 0, 0],
    ]

    for y in range(8):
        for x in range(8):
            color = random.choice(colors)
            current_pixels[y][x] = color

    # Send to Dotti
    if await ensure_dotti_connected():
        try:
            for y in range(8):
                for x in range(8):
                    r, g, b = current_pixels[y][x]
                    await dotti.set_pixel(x, y, r, g, b)
        except Exception as e:
            print(f"Dotti error: {e}")

    return templates.TemplateResponse("partials/grid.html", {
        "request": request,
        "pixels": current_pixels,
    })


@app.post("/slot/save/{slot_id}", response_class=HTMLResponse)
async def save_to_slot(slot_id: int, request: Request):
    """Save current display to Dotti hardware slot (0-7)."""
    if not (0 <= slot_id <= 7):
        raise HTTPException(status_code=400, detail="Slot must be 0-7")

    if await ensure_dotti_connected():
        try:
            await dotti.save_to_slot(slot_id)
            return f'<span class="slot-status">Slot {slot_id} gespeichert!</span>'
        except Exception as e:
            return f'<span class="slot-status error">Fehler: {e}</span>'
    return '<span class="slot-status error">Dotti nicht verbunden</span>'


@app.post("/slot/load/{slot_id}", response_class=HTMLResponse)
async def load_from_slot(slot_id: int, request: Request):
    """Load from Dotti hardware slot (0-7) - instant switch!"""
    if not (0 <= slot_id <= 7):
        raise HTTPException(status_code=400, detail="Slot must be 0-7")

    if await ensure_dotti_connected():
        try:
            await dotti.load_from_slot(slot_id)
            return f'<span class="slot-status">Slot {slot_id} geladen!</span>'
        except Exception as e:
            return f'<span class="slot-status error">Fehler: {e}</span>'
    return '<span class="slot-status error">Dotti nicht verbunden</span>'


@app.post("/preset/{preset_id}", response_class=HTMLResponse)
async def load_preset(preset_id: str, request: Request):
    """Load a preset pattern."""
    global current_pixels

    if preset_id not in PRESETS:
        raise HTTPException(status_code=404, detail="Preset not found")

    current_pixels = [row[:] for row in PRESETS[preset_id]["pixels"]]

    # Send to Dotti
    if await ensure_dotti_connected():
        try:
            for y in range(8):
                for x in range(8):
                    r, g, b = current_pixels[y][x]
                    await dotti.set_pixel(x, y, r, g, b)
        except Exception as e:
            print(f"Dotti error: {e}")

    return templates.TemplateResponse("partials/grid.html", {
        "request": request,
        "pixels": current_pixels,
    })


@app.post("/save", response_class=HTMLResponse)
async def save_image(request: Request, name: str = Form(...), db: Session = Depends(get_db)):
    """Save current image to database."""
    if not name.strip():
        name = "Unnamed"

    # Flatten pixels to list
    flat_pixels = []
    for row in current_pixels:
        for pixel in row:
            flat_pixels.append(pixel)

    image = Image(name=name.strip())
    image.set_pixels(flat_pixels)
    db.add(image)
    db.commit()
    db.refresh(image)

    # Return updated image list
    images = db.query(Image).order_by(Image.created_at.desc()).all()
    return templates.TemplateResponse("partials/image_list.html", {
        "request": request,
        "images": images,
    })


@app.post("/load/{image_id}", response_class=HTMLResponse)
async def load_image(image_id: int, request: Request, db: Session = Depends(get_db)):
    """Load image from database and display on Dotti."""
    global current_pixels

    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    current_pixels = image.get_matrix()

    # Send to Dotti
    if await ensure_dotti_connected():
        try:
            for y in range(8):
                for x in range(8):
                    r, g, b = current_pixels[y][x]
                    await dotti.set_pixel(x, y, r, g, b)
        except Exception as e:
            print(f"Dotti error: {e}")

    return templates.TemplateResponse("partials/grid.html", {
        "request": request,
        "pixels": current_pixels,
    })


@app.delete("/images/{image_id}", response_class=HTMLResponse)
async def delete_image(image_id: int, request: Request, db: Session = Depends(get_db)):
    """Delete image from database."""
    image = db.query(Image).filter(Image.id == image_id).first()
    if image:
        db.delete(image)
        db.commit()

    images = db.query(Image).order_by(Image.created_at.desc()).all()
    return templates.TemplateResponse("partials/image_list.html", {
        "request": request,
        "images": images,
    })
