import xml.etree.ElementTree as ET
import os
import io

from PIL import Image, ImageDraw, ImageFont

# Boyutlar
width = 512
height = 512

# Yeni temiz bir PNG oluştur (Arka plan Bordo, rgba = 128, 0, 32, 255)
img = Image.new('RGBA', (width, height), (128, 0, 32, 255))
draw = ImageDraw.Draw(img)

# İç Çerçeve (Krem rengi, #F5F5DC)
draw.rounded_rectangle(
    [(32, 32), (480, 480)],
    radius=96,
    outline=(245, 245, 220, 128),  # %50 opacity
    width=12
)

# Text 'HY'
# Font sorunu olmaması için standart bir font ya da font yüklemesi denemesi yapalım
try:
    font = ImageFont.truetype("arialbd.ttf", 200)
except IOError:
    # Font bulunamazsa default font kullan ama devasa olsun
    font = ImageFont.load_default()

# Metni ortala (approximate)
text = "HY"
# Bounding box of text
try: # pillow 10.0+
    bbox = draw.textbbox((0,0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
except AttributeError:
    text_w, text_h = draw.textsize(text, font=font)

x = (width - text_w) / 2
y = (height - text_h) / 2 - 20 # Biraz yukarı taşı kalp için

draw.text((x, y), text, font=font, fill=(245, 245, 220, 255))

# Kalp çizimi (Pembe #FFB6C1)
# SVG Path'ten dönüştürülmüş basit kalp şekli koordinatları
heart_coords = [
    (256, 420), (220, 380), (200, 340), (220, 310), (256, 330),
    (292, 310), (312, 340), (292, 380), (256, 420)
]
draw.polygon(heart_coords, fill=(255, 182, 193, 204))

# Kaydet
img.save("static/img/apple-touch-icon.png")
print("PNG dosyasi basariyla olusturuldu.")
