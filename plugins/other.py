from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

@Client.on_message(filters.command("start"))
async def start_msg(client, message):
	await message.reply_text(
		f"Hi {message.from_user.mention},If you need any help, Just click help button.\n\nProject by @Harp_Tech",
		reply_markup=InlineKeyboardMarkup(
				[[
					InlineKeyboardButton("🛠 Help", callback_data=f"help"),
					InlineKeyboardButton("🧰 About", callback_data=f"about")
				]]
			),
		quote=True)

@Client.on_callback_query()
async def cb_handler(client, update):
	cb_data = update.data
	
	if "help" in cb_data:
		await update.message.edit_text("Just Send URL with Format.(Audio/Video)\nExample: `https://youtube.com/playlist?list=xxxxxxxxxx audio`\n\nPowered by @Harp_Tech",
			reply_markup=InlineKeyboardMarkup(
				[[
					InlineKeyboardButton("🧰 About", callback_data=f"about"),
					InlineKeyboardButton("🔙 Back", callback_data=f"back")
				]]
			))
	elif "about" in cb_data:
		await update.message.edit_text("Language: Python\nFramework: Pyrogram\nEngine: YTDL\nCorded By: @Anjana_Ma\n\nPowered by @Harp_Tech",
			reply_markup=InlineKeyboardMarkup(
				[[
					InlineKeyboardButton("🛠 Help", callback_data=f"help"),
					InlineKeyboardButton("🔙 Back", callback_data=f"back")
				]]
			))
	elif "back" in cb_data:
		await update.message.edit_text(f"Hi {update.from_user.mention},If you need any help, Just click help button.\n\nProject by @Harp_Tech",
			reply_markup=InlineKeyboardMarkup(
				[[
					InlineKeyboardButton("🛠 Help", callback_data=f"help"),
					InlineKeyboardButton("🧰 About", callback_data=f"about")
				]]
			))