from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

@Client.on_message(filters.command("start"))
async def start_msg(client, message):

	kk = int(message.message_id) + 1
	keyb = [
		InlineKeyboardButton("Help", callback_data=f"helptxt_{str(kk)}"),
		InlineKeyboardButton("About", callback_data=f"abouttxt_{str(kk)}")
	]
	reply_markup = InlineKeyboardMarkup(keyb)


	await client.send_message(
		message.chat.id,
		f"Hi {message.from_user.mention},If you need any help, Just click help button.\n\nProject by @Harp_Tech",
		reply_markup=reply_markup,
		reply_to_message_id=message.message_id)

@Client.on_callback_query()
async def cb_handler(client, message):
	cb_income_dt = int(message.data.split("_", 1)[1])
	print(cb_income_dt)
	await client.send_message(message.chat.id, "Hello")