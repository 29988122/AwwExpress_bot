import subprocess
from subprocess import Popen, PIPE, STDOUT, check_output
import requests
import logging
import json
import configparser
import telegram
import telegram.ext
from telegram.ext import Updater, MessageHandler, Filters
import dropbox

config = configparser.ConfigParser()
config.read_file(open("config.ini"))
bot_token = config.get("Telegram", "bot_token")
dropbox_token = config.get("Dropbox", "dropbox_token")
upload_to_folder = config.get("Dropbox", "upload_to_folder")
id = config.get("Streamable", "id")
pw = config.get("Streamable", "pw")

# TBD: formal logging.
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO)

# telegram.ext https://python-telegram-bot.org
updater = Updater(token=bot_token)
dispatcher = updater.dispatcher

class TransferData:
    def __init__(self, access_token):
        self.access_token = access_token

    def upload_file(self, file_from, file_to):
        """upload a file to Dropbox using API v2
        """
        dbx = dropbox.Dropbox(self.access_token)
        with open(file_from, "rb") as f:
            dbx.files_upload(f.read(), file_to, mute=True)
    
    def share_link(self, file_to):
        dbx = dropbox.Dropbox(self.access_token)
        link = dbx.sharing_create_shared_link(file_to, short_url=True)
        url = link.url
        return url

def vreddit(bot, update):
    #greet
    redditurl = update.message.text
    bot.send_message(chat_id=update.message.chat_id, text="안녕하세요, 저는 AwwExpress_bot입니다. 잠시만 기다려주세요!")

    #youtube-dl
    dlprocess = subprocess.Popen(["youtube-dl", redditurl, "--restrict-filenames"], stderr=PIPE, bufsize=1, universal_newlines=True)
    out, err = dlprocess.communicate()
    if err:
        print(err)
        bot.send_message(chat_id=update.message.chat_id, text=err)
        return
    else:
        bot.send_message(chat_id=update.message.chat_id, text="File downloaded successfully from reddit.\nI live beside reddit\"s server room, that\"s the secret.\nI\"m quite fast, right?")

    #fetch filename and pass to streamable
    youtubeoutputstring = check_output(["youtube-dl", redditurl, "--no-warnings", "--restrict-filenames", "--get-filename"], universal_newlines=True)
    youtubeoutputstring = str(youtubeoutputstring)
    youtubeoutputstring = youtubeoutputstring.rstrip()

    #streamable
    # url = "https://api.streamable.com/upload"
    # headers = {
    # "User-Agent": "My Personal Bot QQ",
    # "From": "a29988122@gmail.com"  # This is another valid field
    # }
    # files = {"file": open(youtubeoutputstring, "rb")}
    # r = requests.post(url, auth=(id, pw), files=files, headers=headers)
    # bot.send_message(chat_id=update.message.chat_id, text="少々お待ちください、streamableサーバーにアップロードしています。")
    
    # json_data = json.loads(r.text)
    # json_data = json_data["shortcode"]
    # print("Generated link: https://streamable.com/"+json_data)
    # bot.send_message(chat_id=update.message.chat_id, text="我幫你解決了討人厭又打不開的v.reddit.com！來，這裡是你的可愛圖： https://streamable.com/"+json_data)

    #dropbox
    access_token = dropbox_token
    transferData = TransferData(access_token)
    file_from = youtubeoutputstring
    file_to = upload_to_folder+youtubeoutputstring  # The full path to upload the file to, including the file name

    # API v2
    transferData.upload_file(file_from, file_to)
    url = transferData.share_link(file_to)
    print("Generated link: "+url)
    bot.send_message(chat_id=update.message.chat_id, text="我幫你解決了討人厭又打不開的v.reddit.com！\n來，這裡是你的可愛圖："+ url)


#trigger event of vreddit when Filters.text message detected
vreddit_handler = MessageHandler(Filters.text, vreddit)
dispatcher.add_handler(vreddit_handler)

updater.start_polling()