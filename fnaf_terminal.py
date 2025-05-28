import os
import sys
import time
import threading
import random
import msvcrt
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from src.rooms_ascii import ROOMS
from src.cameras_ascii import CAMERAS
from src.animatronic_ai import AnimatronicAI
from src.energy_system import calculate_energy_interval
from src.energy_system import energy_and_refresh_thread
from src.stats import update_stats, print_stats

def load_room(left_closed, right_closed, left_anim=None, right_anim=None):
    # (czemu to nie dziala: jeśli nie ma pliku w ROOMS, zwróci KeyError)
    if left_anim == 'freddy':
        return ROOMS['left_freddy']
    elif left_anim == 'chica':
        return ROOMS['left_chica']
    elif right_anim == 'bonnie':
        return ROOMS['right_bonnie']
    elif right_anim == 'chica':
        return ROOMS['right_chica']
    elif left_closed and right_closed:
        return ROOMS['both_closed']
    elif left_closed:
        return ROOMS['left_closed']
    elif right_closed:
        return ROOMS['right_closed']
    else:
        return ROOMS['both_open']

def show_camera(selected_camera, chica_ai=None, bonnie_ai=None, freddy_ai=None, foxy_ai=None, random_event=None):
    # Losowy event: glitch
    if random_event == 'glitch':
        print("[GLITCH] Obraz kamery zakłócony!")
        print("#@!$%&*#@!$%&*#@!$%&*")
        print("#@!$%&*#@!$%&*#@!$%&*")
        print("#@!$%&*#@!$%&*#@!$%&*")
        print("#@!$%&*#@!$%&*#@!$%&*")
        print("#@!$%&*#@!$%&*#@!$%&*")
        print("Na tej kamerze nic nie widać!")
        return
    anims = []
    if chica_ai and chica_ai.position >= 0 and chica_ai.position <= 4 and chica_ai.camera_path[chica_ai.position] == selected_camera:
        anims.append('Chica')
    if bonnie_ai and bonnie_ai.position >= 0 and bonnie_ai.position <= 4 and bonnie_ai.camera_path[bonnie_ai.position] == selected_camera:
        anims.append('Bonnie')
    if freddy_ai and freddy_ai.position >= 0 and freddy_ai.position <= 4 and freddy_ai.camera_path[freddy_ai.position] == selected_camera:
        anims.append('Freddy')
    if foxy_ai and foxy_ai.position >= 0 and foxy_ai.position <= 4 and foxy_ai.camera_path[foxy_ai.position] == selected_camera:
        anims.append('Foxy')
    anim = None
    if anims:
        if 'Chica' in anims:
            anim = 'chica'
        elif 'Bonnie' in anims:
            anim = 'bonnie'
        elif 'Freddy' in anims:
            anim = 'freddy'
        elif 'Foxy' in anims:
            anim = 'foxy'
    key = f"{selected_camera}_empty"
    if anim:
        key = f"{selected_camera}_{anim}"
    print(CAMERAS.get(key, CAMERAS[f"{selected_camera}_empty"]))
    if anims:
        print("Na tej kamerze: " + ", ".join(anims))
    else:
        print("Na tej kamerze nikogo nie ma.")

def main_menu():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("""
+-----------------------------+
|      FIVE NIGHTS AT PYTHON  |
+-----------------------------+
|  [G] Graj                   |
|  [Q] Wyjdź                  |
+-----------------------------+
""")
        choice = input('> ').strip().lower()
        if choice == 'g':
            return True
        elif choice == 'q':
            return False

def select_ai_levels():
    ai_levels = {}
    anims = ['Freddy', 'Bonnie', 'Chica']
    for anim in anims:
        while True:
            try:
                level = int(input(f"Ustaw poziom AI dla {anim} (1-20): "))
                if 1 <= level <= 20:
                    ai_levels[anim] = level
                    break
                else:
                    print("Podaj liczbę z zakresu 1-20.")
            except ValueError:
                print("Podaj liczbę całkowitą.")
    return ai_levels

def main():
    if not main_menu():
        return
    ai_levels = select_ai_levels()
    chica_ai = AnimatronicAI('chica', ai_levels['Chica'], 15, 20, [5,4,3,2,1,'door'])
    bonnie_ai = AnimatronicAI('bonnie', ai_levels['Bonnie'], 20, 20, [5,4,3,2,1,'door'])
    freddy_ai = AnimatronicAI('freddy', ai_levels['Freddy'], 17, 40, [5,4,3,2,1,'door'])
    foxys_path = [5, 4, 3, 2, 1, 'door']
    foxy_ai = AnimatronicAI('foxy', ai_levels.get('Foxy', 10), 10, 20, foxys_path)
    chica_ai.start_timer()
    bonnie_ai.start_timer()
    freddy_ai.start_timer()
    foxy_ai.start_timer()
    try:
        state = {
            'left_closed': False,
            'right_closed': False,
            'camera_mode': False,
            'selected_camera': 1,
            'energy': 100,
            'last_energy_tick': time.time(),
            'refresh_interval': 0.2,
            'game_over': False,
            'night': 1,
            'minute': 0,
            'foxy_event': False,
            'foxy_attack_timer': 0,
            'random_event': None,
            'random_event_timer': 0
        }
        t = threading.Thread(target=energy_and_refresh_thread, args=(state, chica_ai, bonnie_ai, freddy_ai, foxy_ai), daemon=True)
        t.start()
        last_minute = time.time()
        while not state['game_over']:
            # System nocy: 1 minuta IRL = 1 godzina w grze
            now = time.time()
            # Losowe eventy co 30-90 sekund
            if not state['random_event'] and random.random() < 0.01:
                event = random.choice(['glitch', 'lights', 'door_jam'])
                state['random_event'] = event
                state['random_event_timer'] = now + random.randint(5, 15)
            if state['random_event'] and now >= state['random_event_timer']:
                state['random_event'] = None
            # Foxy atakuje jeśli długo nie patrzysz na kamery
            if foxy_ai.position == 6 and not state.get('foxy_event'):
                state['foxy_event'] = True
                state['foxy_attack_timer'] = now + random.uniform(1, 3)
            if state.get('foxy_event') and now >= state['foxy_attack_timer']:
                print("Foxy wbiegł do biura! Zginąłeś!")
                state['game_over'] = True
                break
            if now - last_minute >= 60:
                state['minute'] += 1
                last_minute = now
                if state['minute'] >= 6:
                    state['night'] += 1
                    state['minute'] = 0
                    print(f"\nPrzetrwałeś noc {state['night']-1}! Gratulacje!")
                    update_stats(state['night']-1, True)
                    print_stats()
                    input("Naciśnij Enter, aby kontynuować...")
            if msvcrt.kbhit():
                key = msvcrt.getwch().lower()
                if state['camera_mode']:
                    if key in ['1','2','3','4','5']:
                        state['selected_camera'] = int(key)
                    elif key == 'e':
                        state['camera_mode'] = False
                else:
                    if key == 'a':
                        state['left_closed'] = not state['left_closed']
                    elif key == 'd':
                        state['right_closed'] = not state['right_closed']
                    elif key == 'k':
                        state['camera_mode'] = True
                    elif key == 'q':
                        state['game_over'] = True
                        break
            time.sleep(0.05)
        t.join()
        update_stats(state['night'], False)
        print_stats()
    finally:
        chica_ai.stop()
        bonnie_ai.stop()
        freddy_ai.stop()
        foxy_ai.stop()

if __name__ == "__main__":
    main()
