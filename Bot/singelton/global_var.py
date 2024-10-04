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
    # Calculate the median of all duration statistics
    durations = []

    # Collect all duration values
    for key in stats:
        if "duration_" in key:
            durations.append(stats[key])

    # Sort the durations to calculate the median
    durations.sort()

    # Calculate median
    if len(durations) % 2 != 0:
        median = durations[len(durations) // 2]  # Odd number of elements
    else:
        mid_index = len(durations) // 2
        median = (durations[mid_index] + durations[mid_index - 1]) / 2  # Even number of elements

    # Function to format the duration in seconds and milliseconds
    format_with_milliseconds = lambda x: f"{x // 1000}s {x % 1000}ms"
    
    # Set the formatted median duration in stats
    set_stats("median_duration", format_with_milliseconds(median))
