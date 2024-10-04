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

def set_median():
    # calculate the median of all stats duration_*
    durations = []
    for key in stats:
        if "duration_" in key:
            durations.append(stats[key])

    durations.sort()
    median = durations[len(durations) // 2] if len(durations) % 2 != 0 else (durations[len(durations) // 2] + durations[len(durations) // 2 - 1]) / 2

    format_with_miliseconds = lambda x: f"{x // 1000}s {x % 1000}ms"
    set_stats("median_duration", format_with_miliseconds(median))
