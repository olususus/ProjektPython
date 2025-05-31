import time
import os

def calculate_energy_interval(camera_mode, left_closed, right_closed):
    if camera_mode and (left_closed or right_closed):
        if left_closed and right_closed:
            return 1.0
        else:
            return 1.5
    elif camera_mode:
        return 3.0
    elif left_closed and right_closed:
        return 1.5
    elif left_closed or right_closed:
        return 2.0
    return None

def energy_and_refresh_thread(state, chica_ai, bonnie_ai, freddy_ai, foxy_ai):
    import random
    try:
        while not state['game_over']:
            now = time.time()
            # Sprawdzanie czy animatronik jest w drzwiach
            anim_in_door = None
            for anim, ai in [('chica', chica_ai), ('bonnie', bonnie_ai), ('freddy', freddy_ai)]:
                if ai.position == 6:  # 6 = drzwi
                    anim_in_door = anim
                    break
            if anim_in_door and not state.get('door_attack'):
                state['door_attack'] = True
                state['door_attack_anim'] = anim_in_door
                state['door_attack_start'] = now
                state['door_attack_time'] = None
                state['door_locked'] = False
            if state.get('door_attack'):
                if (state['door_attack_anim'] == 'chica' and state['right_closed']) or \
                   (state['door_attack_anim'] == 'bonnie' and state['left_closed']) or \
                   (state['door_attack_anim'] == 'freddy' and state['right_closed']):
                    if now - state['door_attack_start'] <= 1.5:
                        if state['door_attack_anim'] == 'chica':
                            chica_ai.reset()
                        elif state['door_attack_anim'] == 'bonnie':
                            bonnie_ai.reset()
                        elif state['door_attack_anim'] == 'freddy':
                            freddy_ai.reset()
                        state['door_attack'] = False
                        state['door_attack_anim'] = None
                        state['door_attack_start'] = None
                        state['door_attack_time'] = None
                    else:
                        state['door_locked'] = True
                if not state['door_locked'] and now - state['door_attack_start'] > 1.5:
                    state['door_locked'] = True
                    state['door_attack_time'] = now + random.uniform(1, 5)
                if state['door_locked'] and state['door_attack_time'] and now >= state['door_attack_time']:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print(f"Zostałeś zabity przez {state['door_attack_anim'].capitalize()}!")
                    state['game_over'] = True
                    break
            interval = calculate_energy_interval(state['camera_mode'], state['left_closed'], state['right_closed'])
            if interval and now - state['last_energy_tick'] >= interval:
                state['energy'] -= 1
                if state['energy'] < 0:
                    state['energy'] = 0
                state['last_energy_tick'] = now
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"Energia: {state['energy']}%")
            print(f'Noc: {state["night"]}, Godzina: {state["minute"]+1}:00')
            if state.get('door_attack'):
                print(f"UWAGA! {state['door_attack_anim'].capitalize()} jest w drzwiach! Zamknij odpowiednie drzwi w 1.5s!")
                if state.get('door_locked'):
                    print("Drzwi są zablokowane! Czekaj na jumpscare...")
            if state['camera_mode']:
                from fnaf_terminal import show_camera
                show_camera(state['selected_camera'], chica_ai, bonnie_ai, freddy_ai, foxy_ai, state.get('random_event'))
                print("[1-5] Zmień kamerę | [E] Wyjdź z kamery")
            else:
                # Losowy event: lights
                if state.get('random_event') == 'lights':
                    print("[EVENT] Światła migoczą!")
                # Losowy event: door_jam
                if state.get('random_event') == 'door_jam':
                    print("[EVENT] Drzwi się zacinają! Nie możesz ich zamknąć!")
                left_anim = None
                right_anim = None
                if chica_ai.position == 6:
                    right_anim = 'chica'
                if bonnie_ai.position == 6:
                    left_anim = 'bonnie'
                if freddy_ai.position == 6:
                    right_anim = 'freddy'
                from fnaf_terminal import load_room
                print(load_room(state['left_closed'], state['right_closed'], left_anim, right_anim))
                print("[A] Zamknij/otwórz lewe drzwi | [D] Zamknij/otwórz prawe drzwi | [K] Kamery | [Q] Wyjdź")
            if state['energy'] == 0:
                print("\nSkończyła się energia! Gra zakończona.")
                state['game_over'] = True
                break
            time.sleep(state['refresh_interval'])
    except Exception as e:
        print(f"Błąd w wątku energii: {e}")
