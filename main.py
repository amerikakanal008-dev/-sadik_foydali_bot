import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
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
        "Salom! Men professional Media yuklovchi botman. 🚀\n\n"
        "Menga YouTube yoki Instagram havolasini (link) yuboring, "
        "men sizga uni **Video** yoki **MP3** formatida yuklab beraman!"
    )

@dp.message(F.text)
async def handle_links(message: types.Message):
    url = message.text
    
    # Faqat YouTube va Instagram linklarini ushlab qolamiz
    if "youtube.com" in url or "youtu.be" in url or "instagram.com" in url:
        # Inline tugmalarni yasash
        builder = InlineKeyboardBuilder()
        # Callback data orqali link va formatni tugmaga yashiramiz
        builder.row(
            types.InlineKeyboardButton(text="🎬 Videoni yuklash", callback_data=f"vid|{url}"),
            types.InlineKeyboardButton(text="🎵 MP3 (Audio) yuklash", callback_data=f"aud|{url}")
        )
        
        await message.answer(
            "Media turi aniqlandi! Qaysi formatda yuklamoqchisiz? 👇",
            reply_markup=builder.as_markup()
        )
    else:
        # Agar link bo'lmasa, qo'shiq nomi deb hisoblab qidiradi (Avvalgi funksiya)
        status_msg = await message.answer(f"🔍 '{url}' nomi bo'yicha musiqa qidirilmoqda...")
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
                info = ydl.extract_info(url, download=True)
                if 'entries' in info and len(info['entries']) > 0:
                    video_info = info['entries'][0]
                    filename = ydl.prepare_filename(video_info).replace('.webm', '.mp3').replace('.m4a', '.mp3')
                    title = video_info.get('title', 'Musiqa')
                    audio_file = types.FSInputFile(filename)
                    await message.answer_audio(audio_file, caption=f"🎧 {title}")
                    os.remove(filename)
                else:
                    await message.answer("Hech narsa topilmadi. 🤷‍♂️")
            await status_msg.delete()
        except Exception:
            await message.answer("Musiqa topilmadi yoki xatolik yuz berdi. ⚠️")
            await status_msg.delete()

# TUGMALAR BOSILGANDA ISHLAYDIGAN QISM (CALLBACK QUERY)
@dp.callback_query(lambda call: call.data.startswith("vid|") or call.data.startswith("aud|"))
async def process_download(call: types.CallbackQuery):
    # Tugmadan ma'lumotlarni ajratib olamiz
    mode, url = call.data.split("|", 1)
    
    # "Yuklanmoqda" matni ko'rinishi uchun tugmalarni o'chiramiz
    await call.message.edit_text("Yuklash jarayoni boshlandi... ⏳ (Fayl hajmiga qarab biroz vaqt olishi mumkin)")
    
    if mode == "vid":
        # VIDEO YUKLASH SOZLAMALARI
        ydl_opts = {
            'format': 'best[ext=mp4]/best', # Eng yaxshi sifatli MP4 video
            'outtmpl': 'downloads/%(title)s.%(ext)s',
        }
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
            
            video_file = types.FSInputFile(filename)
            await call.message.answer_video(video_file, caption="Siz so'ragan video tayyor! 🎉")
            await call.message.delete()
            os.remove(filename)
        except Exception as e:
            await call.message.answer(f"Videoni yuklashda xatolik: {str(e)}")
            
    elif mode == "aud":
        # MP3 AUDIO YUKLASH SOZLAMALARI
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
            await call.message.answer_audio(audio_file, caption="Siz so'ragan MP3 tayyor! 🎵")
            await call.message.delete()
            os.remove(filename)
        except Exception as e:
            await call.message.answer(f"Audioni yuklashda xatolik: {str(e)}")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
    
