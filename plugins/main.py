import os
import time
import math
import asyncio
import logging
from youtube_dl import YoutubeDL
from youtube_dl.utils import (DownloadError, ContentTooShortError,
                ExtractorError, GeoRestrictedError,
                MaxDownloadsReached, PostProcessingError,
                UnavailableVideoError, XAttrMetadataError)
from asyncio import sleep
tdb = {}
import pyrogram
from pyrogram import Client, filters
from pyrogram.errors.exceptions.bad_request_400 import MessageNotModified 

import shutil

logging.basicConfig(
  level=logging.WARNING,
  format='%(name)s - [%(levelname)s] - %(message)s'
)
LOGGER = logging.getLogger(__name__)

# --- PROGRESS DEF --- #
async def progress_for_pyrogram(
  current,
  total,
  ud_type,
  message,
  start
):
  now = time.time()
  diff = now - start
  if round(diff % 10.00) == 0 or current == total:
    percentage = current * 100 / total
    speed = current / diff
    elapsed_time = round(diff) * 1000
    time_to_completion = round((total - current) / speed) * 1000
    estimated_total_time = elapsed_time + time_to_completion
    elapsed_time = time_formatter(milliseconds=elapsed_time)
    estimated_total_time = time_formatter(milliseconds=estimated_total_time)

    progress = "[{0}{1}] \n○ <b>Percentage :</b> {2}%\n○ <b>Completed :</b> ".format(
      ''.join(["█" for i in range(math.floor(percentage / 5))]),
      ''.join(["░" for i in range(20 - math.floor(percentage / 5))]),
      round(percentage, 3))

    tmp = progress + "{0} of {1}\n○ <b>Speed :</b> {2}/s\n○ <b>ETA :</b> {3}\n".format(
      humanbytes(current),
      humanbytes(total),
      humanbytes(speed),
      estimated_total_time if estimated_total_time != '' else "0 s",
    )
    try:
      await message.edit(
        text="{}\n {}".format(
          ud_type,
          tmp
        )
      )
    except MessageNotModified:
      pass

# --- HUMANBYTES DEF --- #
def humanbytes(size):
  if not size:
    return ""
  power = 2**10
  n = 0
  Dic_powerN = {0: ' ', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
  while size > power:
    size /= power
    n += 1
  return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'

# --- TIME FORMATTER DEF --- #
def time_formatter(milliseconds: int) -> str:
  seconds, milliseconds = divmod(int(milliseconds), 1000)
  minutes, seconds = divmod(seconds, 60)
  hours, minutes = divmod(minutes, 60)
  days, hours = divmod(hours, 24)
  tmp = ((str(days) + "d, ") if days else "") + \
    ((str(hours) + "h, ") if hours else "") + \
    ((str(minutes) + "m, ") if minutes else "") + \
    ((str(seconds) + "s, ") if seconds else "") + \
    ((str(milliseconds) + "ms, ") if milliseconds else "")
  return tmp[:-2]


@Client.on_message(filters.regex(pattern=".*http.* (.*)"))
async def download_video(client, message):
  url = message.text.split(None, 1)[0]
  type = message.text.split(None, 1)[1]

  if "playlist?list=" in url:
    msg = await message.reply("`Preparing to download...`")
  else:
    return await message.reply('`I think this is invalid link...`')

  out_folder = f"downloads/{message.from_user.id}/"
  if not os.path.isdir(out_folder):
    os.makedirs(out_folder)

  if type == "audio":
    opts = {
      'format':'bestaudio',
      'addmetadata':True,
      'noplaylist': False,
      'key':'FFmpegMetadata',
      'writethumbnail':True,
      'embedthumbnail':True,
      'prefer_ffmpeg':True,
      'geo_bypass':True,
      'nocheckcertificate':True,
      'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '320',
      }],
      'outtmpl':out_folder + '%(title)s.%(ext)s',
      'quiet':True,
      'logtostderr':False
    }
    video = False
    song = True

  elif type == "video":
    opts = {
      'format':'best',
      'addmetadata':True,
      'noplaylist': False,
      'getthumbnail':True,
      'embedthumbnail': True,
      'xattrs':True,
      'writethumbnail': True,
      'key':'FFmpegMetadata',
      'prefer_ffmpeg':True,
      'geo_bypass':True,
      'nocheckcertificate':True,
      'postprocessors': [{
        'key': 'FFmpegVideoConvertor',
        'preferedformat': 'mp4'},],
      'outtmpl':out_folder + '%(title)s.%(ext)s',
      'logtostderr':False,
      'quiet':True
    }
    song = False
    video = True

  try:
    await msg.edit("`Downloading Playlist...`")
    with YoutubeDL(opts) as ytdl:
      ytdl_data = ytdl.extract_info(url)
    filename = sorted(get_lst_of_files(out_folder, []))
  except DownloadError as DE:
    await msg.edit(f"`{str(DE)}`")
    return
  except ContentTooShortError:
    await msg.edit("`The download content was too short.`")
    return
  except GeoRestrictedError:
    await msg.edit(
      "`Video is not available from your geographic location due to geographic restrictions imposed by a website.`"
    )
    return
  except MaxDownloadsReached:
    await msg.edit("`Max-downloads limit has been reached.`")
    return
  except PostProcessingError:
    await msg.edit("`There was an error during post processing.`")
    return
  except UnavailableVideoError:
    await msg.edit("`Media is not available in the requested format.`")
    return
  except XAttrMetadataError as XAME:
    await msg.edit(f"`{XAME.code}: {XAME.msg}\n{XAME.reason}`")
    return
  except ExtractorError:
    await msg.edit("`There was an error during info extraction.`")
    return
  except Exception as e:
    await msg.edit(f"{str(type(e)): {str(e)}}")
    return
  c_time = time.time()
  await msg.edit("`Downloaded.`")
  if song:
    for single_file in filename:
      if os.path.exists(single_file):
        if single_file.endswith((".mp4", ".mp3", ".flac", ".webm")):
          thumb_image_path = f"{os.path.splitext(single_file)[0]}.jpg"
          if not os.path.exists(thumb_image_path):
            thumb_image_path = f"{os.path.splitext(single_file)[0]}.webp"
          elif os.path.exists(thumb_image_path):
            thumb_image_path = None
          try:
            ytdl_data_name_audio = os.path.basename(single_file)
            tnow = time.time()
            await client.send_audio(
              message.chat.id,
              single_file,
              caption=f"`{ytdl_data_name_audio}`",
              thumb=thumb_image_path,
              progress=progress_for_pyrogram,
              progress_args=("**__Uploading...__**", msg, tnow)
            )
          except Exception as e:
            await msg.edit("{} caused `{}`".format(single_file, str(e)))
            continue
          os.remove(single_file)
    shutil.rmtree(out_folder)
    await del_old_msg_send_msg(msg, client)

  if video:
    for single_file in filename:
      if os.path.exists(single_file):
        if single_file.endswith((".mp4", ".mp3", ".flac", ".webm")):
          thumb_image_path = f"{os.path.splitext(single_file)[0]}.jpg"
          if not os.path.exists(thumb_image_path):
            thumb_image_path = f"{os.path.splitext(single_file)[0]}.webp"
          elif os.path.exists(thumb_image_path):
            thumb_image_path = None
          try:
            ytdl_data_name_audio = os.path.basename(single_file)
            tnow = time.time()
            await client.send_video(
              message.chat.id,
              single_file,
              caption=f"`{ytdl_data_name_audio}`",
              thumb=thumb_image_path,
              progress=progress_for_pyrogram,
              progress_args=("**__Uploading...__**", msg, tnow)
            )
          except Exception as e:
            await msg.edit("{} caused `{}`".format(single_file, str(e)))
            continue
          os.remove(single_file)
    shutil.rmtree(out_folder)
    await del_old_msg_send_msg(msg, client)
    

def get_lst_of_files(input_directory, output_lst):
  filesinfolder = os.listdir(input_directory)
  for file_name in filesinfolder:
    current_file_name = os.path.join(input_directory, file_name)
    if os.path.isdir(current_file_name):
      return get_lst_of_files(current_file_name, output_lst)
    output_lst.append(current_file_name)
  return output_lst

async def del_old_msg_send_msg(msg, client):
  await msg.delete()
  await client.send_message(message.chat.id, "`Playlist Upload Success!`")
 
print("> Bot Started ")
