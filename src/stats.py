# src/stats.py
import json
import os

STATS_FILE = os.path.join(os.path.dirname(__file__), '../stats.json')

def load_stats():
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"nights_survived": 0, "deaths": 0, "max_night": 0}

def save_stats(stats):
    with open(STATS_FILE, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)

def update_stats(night, survived):
    stats = load_stats()
    if survived:
        stats["nights_survived"] += 1
        if night > stats["max_night"]:
            stats["max_night"] = night
    else:
        stats["deaths"] += 1
    save_stats(stats)

def print_stats():
    stats = load_stats()
    print("\n=== STATYSTYKI ===")
    print(f"Nocy przetrwanych: {stats['nights_survived']}")
    print(f"Zgony: {stats['deaths']}")
    print(f"Najdłuższa noc: {stats['max_night']}")
    print("==================\n")
