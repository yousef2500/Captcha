import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image
import io
import numpy as np
import cv2

# تحليل الصورة وتحديد المكان من 1 إلى 9
def match_emoji(image: Image.Image) -> int:
    img = np.array(image.convert("RGB"))
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    cell_h = img.shape[0] // 3
    cell_w = img.shape[1] // 3

    center = img[cell_h:2*cell_h, cell_w:2*cell_w]
    min_diff = float('inf')
    best_cell = 5  # الخانة في المنتصف

    idx = 1
    for row in range(3):
        for col in range(3):
            if row == 1 and col == 1:
                idx += 1
                continue
            cell = img[row*cell_h:(row+1)*cell_h, col*cell_w:(col+1)*cell_w]
            diff = np.sum(cv2.absdiff(cell, center))
            if diff < min_diff:
                min_diff = diff
                best_cell = idx
            idx += 1

    return best_cell

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أرسل صورة الكابتشا (الفاكهة) وسأخبرك بالمكان المناسب 🧠🍉")

# استلام صورة
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    byte_stream = await file.download_as_bytearray()
    image = Image.open(io.BytesIO(byte_stream))

    position = match_emoji(image)
    await update.message.reply_text(f"المكان المطابق هو: {position}️⃣")

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
