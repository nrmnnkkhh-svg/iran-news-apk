import struct
import zlib


def png_chunk(tag, data):
    chunk = struct.pack(">I", len(data)) + tag + data
    chunk += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    return chunk


def make_icon(path, size):
    margin = size * 0.06
    corner = size * 0.22
    cx = cy = (size - 1) / 2.0
    r_dot = size * 0.10
    r_in = size * 0.17
    r_out = size * 0.30

    bg = (14, 20, 32)
    red = (225, 29, 72)
    pink = (251, 113, 133)

    x0 = y0 = margin
    x1 = y1 = size - 1 - margin

    rows = []
    for y in range(size):
        row = bytearray()
        for x in range(size):
            nx = min(max(x, x0 + corner), x1 - corner)
            ny = min(max(y, y0 + corner), y1 - corner)
            dx = x - nx
            dy = y - ny
            inside = (dx * dx + dy * dy) <= corner * corner

            if not inside:
                row += bytes((0, 0, 0, 0))
                continue

            d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5

            if d <= r_dot:
                r, g, b = pink
            elif d <= r_in:
                r, g, b = bg
            elif d <= r_out:
                r, g, b = red
            else:
                r, g, b = bg

            row += bytes((r, g, b, 255))
        rows.append(bytes(row))

    raw = b"".join(b"\x00" + row for row in rows)

    header = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    png = (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", header)
        + png_chunk(b"IDAT", zlib.compress(raw, 9))
        + png_chunk(b"IEND", b"")
    )

    with open(path, "wb") as f:
        f.write(png)

    print(f"created {path}")


make_icon("icon-192.png", 192)
make_icon("icon-512.png", 512)
