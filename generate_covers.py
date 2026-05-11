#!/usr/bin/env python3
"""Generate 1280x720 YouTube thumbnail covers for all 27 quantum computing modules."""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import random

WIDTH, HEIGHT = 1280, 720
OUT_DIR = "covers"
LOGO_PATH = "logo.png"

FONT_BOLD = "/System/Library/Fonts/HelveticaNeue.ttc"
FONT_THAI = "/System/Library/Fonts/Supplemental/Ayuthaya.ttf"

BG_TOP = (8, 12, 28)
BG_BOT = (18, 26, 55)

TRACK_COLORS = {
    "F":  (245, 166,  35),
    "S":  ( 39, 174,  96),
    "D":  ( 41, 128, 185),
    "DS": (230, 126,  34),
    "E":  (192,  57,  43),
}

MODULES = {
    "F1":  {
        "title": "What is Quantum\nComputing?",
        "track": "F", "track_name": "FOUNDATION",
        "thai": "ควอนตัมเปลี่ยนโลกได้จริง\nทำไมทุกคนต้องรู้จักมัน",
    },
    "F2":  {
        "title": "Why Qiskit?",
        "track": "F", "track_name": "FOUNDATION",
        "thai": "เริ่มเขียนโค้ดควอนตัม\nด้วย Python ใน 10 นาที",
    },
    "F3":  {
        "title": "Qubits, States\n& Measurement",
        "track": "F", "track_name": "FOUNDATION",
        "thai": "Qubit อยู่ได้ทั้ง 0 และ 1\nพร้อมกัน จริงหรือไม่?",
    },
    "F4":  {
        "title": "How to Use\nThis Series",
        "track": "F", "track_name": "FOUNDATION",
        "thai": "ตั้งค่า Environment ให้พร้อม\nก่อนเริ่มเรียนควอนตัม",
    },
    "S1":  {
        "title": "Bits, Qubits\n& Superposition",
        "track": "S", "track_name": "STUDENT",
        "thai": "เหรียญกำลังหมุน != หัว หรือก้อย\nนั่นคือ Superposition",
    },
    "S2":  {
        "title": "Quantum Gates",
        "track": "S", "track_name": "STUDENT",
        "thai": "Gate ควอนตัมคืออะไร?\nหมุน Qubit บน Bloch Sphere",
    },
    "S3":  {
        "title": "Entanglement:\nQubits That Share\na Secret",
        "track": "S", "track_name": "STUDENT",
        "thai": "2 อนุภาคคุยกันได้ข้ามกาแล็กซี\nเรื่องจริงหรือเรื่องโกหก?",
    },
    "S4":  {
        "title": "Your First\nQuantum Circuit",
        "track": "S", "track_name": "STUDENT",
        "thai": "สร้าง Quantum Circuit แรก\nทำตามได้ทีละขั้นเลย",
    },
    "S5":  {
        "title": "Quantum Computing\nin the Real World",
        "track": "S", "track_name": "STUDENT",
        "thai": "ควอนตัมแฮกรหัสเข้ารหัสได้จริงไหม?\n3 เรื่องที่ต้องรู้",
    },
    "D1":  {
        "title": "Quantum Computing\nfor Python Devs",
        "track": "D", "track_name": "DEVELOPER",
        "thai": "Python Dev เริ่มเขียน\nQuantum Code ยังไง?",
    },
    "D2":  {
        "title": "Gates as\nMatrix Operations",
        "track": "D", "track_name": "DEVELOPER",
        "thai": "ทุก Gate คือ Matrix 2x2\nพิสูจน์ด้วยโค้ดได้เลย",
    },
    "D3":  {
        "title": "Building\nComplex Circuits",
        "track": "D", "track_name": "DEVELOPER",
        "thai": "ประกอบ Circuit เหมือนเขียน\nModule Python ทีละชิ้น",
    },
    "D4":  {
        "title": "Deutsch-Jozsa\nAlgorithm",
        "track": "D", "track_name": "DEVELOPER",
        "thai": "1 Query ตอบได้ในที่ที่\nClassical ต้องใช้ล้านครั้ง",
    },
    "D5":  {
        "title": "Grover's Search\nAlgorithm",
        "track": "D", "track_name": "DEVELOPER",
        "thai": "ค้นหาเร็วขึ้น sqrt(N) เท่า\nด้วย Quantum Interference",
    },
    "D6":  {
        "title": "Running on Real\nIBM Quantum",
        "track": "D", "track_name": "DEVELOPER",
        "thai": "รัน Code บน Quantum Hardware\nจริงๆ วันนี้เลย",
    },
    "DS1": {
        "title": "QML: The\nBig Picture",
        "track": "DS", "track_name": "DATA SCIENTIST",
        "thai": "VQC vs Neural Network\nใครคืออนาคต ML?",
    },
    "DS2": {
        "title": "Encoding Classical\nData",
        "track": "DS", "track_name": "DATA SCIENTIST",
        "thai": "แปลง Dataset เข้า Quantum Circuit\nทำยังไง?",
    },
    "DS3": {
        "title": "Variational\nQuantum Circuits",
        "track": "DS", "track_name": "DATA SCIENTIST",
        "thai": "Ansatz = Architecture\nมุมหมุน = Weight ฝึกได้เลย",
    },
    "DS4": {
        "title": "Quantum Neural\nNetworks",
        "track": "DS", "track_name": "DATA SCIENTIST",
        "thai": "QNN ต่อกับ PyTorch ได้\nด้วย TorchConnector",
    },
    "DS5": {
        "title": "Quantum Kernels\nfor Classification",
        "track": "DS", "track_name": "DATA SCIENTIST",
        "thai": "Quantum Kernel ชนะ RBF ได้จริงไหม?\nทดสอบเลย",
    },
    "DS6": {
        "title": "Benchmarking &\nReality Check",
        "track": "DS", "track_name": "DATA SCIENTIST",
        "thai": "Quantum ML เจ๋งจริง\nหรือแค่ Hype ว่างเปล่า?",
    },
    "E1":  {
        "title": "Hardware\nArchitectures",
        "track": "E", "track_name": "ENGINEER",
        "thai": "Superconducting vs Trapped Ion\nเลือก Quantum Hardware ยังไง?",
    },
    "E2":  {
        "title": "Noise, Decoherence\n& Error",
        "track": "E", "track_name": "ENGINEER",
        "thai": "Noise ทำลาย Qubit ยังไง?\nT1, T2 คืออะไรกันแน่",
    },
    "E3":  {
        "title": "Transpilation &\nOptimization",
        "track": "E", "track_name": "ENGINEER",
        "thai": "Transpiler ควอนตัม = Compiler\nที่ Engineer ต้องเข้าใจ",
    },
    "E4":  {
        "title": "Pulse-Level\nProgramming",
        "track": "E", "track_name": "ENGINEER",
        "thai": "เขียน Pulse แทน Gate\nเข้าถึง Hardware ระดับ Assembly",
    },
    "E5":  {
        "title": "Error Mitigation\nTechniques",
        "track": "E", "track_name": "ENGINEER",
        "thai": "ลด Error โดยไม่ต้องใช้\nLogical Qubit ด้วย ZNE",
    },
    "E6":  {
        "title": "Quantum Error\nCorrection",
        "track": "E", "track_name": "ENGINEER",
        "thai": "ทำไมต้อง Qubit เยอะมาก\nเพื่อแค่ 1 Logical Qubit?",
    },
}


def get_track_color(module_id):
    if module_id.startswith("DS"):
        return TRACK_COLORS["DS"]
    return TRACK_COLORS[module_id[0]]


def make_white_transparent(img):
    img = img.convert("RGBA")
    data = list(img.getdata())
    new_data = []
    for r, g, b, a in data:
        if r > 210 and g > 210 and b > 210:
            new_data.append((r, g, b, 0))
        else:
            new_data.append((r, g, b, a))
    img.putdata(new_data)
    return img


def draw_gradient_bg(img):
    draw = ImageDraw.Draw(img)
    for y in range(HEIGHT):
        t = y / (HEIGHT - 1)
        r = int(BG_TOP[0] + (BG_BOT[0] - BG_TOP[0]) * t)
        g = int(BG_TOP[1] + (BG_BOT[1] - BG_TOP[1]) * t)
        b = int(BG_TOP[2] + (BG_BOT[2] - BG_TOP[2]) * t)
        draw.line([(0, y), (WIDTH - 1, y)], fill=(r, g, b))


def draw_glow(img, track_color):
    cr, cg, cb = track_color
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse([(40, 160), (760, 590)], fill=(cr, cg, cb, 22))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=90))
    base = img.convert("RGBA")
    result = Image.alpha_composite(base, glow)
    img.paste(result.convert("RGB"), (0, 0))


def draw_circuit_decoration(img, track_color, seed):
    cr, cg, cb = track_color
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    rng = random.Random(seed)

    wire_ys = [185, 360, 535]
    x_start = 690
    x_end = 1255

    for wy in wire_ys:
        draw.line([(x_start, wy), (x_end, wy)], fill=(cr, cg, cb, 55), width=2)

        # Nodes along the wire
        step = (x_end - x_start) // 8
        for i in range(9):
            nx = x_start + i * step
            nr = rng.randint(4, 8)
            draw.ellipse(
                [(nx - nr, wy - nr), (nx + nr, wy + nr)],
                fill=(cr, cg, cb, 70),
                outline=(cr, cg, cb, 110),
                width=1,
            )

        # One right-angle jog per wire
        jog_x = rng.randint(x_start + 80, x_start + 280)
        jog_h = rng.choice([-35, -45, 35, 45])
        draw.line([(jog_x, wy), (jog_x, wy + jog_h)], fill=(cr, cg, cb, 55), width=2)
        jog_end_x = jog_x + rng.randint(50, 90)
        draw.line([(jog_x, wy + jog_h), (jog_end_x, wy + jog_h)], fill=(cr, cg, cb, 55), width=2)
        draw.ellipse(
            [(jog_end_x - 5, wy + jog_h - 5), (jog_end_x + 5, wy + jog_h + 5)],
            fill=(cr, cg, cb, 90),
        )

    # Particle dots — right side (dense)
    for _ in range(28):
        px = rng.randint(700, 1255)
        py = rng.randint(60, 660)
        pr = rng.randint(2, 5)
        pa = rng.randint(25, 65)
        draw.ellipse([(px - pr, py - pr), (px + pr, py + pr)], fill=(cr, cg, cb, pa))

    # Particle dots — left side (sparse accent)
    for _ in range(8):
        px = rng.randint(40, 680)
        py = rng.randint(60, 660)
        pr = rng.randint(1, 3)
        pa = rng.randint(15, 35)
        draw.ellipse([(px - pr, py - pr), (px + pr, py + pr)], fill=(cr, cg, cb, pa))

    base = img.convert("RGBA")
    result = Image.alpha_composite(base, layer)
    img.paste(result.convert("RGB"), (0, 0))


def draw_pill(draw, x, y, text, track_color, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    pad_x, pad_y = 20, 10
    x2 = x + tw + pad_x * 2
    y2 = y + th + pad_y * 2
    cr, cg, cb = track_color
    draw.rounded_rectangle([(x, y), (x2, y2)], radius=8, fill=(cr, cg, cb))
    draw.text((x + pad_x, y + pad_y), text, font=font, fill=(255, 255, 255))


def generate_cover(module_id, data, logo_img, fonts):
    tc = get_track_color(module_id)

    img = Image.new("RGB", (WIDTH, HEIGHT), BG_TOP)
    draw_gradient_bg(img)
    draw_glow(img, tc)
    draw_circuit_decoration(img, tc, seed=abs(hash(module_id)) & 0xFFFF)

    draw = ImageDraw.Draw(img)

    # Bottom accent bar
    draw.rectangle([(0, HEIGHT - 8), (WIDTH, HEIGHT)], fill=tc)

    # Logo (top-left)
    logo_size = 88
    logo_resized = logo_img.resize((logo_size, logo_size), Image.LANCZOS)
    img.paste(logo_resized, (40, 22), logo_resized)

    # Module badge (top-right, large, track color)
    font_badge = fonts["badge"]
    badge_text = module_id
    bbox = draw.textbbox((0, 0), badge_text, font=font_badge)
    bw = bbox[2] - bbox[0]
    draw.text((WIDTH - bw - 48, 18), badge_text, font=font_badge, fill=tc)

    # Track pill
    draw_pill(draw, 40, 140, data["track_name"], tc, fonts["pill"])

    # English title
    font_title = fonts["title"]
    title_lines = data["title"].split("\n")
    ty = 225
    line_h_title = 94
    for line in title_lines:
        draw.text((40, ty), line, font=font_title, fill=(255, 255, 255))
        ty += line_h_title

    # Thai hook — min y=455 so it doesn't crowd the title on short modules
    font_thai = fonts["thai"]
    thai_y = max(ty + 18, 455)
    thai_lines = data["thai"].split("\n")
    line_h_thai = 56
    for line in thai_lines:
        draw.text((40, thai_y), line, font=font_thai, fill=tc)
        thai_y += line_h_thai

    out_path = os.path.join(OUT_DIR, f"{module_id}_cover.png")
    img.save(out_path, "PNG")
    print(f"  Generated {module_id}")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    logo = Image.open(LOGO_PATH).convert("RGBA")
    logo = make_white_transparent(logo)

    fonts = {
        "badge": ImageFont.truetype(FONT_BOLD, 92, index=1),
        "pill":  ImageFont.truetype(FONT_BOLD, 22, index=1),
        "title": ImageFont.truetype(FONT_BOLD, 80, index=1),
        "thai":  ImageFont.truetype(FONT_THAI, 42),
    }

    print(f"Generating {len(MODULES)} covers -> {OUT_DIR}/")
    for module_id, data in MODULES.items():
        generate_cover(module_id, data, logo, fonts)

    print(f"\nDone. {len(MODULES)} covers saved to {OUT_DIR}/")


if __name__ == "__main__":
    main()
