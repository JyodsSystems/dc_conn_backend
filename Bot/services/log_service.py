import datetime
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
    
    #Log with color: dd.mm.yyyy hh:mm:ss - Level: Message
    print(f'{level.value["color"]}[QuackBot] [{level.value["name"]}] - {datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")} - {message}\033[0m')

    # db.write_db({
    #     'level': level.value['name'],
    #     'message': message
    # }, db.DBs.logs)

    return

def safeLog():

    currentDayTime = datetime.datetime.now().strftime(f"%d.%m.%Y %H_%M")

    db.rename_db(db.DBs.logs, "database/logs/" + currentDayTime + '.log')