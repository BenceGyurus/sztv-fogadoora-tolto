from PIL import Image, ImageDraw, ImageFont
import os
import datetime


FONT_LENGTH = 9
FONT_SIZE = 27
START_FIRST_COLUMN_X = 80
START_FIRST_COLUMN_Y = 165
LINE_HEIGHT = 33
START_SECOND_COLUMN_X = 850
START_SECOND_COLUMN_Y = 165
OFFSET = 40
MAX_WIDTH = 680
FONT = "fonts/DINNextLTPro-Condensed1.ttf"
FONT_BOLD = "fonts/DINNextLTPro-BoldCondensed1.ttf"
COLOR = (50, 50, 50)

def getTitle(text):
    words = text.split(" ")
    title = []
    for i, word in enumerate(words):
        if word[0].isupper():
            splited = word.split(",")
            if (len(splited) > 1):
                title.append(splited[0])
                break
            else:
                title.append(word)
        else:
            break
    return " ".join(title) if len(title) > 1 else ""


def parse_txt(filename):
    array = []
    with open(filename, "r", encoding="utf-8") as file:
        lines = file.readlines()
    file.close()
    last_line= ""
    for line in lines:
        if (line.startswith("---")):
            array.append({
                "text": "",
                "type": "s",
                "title": "",
                "separator": True
            })
            continue
        print(f"lastline len: {len(last_line)}")
        line = line.strip()
        if (len(last_line) and line):
            array[-1]["type"] = "s"
        last_line = line
        if line == "":
            continue
        array.append({
            "text": line,
            "type": "p",
            "title": getTitle(line),
            "separator": False
        })
    return array
    

def load_font(font_path, size):
    try:
        return ImageFont.truetype(font_path, size=size)
    except IOError:
        return ImageFont.load_default()

def draw_line(draw, coordinate, text="", color=(200, 200, 200), title="", font_main=load_font(FONT, FONT_SIZE), font_bold=load_font(FONT_BOLD, FONT_SIZE)):
    if (title != ""):
        splited = text.split(title)
    else:
        splited = [text]
    if len(splited) == 1:
        draw.text(
            (coordinate[0], coordinate[1]),
            text,
            fill=color,
            font=font_main
        )
        return
    else:
        current_x = coordinate[0]
        for i, part in enumerate(splited):
            if i > 0:
                draw.text(
                    (current_x, coordinate[1]),
                    title,
                    fill=color,
                    font=font_bold
                )
                bbox = font_bold.getbbox(title)
                current_x +=  bbox[2] - bbox[0]
            draw.text(
                (current_x, coordinate[1]),
                part,
                fill=color,
                font=font_main
            )

def wrap_text(text, font, max_width):
    lines = []
    words = text.split()
    
    if not words:
        return ""

    current_line = words[0]

    for word in words[1:]:
        # Check the pixel width of the line if we add the next word
        if  FONT_LENGTH * len(current_line + " " + word) <= max_width:
            current_line += " " + word
        else:
            # Word doesn't fit, save the current line and start a new one
            lines.append(current_line)
            current_line = word

    # Add the last line
    lines.append(current_line)

    return "\n".join(lines), len(lines)

PNG_INPUT = "varoshaza_fogadoora_1600x900_251017.png"
PNG_OUTPUT = "fogadoora_FROM_PNG.png"

cover_boxes = [
    (50, 150, 800, 900),
    (800, 150, 1570, 860)
]





# Check if input file exists
if not os.path.exists(PNG_INPUT):
    print(f"!!! HIBA: A bemeneti PNG nem található: {PNG_INPUT}")
    print("Győződj meg róla, hogy a szkript és a PNG egy mappában van.")
    exit()

# Try to load a font.
# This will try to find Arial. If it fails, it loads a basic default font.
try:
    font_path = FONT
    if not os.path.exists(FONT):
        font_path = "arial.ttf"
    font_main = ImageFont.truetype(FONT, size=FONT_SIZE)
    print(f"DINNextLTPro-Condensed1 betűtípus betöltve: {FONT}")
except IOError:
    print("Figyelmeztetés: Arial betűtípus nem található. Alapértelmezett betűtípus használata.")
    font_main = ImageFont.load_default()



def create_png(new_texts, output=PNG_OUTPUT, run_count=0):
    second_column_started = False
    i = -1
    with Image.open(PNG_INPUT) as img:
        # Convert to RGBA to ensure we can draw with transparency if needed
        img = img.convert("RGBA")
        _, HEIGHT = img.size
        draw = ImageDraw.Draw(img)
        posX, posY = START_FIRST_COLUMN_X, START_FIRST_COLUMN_Y

        print("Régi szöveg lefedése...")
        # 1. Cover up the old text
        background_color = (240, 240, 240, 255) # GUESSED background color
        for box in cover_boxes:
            draw.rectangle(box, fill=background_color)

        print("Új szöveg hozzáadása...")
        for i, item in enumerate(new_texts):
            if item["separator"]:
                new_texts.remove(item)
                break
            # Use specific font size if provided, else default
            if "font_size" in item:
                try:
                    font = ImageFont.truetype(font_path, size=item["font_size"])
                except IOError:
                    font = ImageFont.load_default(size=item["font_size"])
            else:
                font = font_main
            
            font = load_font(FONT, FONT_SIZE)
            bold_font = load_font(FONT_BOLD, FONT_SIZE)
            
        
            text_to_draw = item["text"]
            text_to_draw, height = wrap_text(item["text"], font, MAX_WIDTH)

            if (posY + (height*LINE_HEIGHT)) > HEIGHT - OFFSET:
                if second_column_started:
                    break
                posX = START_SECOND_COLUMN_X
                posY = START_SECOND_COLUMN_Y
                second_column_started = True

            for line in text_to_draw.split("\n"):
                draw_line(draw, (posX, posY), text=line, color=COLOR, title=item["title"] if "title" in item.keys() else "", font_main=font, font_bold=bold_font)
                posY += LINE_HEIGHT

            if (posY + (OFFSET if item["type"] == "p" else 0)) > HEIGHT - OFFSET:
                if second_column_started:
                    break
                posX = START_SECOND_COLUMN_X
                posY = START_SECOND_COLUMN_Y
                second_column_started = True
            else:
                posY += (OFFSET if item["type"] == "p" else 0)

        # Save the final image
        img.save(f"{output}.png")
        print(f"Kész! Az új kép elmentve ide: {output}")
    return new_texts[i:] if i != len(new_texts)-1 else []


def main():
    new_texts = parse_txt("texts/fogadoora.txt")
    print(f"Szövegek betöltve: {len(new_texts)} elem.")
    run_count = 0
    while len(new_texts):
        new_texts = create_png(new_texts, output=f"ready/varoshaza_fogadoora_1600x900_{datetime.datetime.now().strftime("%y%m%d")}_{run_count}", run_count=run_count)
        run_count += 1

if __name__ == "__main__":
    main()