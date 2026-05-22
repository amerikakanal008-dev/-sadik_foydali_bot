import asyncio
import os
import re
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from yt_dlp import YoutubeDL

# Botingizning maxfiy tokeni
BOT_TOKEN = "8613590891:AAHpgTLtiAOFmmj4xfmym3cKYAemxAbm114"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

if not os.path.exists('downloads'):
    os.makedirs('downloads')

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(
        "Salom! Men kuchaytirilgan Media yuklovchi botman. 🚀\n\n"
        "🟢 **Menga nimalar yubora olasiz:**\n"
        "1. YouTube video/audio linki\n"
        "2. Instagram Reels/Video linki\n"
        "3. Shunchaki qo'shiq yoki video nomini (matn ko'rinishida)\n\n"
        "Sizga kerakli mediyani darhol topib yuklab beraman!"
    )

@dp.message()
async def handle_messages(message: types.Message):
    text = message.text
    
    # 1. INSTAGRAM LINKLARINI YUKLASH
    if "instagram.com" in text:
        status_msg = await message.answer("Instagram video yuklab olinmoqda... 📥")
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            # Ba'zan Instagram bloklamasligi uchun brauzer kabi ko'rsatish
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        }
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(text, download=True)
                filename = ydl.prepare_filename(info)
            
            video_file = types.FSInputFile(filename)
            await message.answer_video(video_file, caption="Instagramdan yuklab olindi! 📸")
            await status_msg.delete()
            os.remove(filename)
        except Exception as e:
            await message.answer("Instagram videosini yuklashda xatolik bo'ldi. Link xususiy (private) profilga tegishli bo'lishi mumkin. ⚠️")
            await status_msg.delete()

    # 2. YOUTUBE LINKLARINI YUKLASH
    elif "youtube.com" in text or "youtu.be" in text:
        status_msg = await message.answer("YouTube musiqasi ajratib olinmoqda... ⏳")
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
                info = ydl.extract_info(text, download=True)
                filename = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')
            
            audio_file = types.FSInputFile(filename)
            await message.answer_audio(audio_file, caption="YouTube'dan yuklab olindi! 🎵")
            await status_msg.delete()
            os.remove(filename)
        except Exception as e:
            await message.answer(f"Xatolik: {str(e)}")
            await status_msg.delete()

    # 3. MATN ORQALI MUSIQA QIDIRISH (Agar link bo'lmasa)
    else:
        status_msg = await message.answer(f"🔍 '{text}' bo'yicha eng yaxshi musiqa qidirilmoqda...")
        # ytsearch1: yozilgan matn bo'yicha YouTube'dan birinchi chiqqan natijani oladi
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'default_search': 'ytsearch1',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(text, download=True)
                # Agar qidiruv bo'lsa, entries ro'yxatidan birinchisini olamiz
                if 'entries' in info and len(info['entries']) > 0:
                    video_info = info['entries'][0]
                    filename = ydl.prepare_filename(video_info).replace('.webm', '.mp3').replace('.m4a', '.mp3')
                    title = video_info.get('title', 'Musiqa')
                else:
                    await status_msg.edit_text("Hech narsa topilmadi. 🤷‍♂️")
                    return

            audio_file = types.FSInputFile(filename)
            await message.answer_audio(audio_file, caption=f"Qidiruv natijasi: **{title}** 🎧")
            await status_msg.delete()
            os.remove(filename)
        except Exception as e:
            await message.answer("Musiqa topilmadi yoki yuklashda xatolik yuz berdi. ⚠️")
            await status_msg.delete()

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
    
