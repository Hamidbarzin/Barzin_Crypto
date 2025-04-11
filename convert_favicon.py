from PIL import Image
import os

# مسیرها
source_image = 'generated-icon.png'
favicon_output = 'static/icons/favicon-32x32.png'
apple_touch_output = 'static/icons/apple-touch-icon.png'

# اطمینان از وجود مسیر خروجی
os.makedirs(os.path.dirname(favicon_output), exist_ok=True)

# تبدیل فایکون
img = Image.open(source_image)
img_resized = img.resize((32, 32), Image.LANCZOS)
img_resized.save(favicon_output)

# تبدیل آیکون اپل
img_apple = img.resize((180, 180), Image.LANCZOS)
img_apple.save(apple_touch_output)

print(f"تصویر {source_image} با موفقیت به فایکون و آیکون اپل تبدیل شد.")