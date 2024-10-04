import numpy as np

stats = {}

def add_stat(self, name, value):
    """Fügt eine Statistik hinzu oder aktualisiert den Wert."""
    stats[name] = value

def get_stats(self):
    """Gibt die Statistiken als formatierten String zurück."""
    output = []
    for name, value in self.stats.items():
        output.append(f"{name}: {value} ms")
    return "\n".join(output)

@staticmethod
def convert_to_milliseconds(time_value, unit):
    """Konvertiert verschiedene Zeitwerte in Millisekunden."""
    conversions = {
        'seconds': time_value * 1000,
        'minutes': time_value * 1000 * 60,
        'hours': time_value * 1000 * 60 * 60,
        'duration_median': time_value,  # wird angenommen, dass dieser bereits in ms vorliegt
    }

    if unit not in conversions:
        raise ValueError(f"Ungültige Zeiteinheit: {unit}. Erlaubte Einheiten: {', '.join(conversions.keys())}")

    return conversions[unit]

def calculate_median_duration():
        """Berechnet den Median der Statistiken, die mit 'duration_' beginnen."""
        duration_values = [value for name, value in stats.items() if name.startswith('duration_')]
        if duration_values:
            median_value = np.median(duration_values)
            add_stat('duration_median', median_value)