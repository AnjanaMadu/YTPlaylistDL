import logging
logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

import pyrogram, os

if __name__ == "__main__" :
    plugins = dict(
        root="plugins"
    )
    app = pyrogram.Client(
        "bot",
        bot_token=os.environ.get("TOKEN"),
        api_id=int(os.environ.get("APP_ID")),
        api_hash=os.environ.get("API_HASH"),
        plugins=plugins
    )
    app.run()
