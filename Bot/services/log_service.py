import datetime
import requests
from enum import Enum


class LogLevel(Enum):
    INFO = {
        'level': 0,
        'name': 'INFO',
        'color': '\033[92m'  # Green
    }
    WARNING = {
        'level': 2,
        'name': 'WARNING',
        'color': '\033[93m'  # Yellow
    }
    ERROR = {
        'level': 3,
        'name': 'ERROR',
        'color': '\033[91m'  # Red
    }
    CRITICAL = {
        'level': 4,
        'name': 'CRITICAL',
        'color': '\033[95m'  # Magenta
    }


def log(level, message):

    discord_webhook = "https://discord.com/api/webhooks/1291532839808139406/odp_LWifXdggCN1JdLcqkqD8cyjutD8_cNohX0Dd6mB3l9uGuEdeS5a1a9RsufqrcCrr"
    
    #Log with color: dd.mm.yyyy hh:mm:ss - Level: Message
    print(f'{level.value["color"]}[QuackBot] [{level.value["name"]}] - {datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")} - {message}\033[0m')

    # db.write_db({
    #     'level': level.value['name'],
    #     'message': message
    # }, db.DBs.logs)

    if level.value['level'] >= LogLevel.ERROR.value['level']:
        requests.post(discord_webhook, json={
            "content": f"[QuackBot] [{level.value['name']}] - {datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')} - {message}"
        })

    return

def safeLog():

    currentDayTime = datetime.datetime.now().strftime(f"%d.%m.%Y %H_%M")

    db.rename_db(db.DBs.logs, "database/logs/" + currentDayTime + '.log')