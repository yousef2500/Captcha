import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image
import io
import numpy as np
import cv2

# دالة مطابقة الفاكهة المطلوبة داخل الشبكة
def match_emoji(image: Image.Image) -> int:
    img = np.array(image.convert("RGB"))
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    h, w, _ = img.shape

    # --- قص صورة الفاكهة المطلوبة (النصف العلوي) ---
    top_crop = img[int(0.13*h):int(0.30*h), int(0.30*w):int(0.70*w)]

    # --- قص الشبكة (3x3) ---
    grid_crop = img[int(0.40*h):int(0.85*h), int(0.10*w):int(0.90*w)]
    gh, gw, _ = grid_crop.shape
    cell_h = gh // 3
    cell_w = gw // 3

    # --- مقارنة الفاكهة مع كل خلية ---
    min_diff = float('inf')
    best_cell = 1
    idx = 1
    for row in range(3):
        for col in range(3):
            cell = grid_crop[row*cell_h:(row+1)*cell_h, col*cell_w:(col+1)*cell_w]
            resized_top = cv2.resize(top_crop, (cell_w, cell_h))
            diff = np.sum(cv2.absdiff(resized_top, cell))
            if diff < min_diff:
                min_diff = diff
                best_cell = idx
            idx += 1

    return best_cell

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أرسل صورة الكابتشا وسأحدد لك المكان الصحيح للفواكه 🔍🍎")

# استقبال صورة كابتشا
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    byte_stream = await file.download_as_bytearray()
    image = Image.open(io.BytesIO(byte_stream))

    try:
        position = match_emoji(image)
        await update.message.reply_text(f"📍 المكان المطابق هو: {position}️⃣")
    except Exception as e:
        await update.message.reply_text("حدث خطأ أثناء تحليل الصورة ❌. تأكد من وضوحها.")
        print(f"خطأ: {e}")

# تشغيل البوت
if __name__ == "__main__":
    token = os.getenv("BOT_TOKEN")
    if not token:
        print("❌ خطأ: لم يتم العثور على متغير البيئة BOT_TOKEN.")
        exit()

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("✅ البوت يعمل الآن...")
    app.run_polling()
