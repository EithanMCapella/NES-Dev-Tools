from PIL import Image

# Load image
img = Image.open("input.png").convert("RGBA")

width, height = img.size
assert width == 256 and height == 240, "Image must be 256x240"

pixels = []
for r, g, b, a in img.getdata():
    argb = (a << 24) | (r << 16) | (g << 8) | b
    pixels.append(f"0x{argb:08X}")

# Write Ripes-compatible output
with open("image_256x240.s", "w") as f:
    f.write(".data\n")
    f.write("image_256x240:\n")

    for i in range(0, len(pixels), 8):
        f.write("    .word " + ", ".join(pixels[i:i+8]) + "\n")

    f.write("\n.text\n")
    f.write("# image data only\n")

print("Done! Output saved as image_256x240.s")
