from PIL import Image
from collections import OrderedDict

IMAGE_PATH = "input.png"
MAX_COLORS = 16

img = Image.open(IMAGE_PATH).convert("RGBA")
width, height = img.size

assert (width, height) == (256, 240)

pixels = list(img.getdata())

# Step 1: Build palette
palette = OrderedDict()

for p in pixels:
    if p not in palette:
        if len(palette) >= MAX_COLORS:
            raise ValueError("More than 16 colors found!")
        palette[p] = len(palette)

# Step 2: Convert image to indices
indexed_pixels = [palette[p] for p in pixels]

# Step 3: Write assembly
with open("image_palette.s", "w") as f:
    f.write(".data\n\n")
    
    # Palette
    f.write("palette:\n")
    for (r, g, b, a) in palette:
        argb = (a << 24) | (r << 16) | (g << 8) | b
        f.write(f"    .word 0x{argb:08X}\n")

    f.write("\nimage:\n")

    # Write pixels (16 per line)
    for i in range(0, len(indexed_pixels), 16):
        row = indexed_pixels[i:i+16]
        f.write("    .byte " + ", ".join(map(str, row)) + "\n")

    f.write("\n.text\n")
    f.write("# Render using palette lookup\n")

print("Done! Generated image_palette.s")
