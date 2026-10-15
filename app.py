import pygame 
import random 
import math 
import time 
 
pygame.init() 
 
# ---------------- CONFIGURATION ---------------- 
WIDTH, HEIGHT = 1100, 700 
FPS = 60 
GAME_DURATION = 60 
 
screen = pygame.display.set_mode((WIDTH, HEIGHT)) 
pygame.display.set_caption("NEURAL AIM - AI Aim Trainer") 
 
clock = pygame.time.Clock() 
 
BG = (10, 15, 32) 
WHITE = (240, 248, 255) 
CYAN = (0, 240, 255) 
PINK = (255, 65, 160) 
GREEN = (70, 255, 150) 
YELLOW = (255, 220, 80) 
MUTED = (120, 145, 175) 
 
font = pygame.font.SysFont("consolas", 22, bold=True) 
big_font = pygame.font.SysFont("consolas", 48, bold=True) 
small_font = pygame.font.SysFont("consolas", 16) 
 
# ---------------- GAME STATE ---------------- 
player_score = 0 
ai_score = 0 
player_shots = 0 
player_hits = 0 
ai_shots = 0 
ai_hits = 0 
 
start_time = time.time() 
game_over = False 
 
ai_x, ai_y = WIDTH // 2, HEIGHT // 2 
ai_target = None 
ai_cooldown = 0 
ai_reaction = 0 
 
targets = [] 
particles = [] 
stars = [ 
    (random.randrange(WIDTH), random.randrange(HEIGHT), 
 random.choice([1, 1, 2])) 
    for _ in range(100) 
] 
 
 
class Target: 
    def __init__(self): 
        self.radius = random.randint(19, 31) 
        self.x = random.randint(60, WIDTH - 60) 
        self.y = random.randint(125, HEIGHT - 60) 
        self.vx = random.choice([-1, 1]) * random.uniform(1.0, 2.5) 
        self.vy = random.choice([-1, 1]) * random.uniform(0.6, 1.8) 
        self.color = random.choice([CYAN, PINK, GREEN, YELLOW]) 
        self.alive = True 
 
    def update(self): 
        self.x += self.vx 
        self.y += self.vy 
 
        if self.x < self.radius or self.x > WIDTH - self.radius: 
            self.vx *= -1 
 
        if self.y < 115 + self.radius or self.y > HEIGHT - self.radius: 
            self.vy *= -1 
 
    def draw(self): 
        if not self.alive: 
            return 
 
        x, y, r = int(self.x), int(self.y), self.radius 
 
        pygame.draw.circle(screen, self.color, (x, y), r + 5, 1) 
        pygame.draw.circle(screen, self.color, (x, y), r, 2) 
        pygame.draw.circle(screen, WHITE, (x, y), r - 8, 2) 
        pygame.draw.circle(screen, self.color, (x, y), 5) 
 
        pygame.draw.line(screen, self.color, 
                         (x - r - 7, y), (x - r + 3, y), 2) 
        pygame.draw.line(screen, self.color, 
                         (x + r - 3, y), (x + r + 7, y), 2) 
        pygame.draw.line(screen, self.color, 
                         (x, y - r - 7), (x, y - r + 3), 2) 
        pygame.draw.line(screen, self.color, 
                         (x, y + r - 3), (x, y + r + 7), 2) 
 
    def contains(self, px, py): 
        return math.hypot(self.x - px, self.y - py) < self.radius 
 
 
def draw_text(text, x, y, color=WHITE, f=font, center=False): 
    image = f.render(str(text), True, color) 
    rect = image.get_rect() 
    if center: 
        rect.center = (x, y) 
    else: 
        rect.topleft = (x, y) 
    screen.blit(image, rect) 
 
 
def make_particles(x, y, color): 
    for _ in range(16): 
        angle = random.uniform(0, math.tau) 
        speed = random.uniform(1, 5) 
        particles.append([ 
            x, y, 
            math.cos(angle) * speed, 
            math.sin(angle) * speed, 
            20, color 
        ]) 
 
 
def draw_background(): 
    screen.fill(BG) 
 
    for x, y, size in stars: 
        pygame.draw.circle(screen, (40, 65, 95), (x, y), size) 
 
    # Arena grid 
    for x in range(0, WIDTH, 50): 
        pygame.draw.line(screen, (17, 29, 51), 
                         (x, 110), (x, HEIGHT), 1) 
 
    for y in range(120, HEIGHT, 50): 
        pygame.draw.line(screen, (17, 29, 51), 
                         (0, y), (WIDTH, y), 1) 
 
    pygame.draw.line(screen, CYAN, (0, 105), (WIDTH, 105), 2) 
 
 
def draw_hud(remaining): 
    draw_text("NEURAL AIM", 25, 20, CYAN, big_font) 
    draw_text("HUMAN", 28, 75, WHITE, small_font) 
    draw_text(f"SCORE  {player_score}", 120, 72, CYAN, font) 
 
    draw_text("AI BOT", 390, 75, WHITE, small_font) 
    draw_text(f"SCORE  {ai_score}", 475, 72, PINK, font) 
 
    draw_text(f"TIME  {max(0, remaining):04.1f}s", 
              820, 22, YELLOW, font) 
 
    player_acc = 100 * player_hits / max(1, player_shots) 
    ai_acc = 100 * ai_hits / max(1, ai_shots) 
 
    draw_text(f"PLAYER ACCURACY: {player_acc:.0f}%", 
              25, HEIGHT - 32, CYAN, small_font) 
    draw_text(f"AI ACCURACY: {ai_acc:.0f}%", 
              WIDTH - 230, HEIGHT - 32, PINK, small_font) 
 
 
def draw_crosshair(x, y, color, size=15): 
    x, y = int(x), int(y) 
    pygame.draw.circle(screen, color, (x, y), size, 1) 
    pygame.draw.line(screen, color, (x - size - 7, y), 
                     (x - 4, y), 2) 
    pygame.draw.line(screen, color, (x + 4, y), 
                     (x + size + 7, y), 2) 
    pygame.draw.line(screen, color, (x, y - size - 7), 
                     (x, y - 4), 2) 
    pygame.draw.line(screen, color, (x, y + 4), 
                     (x, y + size + 7), 2) 
    pygame.draw.circle(screen, color, (x, y), 2) 
 
 
def ai_update(dt): 
    global ai_x, ai_y, ai_target, ai_cooldown 
    global ai_reaction, ai_score, ai_hits, ai_shots 
 
    ai_cooldown = max(0, ai_cooldown - dt) 
    ai_reaction = max(0, ai_reaction - dt) 
 
    alive = [t for t in targets if t.alive] 
 
    if not alive: 
        ai_target = None 
        return 
 
    # Choose a target, then predict its future position. 
    if ai_target not in alive: 
        ai_target = min( 
            alive, 
            key=lambda t: math.hypot(t.x - ai_x, t.y - ai_y) 
        ) 
        ai_reaction = 0.30  # AI reaction delay 
 
    t = ai_target 
 
    aim_x = t.x + t.vx * 9 
    aim_y = t.y + t.vy * 9 
 
    dx = aim_x - ai_x 
    dy = aim_y - ai_y 
    distance = math.hypot(dx, dy) 
 
    # Smooth tracking: the AI crosshair follows the target. 
    if distance > 0: 
        speed = 420 * dt 
        ai_x += dx / distance * min(speed, distance) 
        ai_y += dy / distance * min(speed, distance) 
 
    # AI shoots with imperfect accuracy and a reaction delay. 
    if distance < 20 and ai_cooldown <= 0 and ai_reaction <= 0: 
        ai_shots += 1 
        ai_cooldown = 0.48 
 
        error = random.gauss(0, 13) 
        error_y = random.gauss(0, 13) 
 
        if t.contains(ai_x + error, ai_y + error_y): 
            t.alive = False 
            ai_score += 10 
            ai_hits += 1 
            make_particles(t.x, t.y, PINK) 
 
 
# ---------------- MAIN LOOP ---------------- 
running = True 
 
while running: 
    dt = min(clock.tick(FPS) / 1000, 0.05) 
    elapsed = time.time() - start_time 
    remaining = GAME_DURATION - elapsed 
 
    if remaining <= 0: 
        game_over = True 
 
    for event in pygame.event.get(): 
        if event.type == pygame.QUIT: 
            running = False 
 
        if event.type == pygame.KEYDOWN: 
            if event.key == pygame.K_ESCAPE: 
                running = False 
 
            if event.key == pygame.K_r and game_over: 
                player_score = ai_score = 0 
                player_shots = player_hits = 0 
                ai_shots = ai_hits = 0 
                targets.clear() 
                particles.clear() 
                start_time = time.time() 
                game_over = False 
                ai_target = None 
                ai_cooldown = 0 
                ai_reaction = 0 
 
        if (event.type == pygame.MOUSEBUTTONDOWN 
                and event.button == 1 and not game_over): 
            player_shots += 1 
            mx, my = event.pos 
 
            for target in reversed(targets): 
                if target.alive and target.contains(mx, my): 
                    target.alive = False 
                    player_score += 10 
                    player_hits += 1 
                    make_particles(target.x, target.y, target.color) 
                    break 
 
    draw_background() 
 
    if not game_over: 
        # Keep several targets on screen. 
        alive_count = sum(t.alive for t in targets) 
        if alive_count < 6: 
            targets.append(Target()) 
 
        for target in targets: 
            target.update() 
            target.draw() 
 
        ai_update(dt) 
 
        # Show the AI's tracking crosshair and aim line. 
        if ai_target and ai_target.alive: 
            pygame.draw.line( 
                screen, (110, 35, 80), 
                (int(ai_x), int(ai_y)), 
                (int(ai_target.x), int(ai_target.y)), 1 
            ) 
 
        draw_crosshair(ai_x, ai_y, PINK, 12) 
 
        # Player crosshair 
        mx, my = pygame.mouse.get_pos() 
        draw_crosshair(mx, my, CYAN, 15) 
 
    # Hit particles 
    for p in particles[:]: 
        p[0] += p[2] 
        p[1] += p[3] 
        p[4] -= 1 
 
        if p[4] <= 0: 
            particles.remove(p) 
        else: 
            pygame.draw.circle( 
                screen, p[5], 
                (int(p[0]), int(p[1])), 
                max(1, p[4] // 5) 
            ) 
 
    targets = [t for t in targets if t.alive or game_over is False] 
 
    draw_hud(remaining) 
 
    if game_over: 
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA) 
        overlay.fill((4, 8, 20, 210)) 
        screen.blit(overlay, (0, 0)) 
 
        draw_text("SESSION COMPLETE", WIDTH // 2, 210, 
                  CYAN, big_font, center=True) 
 
        draw_text(f"PLAYER SCORE: {player_score}", 
                  WIDTH // 2, 300, CYAN, font, center=True) 
        draw_text(f"AI SCORE: {ai_score}", 
                  WIDTH // 2, 345, PINK, font, center=True) 
 
        if player_score > ai_score: 
            result = "HUMAN WINS!" 
            color = GREEN 
        elif ai_score > player_score: 
            result = "AI WINS!" 
            color = PINK 
        else: 
            result = "DRAW!" 
            color = YELLOW 
 
        draw_text(result, WIDTH // 2, 410, 
                  color, big_font, center=True) 
        draw_text("PRESS R TO PLAY AGAIN  |  ESC TO EXIT", 
                  WIDTH // 2, 485, WHITE, small_font, center=True) 
 
    pygame.display.flip() 
 
pygame.quit() 
