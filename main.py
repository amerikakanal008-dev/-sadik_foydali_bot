import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from yt_dlp import YoutubeDL

# Token server sozlamalaridan o'qiladi
BOT_TOKEN = os.getenv("8613590891:AAHpgTLtiAOFmmj4xfmym3cKYAemxAbm114")

bot = Bot(token=8613590891:AAHpgTLtiAOFmmj4xfmym3cKYAemxAbm114)
dp = Dispatcher()

if not os.path.exists('downloads'):
    os.makedirs('downloads')

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer("Salom! Men YouTube va Instagram yuklovchi botman. 🚀\nMenga YouTube linkini yuboring!")

@dp.message()
async def handle_links(message: types.Message):
    url = message.text
    if "youtube.com" in url or "youtu.be" in url:
        status_msg = await message.answer("Musiqa yuklab olinmoqda... ⏳")
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')
            
            audio_file = types.FSInputFile(filename)
            await message.answer_audio(audio_file, caption="Musiqa tayyor! 🎉")
            await status_msg.delete()
            os.remove(filename)
        except Exception as e:
            await message.answer(f"Xatolik: {str(e)}")
    else:
        await message.answer("Iltimos, to'g'ri YouTube havolasini yuboring. ⚠️")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
  
