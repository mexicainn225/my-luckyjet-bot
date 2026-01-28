import telebot
bot = telebot.TeleBot('8373837099:AAEffbpvjdegwuUgGT5nvPHAWB_oxSLIdu0')

@bot.message_handler(content_types=['video'])
def get_id(message):
    bot.reply_to(message, f"Voici l'ID de ta vidéo :\n\n`{message.video.file_id}`")

bot.infinity_polling()
