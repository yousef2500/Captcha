import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image
import io
import numpy as np
import cv2
from skimage.metrics import structural_similarity as ssim

def match_emoji(image: Image.Image) -> int:
    img = np.array(image.convert("RGB"))
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    h, w, _ = img.shape

    # قص صورة الفاكهة المطلوبة
    top_crop = img[int(0.22*h):int(0.32*h), int(0.30*w):int(0.70*w)]

    # قص الشبكة
    grid_crop = img[int(0.45*h):int(0.87*h), int(0.10*w):int(0.90*w)]
    gh, gw, _ = grid_crop.shape
    cell_h = gh // 3
    cell_w = gw // 3

    # تهيئة للمقارنة
    best_score = -1
    best_cell = 1
    idx = 1

    top_gray = cv2.cvtColor(top_crop, cv2.COLOR_BGR2GRAY)

    for row in range(3):
        for col in range(3):
            cell = grid_crop[row*cell_h:(row+1)*cell_h, col*cell_w:(col+1)*cell_w]
            cell_resized = cv2.resize(cell, (top_crop.shape[1], top_crop.shape[0]))
            cell_gray = cv2.cvtColor(cell_resized, cv2.COLOR_BGR2GRAY)
            score = ssim(top_gray, cell_gray)

            if score > best_score:
                best_score = score
                best_cell = idx
            idx += 1

    return best_cell

# أوامر البوت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أرسل صورة الكابتشا وسأحدد مكان الفاكهة بدقة 🍓📍")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    byte_stream = await file.download_as_bytearray()
    image = Image.open(io.BytesIO(byte_stream))

    try:
        position = match_emoji(image)
        await update.message.reply_text(f"✅ المكان المطابق هو: {position}️⃣")
    except Exception as e:
        await update.message.reply_text("❌ حدث خطأ أثناء تحليل الصورة.")
        print("خطأ:", e)

if __name__ == "__main__":
    token = os.getenv("BOT_TOKEN")
    if not token:
        print("❌ لم يتم العثور على توكن.")
        exit()

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("✅ البوت يعمل الآن...")
    app.run_polling()
