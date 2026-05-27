import re

WIDTH = 32
HEIGHT = 30   # NES nametable tile height

# This compression uses a byte to represent 4 metatiles
# 2 bits per metatile, max 4 metatiles

METATILES = {
    (0x00, 0x00, 0x00, 0x00): 0,
    (0x04, 0x05, 0x14, 0x15): 1,
    (0x06, 0x07, 0x16, 0x17): 2,
    (0x08, 0x09, 0x18, 0x19): 3,
}


def read_tiles(filename):
    """Parse .asm file and return tile data + attribute data"""

    with open(filename) as f:
        text = f.read()

    matches = re.findall(r"\$([0-9A-Fa-f]{2})", text)
    data = [int(x, 16) for x in matches]

    print("Total bytes in file:", len(data))

    tiles = data
    attributes = []

    # Detect full nametable export
    if len(data) == 1024:
        print("Detected attribute table, separating last 64 bytes")

        tiles = data[:960]
        attributes = data[960:]

    return tiles, attributes


def build_grid(tiles):
    """Convert flat tile list into 2D grid"""

    grid = []
    for y in range(HEIGHT):
        row = tiles[y * WIDTH:(y + 1) * WIDTH]
        grid.append(row)

    return grid


def extract_metatiles(grid):
    """Convert 2x2 tiles into metatile indices"""

    meta_rows = []

    for y in range(0, HEIGHT, 2):
        row = []

        for x in range(0, WIDTH, 2):
            tl = grid[y][x]
            tr = grid[y][x + 1]
            bl = grid[y + 1][x]
            br = grid[y + 1][x + 1]

            key = (tl, tr, bl, br)

            if key not in METATILES:
                raise ValueError(f"Unknown metatile pattern {key}")

            row.append(METATILES[key])

        meta_rows.append(row)

    return meta_rows


def pack_bytes(meta_rows):
    """Pack 4 metatiles (2 bits each) into one byte"""

    packed_rows = []

    for row in meta_rows:
        packed = []

        for i in range(0, len(row), 4):
            m0, m1, m2, m3 = row[i:i+4]

            byte = (
                (m0 << 6) |
                (m1 << 4) |
                (m2 << 2) |
                m3
            )

            packed.append(byte)

        packed_rows.append(packed)

    return packed_rows


def print_metatile_map(packed_rows):
    print("\nmetatile_map:")

    for row in packed_rows:
        values = ",".join(f"${b:02X}" for b in row)
        print(f"    .byte {values}")


def print_attributes(attributes):
    """Print attribute table so it can still be used by the NES"""

    if not attributes:
        return

    print("\nattribute_table:")

    for i in range(0, len(attributes), 8):
        row = attributes[i:i+8]
        values = ",".join(f"${b:02X}" for b in row)
        print(f"    .byte {values}")


def main():
    tiles, attributes = read_tiles("map.asm")

    grid = build_grid(tiles)

    meta_rows = extract_metatiles(grid)

    packed = pack_bytes(meta_rows)

    print_metatile_map(packed)

    print_attributes(attributes)


if __name__ == "__main__":
    main()