"""Generate PWA icons for Smart Inventory without external dependencies."""
import struct
import zlib
import os


def create_png(width, height, pixel_fn):
    """Create a PNG file with the given pixel function (supersampled for anti-aliasing)."""
    scale = 4  # supersampling factor
    w, h = width * scale, height * scale

    rows = []
    for y in range(h):
        row = bytearray([0])  # filter type 0
        for x in range(w):
            r, g, b, a = pixel_fn(x / scale, y / scale, width)
            row.extend([max(0, min(255, int(v))) for v in (r, g, b, a)])
        rows.append(bytes(row))

    def chunk(type_, data):
        return struct.pack('>I', len(data)) + type_ + data + struct.pack('>I', zlib.crc32(type_ + data))

    ihdr = chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0))
    idat = chunk(b'IDAT', zlib.compress(b''.join(rows), 9))
    iend = chunk(b'IEND', b'')
    return b'\x89PNG\r\n\x1a\n' + ihdr + idat + iend


def inside_rounded_rect(x, y, left, top, right, bottom, radius):
    """Check if point (x, y) is inside a rounded rectangle."""
    if x < left or x > right or y < top or y > bottom:
        return False
    if x < left + radius and y < top + radius:
        return (x - left - radius) ** 2 + (y - top - radius) ** 2 <= radius ** 2
    if x > right - radius and y < top + radius:
        return (x - right + radius) ** 2 + (y - top - radius) ** 2 <= radius ** 2
    if x < left + radius and y > bottom - radius:
        return (x - left - radius) ** 2 + (y - bottom + radius) ** 2 <= radius ** 2
    if x > right - radius and y > bottom - radius:
        return (x - right + radius) ** 2 + (y - bottom + radius) ** 2 <= radius ** 2
    return True


def make_app_icon(size, maskable=False):
    """Return a pixel function that draws the app icon."""
    def pixel_fn(x, y, size):
        # Background
        if maskable:
            left, top, right, bottom = 0, 0, size, size
            bg_inside = True
        else:
            m = size * 0.045
            left, top, right, bottom = m, m, size - m, size - m
            bg_inside = inside_rounded_rect(x, y, left, top, right, bottom, size * 0.19)

        if not bg_inside:
            return (0, 0, 0, 0)

        # Gradient blue background (#0a58ca -> #007bff)
        t = y / size
        r = 10 + (0 - 10) * t
        g = 88 + (123 - 88) * t
        b = 202 + (255 - 202) * t

        # White pill (capsule) shape in the center
        pill_left = size * 0.20
        pill_right = size * 0.80
        pill_top = size * 0.36
        pill_bottom = size * 0.64
        pill_radius = (pill_bottom - pill_top) / 2

        in_pill = inside_rounded_rect(x, y, pill_left, pill_top, pill_right, pill_bottom, pill_radius)

        if in_pill:
            split_half = size * 0.012
            if abs(x - size * 0.5) < split_half:
                return (190, 200, 210, 255)  # light gray split line
            rel_y = (y - pill_top) / (pill_bottom - pill_top)
            shade = 255 - int(rel_y * 25)
            return (shade, shade, shade, 255)

        return (r, g, b, 255)

    return pixel_fn


def main():
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons')
    os.makedirs(out_dir, exist_ok=True)

    png = create_png(192, 192, make_app_icon(192))
    with open(os.path.join(out_dir, 'icon-192x192.png'), 'wb') as f:
        f.write(png)

    png = create_png(512, 512, make_app_icon(512))
    with open(os.path.join(out_dir, 'icon-512x512.png'), 'wb') as f:
        f.write(png)

    png = create_png(512, 512, make_app_icon(512, maskable=True))
    with open(os.path.join(out_dir, 'icon-512x512-maskable.png'), 'wb') as f:
        f.write(png)

    print("Icons generated successfully!")
    for name in sorted(os.listdir(out_dir)):
        path = os.path.join(out_dir, name)
        print(f"  {name} ({os.path.getsize(path)} bytes)")


if __name__ == '__main__':
    main()