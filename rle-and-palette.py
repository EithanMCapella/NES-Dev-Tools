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

# Step 2: Convert image to palette indices
indexed_pixels = [palette[p] for p in pixels]

# Step 3: RLE encode
def rle_encode(data):
    encoded = []
    i = 0
    while i < len(data):
        value = data[i]
        count = 1
        while i + count < len(data) and data[i + count] == value and count < 255:
            count += 1
        encoded.append((count, value))
        i += count
    return encoded

rle_data = rle_encode(indexed_pixels)

# Step 4: Write assembly
with open("image_palette_rle.s", "w") as f:
    f.write(".data\n\n")

    # Palette
    f.write("palette:\n")
    for (r, g, b, a) in palette:
        argb = (a << 24) | (r << 16) | (g << 8) | b
        f.write(f"    .word 0x{argb:08X}\n")

    # RLE image data
    f.write("\nimage_rle:\n")
    for count, value in rle_data:
        f.write(f"    .byte {count}, {value}\n")

    f.write("\n.text\n")
    f.write("# RLE palette-rendered image\n")

print(f"Done! {len(indexed_pixels)} pixels → {len(rle_data)*2} bytes RLE")
