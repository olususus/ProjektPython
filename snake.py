import os
import sys
import time
import random
from collections import deque

try:
    import msvcrt
    WINDOWS = True
except ImportError:
    import termios, tty
    WINDOWS = False

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

class PowerUp:
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.type = power_type
        self.duration = 50
        self.symbol = {'speed': '*', 'shrink': 'X', 'score': '$', 'wall': '#'}[power_type]
        self.color = {'speed': Colors.YELLOW, 'shrink': Colors.RED, 'score': Colors.CYAN, 'wall': Colors.MAGENTA}[power_type]

class Snake:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.body = deque([(width//2, height//2)])
        self.direction = (1, 0)
        self.grow = False
        self.speed_boost = 0
        self.wall_phase = 0
        
    def move(self):
        head_x, head_y = self.body[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)
        
        if self.wall_phase > 0:
            new_head = (new_head[0] % self.width, new_head[1] % self.height)
            self.wall_phase -= 1
        
        self.body.appendleft(new_head)
        
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False
            
        if self.speed_boost > 0:
            self.speed_boost -= 1
    
    def change_direction(self, direction):
        dx, dy = direction
        current_dx, current_dy = self.direction
        if (dx, dy) != (-current_dx, -current_dy):
            self.direction = direction
    
    def check_collision(self):
        head = self.body[0]
        if self.wall_phase > 0:
            return False
        if head[0] < 0 or head[0] >= self.width or head[1] < 0 or head[1] >= self.height:
            return True
        if head in list(self.body)[1:]:
            return True
        return False
    
    def shrink(self):
        if len(self.body) > 3:
            for _ in range(min(3, len(self.body) - 1)):
                self.body.pop()

class SnakeGame:
    def __init__(self, width=40, height=20):
        self.width = width
        self.height = height
        self.snake = Snake(width, height)
        self.food = self.generate_food()
        self.powerups = []
        self.score = 0
        self.level = 1
        self.high_score = self.load_high_score()
        self.game_over = False
        self.paused = False
        self.key_pressed = None
        
    def generate_food(self):
        while True:
            x, y = random.randint(0, self.width-1), random.randint(0, self.height-1)
            if (x, y) not in self.snake.body:
                return (x, y)
    
    def generate_powerup(self):
        if random.random() < 0.05 and len(self.powerups) < 1:
            while True:
                x, y = random.randint(0, self.width-1), random.randint(0, self.height-1)
                if (x, y) not in self.snake.body and (x, y) != self.food:
                    power_type = random.choice(['speed', 'shrink', 'score', 'wall'])
                    self.powerups.append(PowerUp(x, y, power_type))
                    break
    
    def load_high_score(self):
        try:
            with open('.snake_highscore', 'r') as f:
                return int(f.read().strip())
        except:
            return 0
    
    def save_high_score(self):
        if self.score > self.high_score:
            with open('.snake_highscore', 'w') as f:
                f.write(str(self.score))
            self.high_score = self.score
    
    def update(self):
        if self.paused:
            return
        
        self.snake.move()
        
        if self.snake.check_collision():
            self.game_over = True
            self.save_high_score()
            return
        
        head = self.snake.body[0]
        
        if head == self.food:
            self.snake.grow = True
            points = 10 * self.level
            self.score += points
            self.food = self.generate_food()
            
            if self.score // 150 > (self.score - points) // 150:
                self.level += 1
        
        for powerup in self.powerups[:]:
            if head == (powerup.x, powerup.y):
                self.powerups.remove(powerup)
                
                if powerup.type == 'speed':
                    self.snake.speed_boost = 25
                elif powerup.type == 'shrink':
                    self.snake.shrink()
                elif powerup.type == 'score':
                    self.score += 75
                elif powerup.type == 'wall':
                    self.snake.wall_phase = 40
        
        self.generate_powerup()
        
        self.powerups = [p for p in self.powerups if p.duration > 0]
        for p in self.powerups:
            p.duration -= 1
    
    def draw(self):
        if WINDOWS:
            os.system('cls')
        else:
            os.system('clear')
        
        grid = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        
        for i, (x, y) in enumerate(self.snake.body):
            if 0 <= x < self.width and 0 <= y < self.height:
                if i == 0:
                    head_chars = {(1,0): '>', (-1,0): '<', (0,1): 'v', (0,-1): '^'}
                    head_char = head_chars.get(self.snake.direction, 'O')
                    color = Colors.GREEN + Colors.BOLD
                    if self.snake.wall_phase > 0:
                        color = Colors.MAGENTA + Colors.BOLD
                    if self.snake.speed_boost > 0:
                        color = Colors.YELLOW + Colors.BOLD
                    grid[y][x] = color + head_char + Colors.RESET
                else:
                    grid[y][x] = Colors.GREEN + 'O' + Colors.RESET
        
        fx, fy = self.food
        food_char = ['@', 'O', '*', '%'][self.level % 4]
        grid[fy][fx] = Colors.RED + Colors.BOLD + food_char + Colors.RESET
        
        for powerup in self.powerups:
            if 0 <= powerup.x < self.width and 0 <= powerup.y < self.height:
                blink = (time.time() * 4) % 2 < 1
                if blink:
                    grid[powerup.y][powerup.x] = powerup.color + Colors.BOLD + powerup.symbol + Colors.RESET
        
        border_h = '+' + '-' * self.width + '+'
        
        print(border_h)
        for row in grid:
            print('|' + ''.join(row) + '|')
        print(border_h)
        
        status_parts = [
            f"Score: {Colors.YELLOW}{self.score}{Colors.RESET}",
            f"Level: {Colors.CYAN}{self.level}{Colors.RESET}",
            f"Length: {Colors.GREEN}{len(self.snake.body)}{Colors.RESET}",
            f"High: {Colors.MAGENTA}{self.high_score}{Colors.RESET}"
        ]
        
        effects = []
        if self.snake.speed_boost > 0:
            effects.append(f"{Colors.YELLOW}SPEED({self.snake.speed_boost}){Colors.RESET}")
        if self.snake.wall_phase > 0:
            effects.append(f"{Colors.MAGENTA}PHASE({self.snake.wall_phase}){Colors.RESET}")
        if self.paused:
            effects.append(f"{Colors.CYAN}PAUSED{Colors.RESET}")
            
        print(' | '.join(status_parts + effects))
        
        if self.powerups:
            print(f"{Colors.CYAN}Active power-ups: {len(self.powerups)}{Colors.RESET}")
        
        print(f"\n{Colors.CYAN}Strzałki/WASD: Ruch | P: Pauza | Q: Wyjście{Colors.RESET}")
    
    def draw_game_over(self):
        if WINDOWS:
            os.system('cls')
        else:
            os.system('clear')
            
        print(f"\n{Colors.RED}{Colors.BOLD}")
        print("  +" + "="*35 + "+")
        print("  |            GAME OVER!            |")
        print("  +" + "="*35 + "+")
        print(f"{Colors.RESET}")
        
        stats = [
            f"Final Score: {Colors.YELLOW}{self.score}{Colors.RESET}",
            f"Level Reached: {Colors.CYAN}{self.level}{Colors.RESET}",
            f"Snake Length: {Colors.GREEN}{len(self.snake.body)}{Colors.RESET}"
        ]
        
        for stat in stats:
            print(f"  {stat}")
        
        if self.score >= self.high_score:
            print(f"  {Colors.MAGENTA}{Colors.BOLD}*** NEW HIGH SCORE! ***{Colors.RESET}")
        else:
            print(f"  High Score: {Colors.MAGENTA}{self.high_score}{Colors.RESET}")
        
        print(f"\n  {Colors.CYAN}Press R to restart or Q to quit{Colors.RESET}")

def get_key():
    if WINDOWS:
        if msvcrt.kbhit():
            key = msvcrt.getch().decode('utf-8').lower()
            if key == '\xe0':
                key = msvcrt.getch().decode('utf-8')
                arrow_keys = {'H': 'w', 'P': 's', 'K': 'a', 'M': 'd'}
                return arrow_keys.get(key, '')
            return key
        return None
    else:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            key = sys.stdin.read(1)
            if key == '\x1b':
                key += sys.stdin.read(2)
                arrow_keys = {'\x1b[A': 'w', '\x1b[B': 's', '\x1b[D': 'a', '\x1b[C': 'd'}
                return arrow_keys.get(key, '')
            return key.lower()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def main():
    try:
        game = SnakeGame()
        
        while not game.game_over:
            key = get_key()
            if key:
                game.key_pressed = key
            
            if game.key_pressed:
                key = game.key_pressed
                game.key_pressed = None
                
                if key == 'q':
                    game.game_over = True
                    break
                elif key == 'p':
                    game.paused = not game.paused
                elif key == 'w' or key == '\x1b[A':
                    game.snake.change_direction((0, -1))
                elif key == 's' or key == '\x1b[B':
                    game.snake.change_direction((0, 1))
                elif key == 'a' or key == '\x1b[D':
                    game.snake.change_direction((-1, 0))
                elif key == 'd' or key == '\x1b[C':
                    game.snake.change_direction((1, 0))
            
            game.draw()
            game.update()
            
            speed = 0.06 if game.snake.speed_boost > 0 else max(0.04, 0.12 - game.level * 0.008)
            time.sleep(speed)
        
        while True:
            game.draw_game_over()
            
            if WINDOWS:
                while True:
                    key = get_key()
                    if key:
                        break
                    time.sleep(0.05)
            else:
                key = get_key()
            
            if key == 'r':
                game = SnakeGame()
                break
            elif key == 'q':
                break
        
        if WINDOWS:
            os.system('cls')
        else:
            os.system('clear')
        print(f"{Colors.CYAN}Thanks for playing Snake! {Colors.GREEN}>{Colors.RESET}")
        
    except KeyboardInterrupt:
        if WINDOWS:
            os.system('cls')
        else:
            os.system('clear')
        print(f"{Colors.CYAN}Game interrupted. Bye! {Colors.RESET}")

if __name__ == "__main__":
    main()