import logging, requests, urllib3
urllib3.disable_warnings()
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=
        "This bot will send links to pyload for you.\n"+
        "To download files you will need to provide the following:\n"+
        "- Package-Name (the name for the pyload-queue)\n"+
        "- Downloadlink (make sure it works, the bot is dumb)\n"+
        "- Package-PW (Insert none for no pw)\n\n"+
        "Sample request single download:\n"+
        "/download test;https://...zip;password123\n\n"+
        "Sample request multiple links per package:\n"+
        "/download bla;https://..iso;http://..zip;pass\n\n"+
        "Caution:\nFor packages with multiple links, make sure to paste them with http(s) otherwise the bot will not pick it up.\n\n"+
        "Not supported yet:\n"+
        "- Containers")

async def download_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /download is issued."""
    admin = "__BOT__ID__"
    user = update.message.from_user.id
    #print(user)
    #print(admin)
    if str(admin) == str(user):
    # correct user == authorized
        pyloadcookie = loginpyload()
        # session cookie
        downurl = update.message.text[10:]
        listurls = downurl.split(";")
        if len(listurls) < 3:
            # invalid request
            await update.message.reply_text("Invalid request!")
        elif len(listurls) == 3:
            # single file
            if listurls[2] == "none":
                listurls[2] = ""
            single_response = sendtopyload_single(listurls[0], listurls[1], listurls[2], pyloadcookie[15:])
            await update.message.reply_text("Server responded with: " + str(single_response))
        elif len(listurls) > 3:
            # multiple urls
            package_pw = listurls[-1]
            package_name = listurls[0]
            listurls.pop(0)
            listurls.pop(-1)
            multi_url = ""
            for f in listurls:
                multi_url = multi_url + "\r\n" + f
            single_response = sendtopyload_single(package_name, multi_url, package_pw, pyloadcookie[15:])
            await update.message.reply_text("Server responded with: " + str(single_response))
    else:
        await update.message.reply_text("Unauthorized!")

def loginpyload():
    # get session cookie
    headers = {
    	'Host': 'download.0idea.dev',
    	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.5304.63 Safari/537.36',
    	'Content-Type': 'application/x-www-form-urlencoded',
	}
    params = {
    	'next': 'http://download.0idea.dev/',
	}
    data = 'do=login&username=down&password=__REPLACE_THIS_WITH_YOUR_PW__&submit=Login'
    response = requests.post('https://download.0idea.dev/login', params=params, headers=headers, data=data, verify=False) 
    sescookie = (response.headers["Set-Cookie"]).split(";")
    return sescookie[0]

def sendtopyload_single(package_name, single_url, package_pw, pycookie):
    # one single url to download
    cookies = {
    	'pyload_session': pycookie,
	}
    headers = {
    	'Host': 'download.0idea.dev',
    	'Sec-Ch-Ua': '"Chromium";v="107", "Not=A?Brand";v="24"',
    	'Accept': '*/*',
    	'Content-Type': 'multipart/form-data; boundary=----WebKitFormBoundaryZZEdj8mvw32GO6oJ',
    	'X-Requested-With': 'XMLHttpRequest',
    	'Sec-Ch-Ua-Mobile': '?0',
    	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.5304.63 Safari/537.36',
    	'Sec-Ch-Ua-Platform': '"Linux"',
    	'Origin': 'https://download.0idea.dev',
    	'Sec-Fetch-Site': 'same-origin',
    	'Sec-Fetch-Mode': 'cors',
    	'Sec-Fetch-Dest': 'empty',
    	'Referer': 'https://download.0idea.dev/',
    	'Accept-Language': 'en-US,en;q=0.9',
    	'Cookie': 'pyload_session=' + pycookie,
	}
    data = '------WebKitFormBoundaryZZEdj8mvw32GO6oJ\r\nContent-Disposition: form-data; name="add_name"\r\n\r\n' + package_name + '\r\n------WebKitFormBoundaryZZEdj8mvw32GO6oJ\r\nContent-Disposition: form-data; name="add_links"\r\n\r\n' + single_url + '\r\n------WebKitFormBoundaryZZEdj8mvw32GO6oJ\r\nContent-Disposition: form-data; name="add_password"\r\n\r\n' + package_pw + '\r\n------WebKitFormBoundaryZZEdj8mvw32GO6oJ\r\nContent-Disposition: form-data; name="add_file"; filename=""\r\nContent-Type: application/octet-stream\r\n\r\n\r\n------WebKitFormBoundaryZZEdj8mvw32GO6oJ\r\nContent-Disposition: form-data; name="add_dest"\r\n\r\n1\r\n------WebKitFormBoundaryZZEdj8mvw32GO6oJ--\r\n'
    response = requests.post('https://download.0idea.dev/json/add_package', cookies=cookies, headers=headers, data=data, verify=False)
    return response


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("USE_YOUR_TOKEN_HERE").build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("download", download_command))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == "__main__":
    main()
