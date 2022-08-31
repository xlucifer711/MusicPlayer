import os
from config import BOT_TOKEN, API_ID, API_HASH, OWNER_ID, SUPPORT, SESSION_NAME 
import glob
import json
import logging
import asyncio
import youtube_dl
from pytgcalls import StreamType
from pytube import YouTube
from youtube_search import YoutubeSearch
from pytgcalls import PyTgCalls, idle
from pytgcalls.types import Update
from pyrogram.raw.base import Update
from pytgcalls.types import AudioPiped, AudioVideoPiped
from pytgcalls.types import (
    HighQualityAudio,
    HighQualityVideo,
    LowQualityVideo,
    MediumQualityVideo
)
from pytgcalls.types.stream import StreamAudioEnded, StreamVideoEnded
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.errors import UserAlreadyParticipant, UserNotParticipant
from helpers.queues import QUEUE, add_to_queue, get_queue, clear_queue, pop_an_item
from helpers.admin_check import *

bot = Client(
    "AyameMusic",
    bot_token = os.environ["BOT_TOKEN"],
    api_id = int(os.environ["API_ID"]),
    api_hash = os.environ["API_HASH"]
)

client = Client(os.environ["SESSION_NAME"], int(os.environ["API_ID"]), os.environ["API_HASH"])

app = PyTgCalls(client)

OWNER_ID = int(os.environ["OWNER_ID"])
SUPPORT = os.environ["SUPPORT"]

LIVE_CHATS = []

START_TEXT = """━━━━━━━━━━━━━━━━━━━━━━
[🖤](https://te.legra.ph/file/597d7028d6d00a9389daa.jpg) ʜᴇʏ, <b>{}</b> 
ɪ ᴀᴍ ɴᴇxᴛ ʟᴇᴠᴇʟ ᴠᴄ ɢᴇɴᴇʀᴀᴛɪᴏɴ ʙᴏᴛ ᴏʀ sᴜᴘᴇʀ ғᴀsᴛ ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ ᴀɴᴅ ᴀʟsᴏ ᴀᴅᴅᴇᴅ ʜɪɢʜ sᴏᴜɴᴅ ǫᴜᴀʟɪᴛʏ 
ᴄʟɪᴄᴋ ᴏɴ ʜᴇʟᴩ ʙᴜᴛᴛᴏɴ ᴛᴏ ᴋɴᴏᴡ ᴀʟʟ ᴏғ ᴍʏ ᴄᴏᴍᴍᴀɴᴅs.
━━━━━━━━━━━━━━━━━━━━━━
"""

START_BUTTONS = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                        "➕ ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ➕", url="https://t.me/AyameMusicBot?startgroup=true")
        ],
        [
            InlineKeyboardButton("🏩 ᴜᴘᴅᴀᴛᴇs ", url=f"https://t.me/TechQuard"),
            InlineKeyboardButton("⛪ sᴜᴘᴘᴏʀᴛ", url=f"https://t.me/{SUPPORT}")
        ],
        [
            InlineKeyboardButton("📄 ʜᴇʟᴘ ᴀɴᴅ ᴄᴍᴅ", url="https://te.legra.ph/%E1%B4%8D%E1%B4%80%C9%AA%C9%B4-%E1%B4%84%E1%B4%8F%E1%B4%8D%E1%B4%8D%E1%B4%80%C9%B4%E1%B4%85s-08-31")
        ],
        [
            InlineKeyboardButton("🚦 ᴅᴇᴠᴇʟᴏᴘᴇʀ ", url=f"https://t.me/Mr_Disaster_xd"),
            InlineKeyboardButton("💠 ʏᴏᴜᴛᴜʙᴇ", url="https://youtube.com/channel/UCtI7hbY-BD7wvuIzoSU0cEw")
        ]
    ]
)

BUTTONS = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("▷", callback_data="resume"),
            InlineKeyboardButton("II", callback_data="pause"),
            InlineKeyboardButton("‣‣I", callback_data="skip"),
            InlineKeyboardButton("▢", callback_data="end"),
        ],
        [
            InlineKeyboardButton("🏩 ᴜᴘᴅᴀᴛᴇs ", url=f"https://t.me/TechQuard"),
            InlineKeyboardButton("⛪ sᴜᴘᴘᴏʀᴛ", url=f"https://t.me/{SUPPORT}")
        ],
        [
            InlineKeyboardButton(" ᴄʟᴏsᴇ​ ", callback_data="close")
        ]
    ]
)

async def skip_current_song(chat_id):
    if chat_id in QUEUE:
        chat_queue = get_queue(chat_id)
        if len(chat_queue) == 1:
            await app.leave_group_call(chat_id)
            clear_queue(chat_id)
            return 1
        else:
            title = chat_queue[1][0]
            duration = chat_queue[1][1]
            link = chat_queue[1][2]
            playlink = chat_queue[1][3]
            type = chat_queue[1][4]
            Q = chat_queue[1][5]
            thumb = chat_queue[1][6]
            if type == "Audio":
                await app.change_stream(
                    chat_id,
                    AudioPiped(
                        playlink,
                    ),
                )
            elif type == "Video":
                if Q == "high":
                    hm = HighQualityVideo()
                elif Q == "mid":
                    hm = MediumQualityVideo()
                elif Q == "low":
                    hm = LowQualityVideo()
                else:
                    hm = MediumQualityVideo()
                await app.change_stream(
                    chat_id, AudioVideoPiped(playlink, HighQualityAudio(), hm)
                )
            pop_an_item(chat_id)
            await bot.send_photo(chat_id, photo = thumb,
                                 caption = f"» sᴋɪᴘ ᴛʜᴇ ᴍᴜsɪᴄ ʙᴏᴛ\n\n🎬 <b>ɴᴀᴍᴇ :</b> [{yt.title}]({link})\n⏰ <b>ᴅᴜʀᴀᴛɪᴏɴ:</b> {duration}\n👀 <b>sᴛʀᴇᴀᴍ ᴛʏᴩᴇ :</b> `{doom}`",
                                 reply_markup = BUTTONS)
            return [title, link, type, duration, thumb]
    else:
        return 0


async def skip_item(chat_id, lol):
    if chat_id in QUEUE:
        chat_queue = get_queue(chat_id)
        try:
            x = int(lol)
            title = chat_queue[x][0]
            chat_queue.pop(x)
            return title
        except Exception as e:
            print(e)
            return 0
    else:
        return 0


@app.on_stream_end()
async def on_end_handler(_, update: Update):
    if isinstance(update, StreamAudioEnded):
        chat_id = update.chat_id
        await skip_current_song(chat_id)


@app.on_closed_voice_chat()
async def close_handler(client: PyTgCalls, chat_id: int):
    if chat_id in QUEUE:
        clear_queue(chat_id)
        

async def yt_video(link):
    proc = await asyncio.create_subprocess_exec(
        "yt-dlp",
        "-g",
        "-f",
        "best[height<=?720][width<=?1280]",
        f"{link}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if stdout:
        return 1, stdout.decode().split("\n")[0]
    else:
        return 0, stderr.decode()
    

async def yt_audio(link):
    proc = await asyncio.create_subprocess_exec(
        "yt-dlp",
        "-g",
        "-f",
        "bestaudio",
        f"{link}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if stdout:
        return 1, stdout.decode().split("\n")[0]
    else:
        return 0, stderr.decode()


@bot.on_callback_query()
async def callbacks(_, cq: CallbackQuery):
    user_id = cq.from_user.id
    try:
        user = await cq.message.chat.get_member(user_id)
        admin_strings = ("creator", "administrator")
        if user.status not in admin_strings:
            is_admin = False
        else:
            is_admin = True
    except ValueError:
        is_admin = True        
    if not is_admin:
        return await cq.answer("» ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")   
    chat_id = cq.message.chat.id
    data = cq.data
    if data == "close":
        return await cq.message.delete()
    if not chat_id in QUEUE:
        return await cq.answer("» ɴᴏᴛʜɪɴɢ ɪs ᴩʟᴀʏɪɴɢ.")

    if data == "pause":
        try:
            await app.pause_stream(chat_id)
            await cq.answer("» ᴛʀᴀᴄᴋ ᴘᴀᴜsᴇᴅ.")
        except:
            await cq.answer("» ɴᴏᴛʜɪɴɢ ɪs ᴩʟᴀʏɪɴɢ.")
      
    elif data == "resume":
        try:
            await app.resume_stream(chat_id)
            await cq.answer("» ᴛʀᴀᴄᴋ ʀᴇsᴜᴍᴇᴅ.")
        except:
            await cq.answer("» ɴᴏᴛʜɪɴɢ ɪs ᴩʟᴀʏɪɴɢ.")   

    elif data == "end":
        await app.leave_group_call(chat_id)
        clear_queue(chat_id)
        await cq.answer("» sᴛʀᴇᴀᴍ ᴇɴᴅᴇᴅ.")  

    elif data == "skip":
        op = await skip_current_song(chat_id)
        if op == 0:
            await cq.answer("» ǫᴜᴇᴜᴇ ᴇᴍᴘᴛʏ.")
        elif op == 1:
            await cq.answer("» ǫᴜᴇᴜᴇ ᴇᴍᴘᴛʏ, ᴄʟᴏsᴇᴅ sᴛʀᴇᴀᴍɪɴɢ.")
        else:
            await cq.answer("» ᴛʀᴀᴄᴋ sᴋɪᴘᴘᴇᴅ.")
            

@bot.on_message(filters.command("start") & filters.private)
async def start_private(_, message):
    msg = START_TEXT.format(message.from_user.mention, OWNER_ID)
    await message.reply_text(text = msg,
                             reply_markup = START_BUTTONS)
    

@bot.on_message(filters.command(["ping", "alive"]) & filters.group)
async def start_group(_, message):
    await message.delete()
    fuk = "<b>ᴩᴏɴɢ ʙᴀʙʏ !</b>"
    await message.reply_photo(photo="https://te.legra.ph/file/03ad87e41b9f6419660e4.jpg", caption=fuk)


@bot.on_message(filters.command(["join", "userbotjoin"]) & filters.group)
@is_admin
async def join_chat(c: Client, m: Message):
    chat_id = m.chat.id
    try:
        invitelink = await c.export_chat_invite_link(chat_id)
        if invitelink.startswith("https://t.me/+"):
            invitelink = invitelink.replace(
                "https://t.me/+", "https://t.me/joinchat/"
            )
            await client.join_chat(invitelink)
            return await client.send_message(chat_id, "**» ᴀssɪsᴛᴀɴᴛ sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴊᴏɪɴᴇᴅ ᴛʜᴇ ᴄʜᴀᴛ.**")
    except UserAlreadyParticipant:
        return await client.send_message(chat_id, "**» ᴀssɪsᴛᴀɴᴛ ᴀʟʀᴇᴀᴅʏ ᴊᴏɪɴᴇᴅ ᴛʜᴇ ᴄʜᴀᴛ.**")

    
@bot.on_message(filters.command(["play", "vplay"]) & filters.group)
async def video_play(_, message):
    await message.delete()
    user_id = message.from_user.id
    state = message.command[0].lower()
    try:
        query = message.text.split(None, 1)[1]
    except:
        return await message.reply_photo(
                     photo=f"https://te.legra.ph/file/03ad87e41b9f6419660e4.jpg",
                    caption="💌 **ᴜsᴀɢᴇ: /play ɢɪᴠᴇ ᴀ ᴛɪᴛʟᴇ sᴏɴɢ ᴛᴏ ᴘʟᴀʏ ᴍᴜsɪᴄ ᴏʀ /vplay ғᴏʀ ᴠɪᴅᴇᴏ ᴘʟᴀʏ**")                
    chat_id = message.chat.id
    if chat_id in LIVE_CHATS:
        return await message.reply_text("» ᴩʟᴇᴀsᴇ sᴇɴᴅ <code>/end</code> ᴛᴏ ᴇɴᴅ ᴛʜᴇ ᴏɴɢᴏɪɴɢ ʟɪᴠᴇ sᴛʀᴇᴀᴍ ᴀɴᴅ sᴛᴀʀᴛ ᴩʟᴀʏɪɴɢ sᴏɴɢs ᴀɢᴀɪɴ.")
    
    m = await message.reply_text("**» sᴇᴀʀᴄʜɪɴɢ, ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...**")
    if state == "play":
        damn = AudioPiped
        ded = yt_audio
        doom = "ᴀᴜᴅɪᴏ"
    elif state == "vplay":
        damn = AudioVideoPiped
        ded = yt_video
        doom = "ᴠɪᴅᴇᴏ"
    if "low" in query:
        Q = "low"
    elif "mid" in query:
        Q = "mid"
    elif "high" in query:
        Q = "high"
    else:
        Q = "0"
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        link = f"https://youtube.com{results[0]['url_suffix']}"
        thumb = results[0]["thumbnails"][0]
        duration = results[0]["duration"]
        yt = YouTube(link)
        cap = f"🎬 <b>ɴᴀᴍᴇ :</b> [{yt.title}]({link})\n⏰ <b>ᴅᴜʀᴀᴛɪᴏɴ:</b> {duration}\n👀 <b>sᴛʀᴇᴀᴍ ᴛʏᴩᴇ :</b> `{doom}`"
        try:
            ydl_opts = {"format": "bestvideo[height<=720]+bestaudio/best[height<=720]"}
            ydl = youtube_dl.YoutubeDL(ydl_opts)
            info_dict = ydl.extract_info(link, download=False)
            p = json.dumps(info_dict)
            a = json.loads(p)
            playlink = a['formats'][1]['manifest_url']
        except:
            ice, playlink = await ded(link)
            if ice == "0":
                return await m.edit("❗️YTDL ERROR !!!")               
    except Exception as e:
        return await m.edit(str(e))
    
    try:
        if chat_id in QUEUE:
            position = add_to_queue(chat_id, yt.title, duration, link, playlink, doom, Q, thumb)
            caps = f"» <b>ǫᴜᴇᴜᴇᴅ ᴘᴏsɪᴛɪᴏɴ ᴀᴛ {position}</b> \n\n🎬 <b>ɴᴀᴍᴇ :</b> [{yt.title}]({link})\n⏰ <b>ᴅᴜʀᴀᴛɪᴏɴ:</b> {duration}"
            await message.reply_photo(thumb, caption=caps)
            await m.delete()
        else:            
            await app.join_group_call(
                chat_id,
                damn(playlink),
                stream_type=StreamType().pulse_stream
            )
            add_to_queue(chat_id, yt.title, duration, link, playlink, doom, Q, thumb)
            await message.reply_photo(thumb, caption=cap, reply_markup=BUTTONS)
            await m.delete()
    except Exception as e:
        return await m.edit(str(e))
    
    
@bot.on_message(filters.command(["stream", "vstream"]) & filters.group)
@is_admin
async def stream_func(_, message):
    await message.delete()
    state = message.command[0].lower()
    try:
        link = message.text.split(None, 1)[1]
    except:
        return await message.reply_text(f"<b>Usage:</b> <code>/{state} [link]</code>")
    chat_id = message.chat.id
    
    if state == "stream":
        damn = AudioPiped
        emj = "🎵"
    elif state == "vstream":
        damn = AudioVideoPiped
        emj = "🎬"
    m = await message.reply_text("» ᴘʀᴏᴄᴇssɪɴɢ ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...")
    try:
        if chat_id in QUEUE:
            return await m.edit("❗️Please send <code>/end</code> to end voice chat before live streaming.")
        elif chat_id in LIVE_CHATS:
            await app.change_stream(
                chat_id,
                damn(link)
            )
            await m.edit(f"{emj} Started streaming: [Link]({link})", disable_web_page_preview=True)
        else:    
            await app.join_group_call(
                chat_id,
                damn(link),
                stream_type=StreamType().pulse_stream)
            await m.edit(f"{emj} Started streaming: [Link]({link})", disable_web_page_preview=True)
            LIVE_CHATS.append(chat_id)
    except Exception as e:
        return await m.edit(str(e))


@bot.on_message(filters.command("skip") & filters.group)
@is_admin
async def skip(_, message):
    await message.delete()
    chat_id = message.chat.id
    if len(message.command) < 2:
        op = await skip_current_song(chat_id)
        if op == 0:
            await message.reply_text("» ǫᴜᴇᴜᴇ ᴇᴍᴘᴛʏ..")
        elif op == 1:
            await message.reply_text("» ǫᴜᴇᴜᴇ ᴇᴍᴘᴛʏ, ᴄʟᴏsᴇᴅ sᴛʀᴇᴀᴍɪɴɢ.")
    else:
        skip = message.text.split(None, 1)[1]
        out = "🗑 <b>ʀᴇᴍᴏᴠᴇ ᴛʜᴇ ғᴏʟʟᴏᴡɪɴɢ sᴏɴɢs (s) ғʀᴏᴍ ᴛʜᴇ ǫᴜᴇᴜᴇ:</b> \n"
        if chat_id in QUEUE:
            items = [int(x) for x in skip.split(" ") if x.isdigit()]
            items.sort(reverse=True)
            for x in items:
                if x == 0:
                    pass
                else:
                    hm = await skip_item(chat_id, x)
                    if hm == 0:
                        pass
                    else:
                        out = out + "\n" + f"<b>» {x}</b> - {hm}"
            await message.reply_text(out)
            
            
@bot.on_message(filters.command(["playlist", "queue"]) & filters.group)
@is_admin
async def playlist(_, message):
    chat_id = message.chat.id
    if chat_id in QUEUE:
        chat_queue = get_queue(chat_id)
        if len(chat_queue) == 1:
            await message.delete()
            await message.reply_text(
                f"🍁 <b>ᴄᴜʀʀᴇɴᴛʟʏ ᴩʟᴀʏɪɴɢ :</b> [{chat_queue[0][0]}]({chat_queue[0][2]}) | `{chat_queue[0][4]}`",
                disable_web_page_preview=True,
            )
        else:
            out = f"<b>📃 ǫᴜᴇᴜᴇ :</b> \n\n🍁 <b>ᴩʟᴀʏɪɴɢ :</b> [{chat_queue[0][0]}]({chat_queue[0][2]}) | `{chat_queue[0][4]}` \n"
            l = len(chat_queue)
            for x in range(1, l):
                title = chat_queue[x][0]
                link = chat_queue[x][2]
                type = chat_queue[x][4]
                out = out + "\n" + f"<b>» {x}</b> - [{title}]({link}) | `{type}` \n"
            await message.reply_text(out, disable_web_page_preview=True)
    else:
        await message.reply_text("» ɴᴏᴛʜɪɴɢ ɪs ᴩʟᴀʏɪɴɢ.")
    

@bot.on_message(filters.command(["end", "stop"]) & filters.group)
@is_admin
async def end(_, message):
    await message.delete()
    chat_id = message.chat.id
    if chat_id in LIVE_CHATS:
        await app.leave_group_call(chat_id)
        LIVE_CHATS.remove(chat_id)
        return await message.reply_text("» sᴛʀᴇᴀᴍ ᴇɴᴅᴇᴅ.")
        
    if chat_id in QUEUE:
        await app.leave_group_call(chat_id)
        clear_queue(chat_id)
        await message.reply_text("» sᴛʀᴇᴀᴍ ᴇɴᴅᴇᴅ.")
    else:
        await message.reply_text("» ɴᴏᴛʜɪɴɢ ɪs ᴩʟᴀʏɪɴɢ.")
        

@bot.on_message(filters.command("pause") & filters.group)
@is_admin
async def pause(_, message):
    await message.delete()
    chat_id = message.chat.id
    if chat_id in QUEUE:
        try:
            await app.pause_stream(chat_id)
            await message.reply_text("» ᴛʀᴀᴄᴋ ᴘᴀᴜsᴇᴅ.")
        except:
            await message.reply_text("» ɴᴏᴛʜɪɴɢ ɪs ᴩʟᴀʏɪɴɢ.")
    else:
        await message.reply_text("» ɴᴏᴛʜɪɴɢ ɪs ᴩʟᴀʏɪɴɢ.")
        
        
@bot.on_message(filters.command("resume") & filters.group)
@is_admin
async def resume(_, message):
    await message.delete()
    chat_id = message.chat.id
    if chat_id in QUEUE:
        try:
            await app.resume_stream(chat_id)
            await message.reply_text("» ᴛʀᴀᴄᴋ ʀᴇsᴜᴍᴇᴅ.")
        except:
            await message.reply_text("» ɴᴏᴛʜɪɴɢ ɪs ᴩʟᴀʏɪɴɢ.")
    else:
        await message.reply_text("» ɴᴏᴛʜɪɴɢ ɪs ᴩʟᴀʏɪɴɢ.")


@bot.on_message(filters.command("restart"))
async def restart(_, message):
    user_id = message.from_user.id
    if user_id != OWNER_ID:
        return
    await message.reply_text("» <i>ʀᴇsᴛᴀʀᴛɪɴɢ ʙᴀʙʏ...</i>")
    os.system(f"kill -9 {os.getpid()} && python3 app.py")
            

app.start()
bot.run()
idle()
