import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from yt_dlp import YoutubeDL

# Botingizning maxfiy tokeni to'g'ridan-to'g'ri kod ichiga yozildi
BOT_TOKEN = "8613590891:AAHpgTLtiAOFmmj4xfmym3cKYAemxAbm114"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Yuklanadigan fayllar uchun papka
if not os.path.exists('downloads'):
    os.makedirs('downloads')

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(
        "Salom! Men YouTube va Instagram yuklovchi botman. 🚀\n"
        "Menga YouTube videosining havolasini (linkini) yuboring, "
        "men uni sizga MP3 formatida yuklab beraman!"
    )

@dp.message()
async def handle_links(message: types.Message):
    url = message.text
    
    # YouTube havolasini tekshirish
    if "youtube.com" in url or "youtu.be" in url:
        status_msg = await message.answer("YouTube videosidan audio ajratib olinmoqda... ⏳")
        
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
            
            # Tayyor audioni foydalanuvchiga yuborish
            audio_file = types.FSInputFile(filename)
            await message.answer_audio(audio_file, caption="Musiqa yuklab olindi! 🎉")
            await status_msg.delete()
            
            # Server xotirasini tozalash
            os.remove(filename)
            
        except Exception as e:
            await message.answer(f"Xatolik yuz berdi: {str(e)}")
            await status_msg.delete()

    # Instagram havolasini tekshirish
    elif "instagram.com" in url:
        await message.answer("Instagram tizimi tez orada to'liq ishga tushiriladi! 📸")
        
    else:
        await message.answer("Iltimos, menga faqat YouTube yoki Instagram havolasini yuboring! ⚠️")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
    
