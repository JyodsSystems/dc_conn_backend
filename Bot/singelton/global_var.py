stats = {}

def set_stats(key, value):
    stats[key] = value

def get_stats(key):
    return stats[key] if key in stats else None

def get_all_stats():
    return stats

def format_stats():
    # create a message with all stats
    message = ""
    for key in stats:
        message += f"{key}: {stats[key]}\n"

    return message