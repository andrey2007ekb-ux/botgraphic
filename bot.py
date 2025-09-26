import re
import logging
import matplotlib.pyplot as plt
from io import BytesIO
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Вставь сюда свой токен
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# --- Обработчик старта ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Пример запроса"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Привет! Я бот для построения проекций.\n"
        "Формат запроса:\n"
        "• проекция точки x 10 y 30 z 40\n"
        "• проекция прямой A(1,2,3) B(4,5,6)",
        reply_markup=reply_markup,
    )

# --- Парсинг и построение ---
def plot_point(x, y, z):
    fig, axs = plt.subplots(1, 3, figsize=(9, 3))

    # XY
    axs[0].scatter(x, y, color="red")
    axs[0].set_title("Проекция на XY")
    axs[0].set_xlabel("X")
    axs[0].set_ylabel("Y")

    # XZ
    axs[1].scatter(x, z, color="blue")
    axs[1].set_title("Проекция на XZ")
    axs[1].set_xlabel("X")
    axs[1].set_ylabel("Z")

    # YZ
    axs[2].scatter(y, z, color="green")
    axs[2].set_title("Проекция на YZ")
    axs[2].set_xlabel("Y")
    axs[2].set_ylabel("Z")

    buf = BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return buf

def plot_line(x1, y1, z1, x2, y2, z2):
    fig, axs = plt.subplots(1, 3, figsize=(9, 3))

    # XY
    axs[0].plot([x1, x2], [y1, y2], marker="o", color="red")
    axs[0].set_title("Прямая на XY")
    axs[0].set_xlabel("X")
    axs[0].set_ylabel("Y")

    # XZ
    axs[1].plot([x1, x2], [z1, z2], marker="o", color="blue")
    axs[1].set_title("Прямая на XZ")
    axs[1].set_xlabel("X")
    axs[1].set_ylabel("Z")

    # YZ
    axs[2].plot([y1, y2], [z1, z2], marker="o", color="green")
    axs[2].set_title("Прямая на YZ")
    axs[2].set_xlabel("Y")
    axs[2].set_ylabel("Z")

    buf = BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return buf

# --- Обработка сообщений ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    # проекция точки
    match_point = re.search(r"проекция точки x\s*(-?\d+)\s*y\s*(-?\d+)\s*z\s*(-?\d+)", text)
    if match_point:
        x, y, z = map(int, match_point.groups())
        buf = plot_point(x, y, z)
        await update.message.reply_photo(photo=buf, caption=f"Точка ({x}, {y}, {z})")
        return

    # проекция прямой
    match_line = re.search(
        r"проекция прямой a\((-?\d+),\s*(-?\d+),\s*(-?\d+)\)\s*b\((-?\d+),\s*(-?\d+),\s*(-?\d+)\)",
        text,
    )
    if match_line:
        x1, y1, z1, x2, y2, z2 = map(int, match_line.groups())
        buf = plot_line(x1, y1, z1, x2, y2, z2)
        await update.message.reply_photo(
            photo=buf,
            caption=f"Прямая A({x1},{y1},{z1}) → B({x2},{y2},{z2})"
        )
        return

    await update.message.reply_text("Не понял запрос. Формат:\n"
                                    "• проекция точки x 10 y 20 z 30\n"
                                    "• проекция прямой A(1,2,3) B(4,5,6)")

# --- Основная функция ---
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
