import pygame
import random

pygame.init()

WIDTH, HEIGHT = 1200, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Blackjack - Hidden AI Personalities")

font = pygame.font.SysFont("arial", 20)
big_font = pygame.font.SysFont("arial", 28)

# =========================
# CARDS
# =========================

suits = ["♠", "♥", "♦", "♣"]
ranks = [
    ("2", 2), ("3", 3), ("4", 4), ("5", 5), ("6", 6),
    ("7", 7), ("8", 8), ("9", 9), ("10", 10),
    ("J", 10), ("Q", 10), ("K", 10), ("A", 11)
]

def create_deck():
    deck = [(r, v, s) for s in suits for r, v in ranks]
    random.shuffle(deck)
    return deck

def hand_value(hand):
    value = sum(c[1] for c in hand)
    aces = sum(1 for c in hand if c[0] == "A")

    while value > 21 and aces:
        value -= 10
        aces -= 1

    return value

# =========================
# HIDDEN AI SYSTEM
# =========================

AI_STYLES = ["safe", "normal", "aggressive"]

class AIPlayer:
    def __init__(self, name):
        self.name = name
        self.style = random.choice(AI_STYLES)  # 🔥 hidden
        self.hand = []

    def reset(self):
        self.hand = []

    def should_hit(self):
        v = hand_value(self.hand)

        # 🟢 SAFE
        if self.style == "safe":
            return v < 15

        # 🔵 NORMAL
        if self.style == "normal":
            return v < 17

        # 🔴 AGGRESSIVE (smarter, less reckless)
        if self.style == "aggressive":
            if v < 16:
                return True
            if v < 19:
                return random.random() < 0.35  # controlled risk
            return False

        return v < 16

# =========================
# BUTTON SYSTEM
# =========================

class Button:
    def __init__(self, x, y, w, h, text, action):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action = action

    def draw(self):
        pygame.draw.rect(screen, (230, 230, 230), self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)

        txt = font.render(self.text, True, (0, 0, 0))
        screen.blit(txt, (self.rect.x + 10, self.rect.y + 10))

    def click(self, pos):
        if self.rect.collidepoint(pos):
            self.action()

# =========================
# PLAYER
# =========================

class Player:
    def __init__(self):
        self.hand = []
        self.money = 100
        self.bet = 10

    def reset(self):
        self.hand = []

# =========================
# GAME STATES
# =========================

BETTING = "betting"
PLAYING = "playing"
END = "end"

class Game:
    def __init__(self):
        self.deck = create_deck()

        self.player = Player()
        self.ais = [AIPlayer(f"AI-{i+1}") for i in range(3)]
        self.dealer = Player()

        self.state = BETTING
        self.reveal = False
        self.bet_input = 10
        self.message = "Set bet"

        self.buttons = []
        self.create_buttons()

        self.new_round()

    # =========================
    # UI LAYOUT
    # =========================

    def create_buttons(self):
        x = 920

        self.buttons = [
            Button(x, 150, 220, 45, "Hit", self.hit),
            Button(x, 210, 220, 45, "Stand", self.stand),
            Button(x, 270, 220, 45, "Next Round", self.next_round),

            Button(x, 380, 105, 45, "+10", self.bet_plus),
            Button(x + 115, 380, 105, 45, "-10", self.bet_minus),
            Button(x, 440, 220, 45, "Confirm Bet", self.confirm_bet),
        ]

    # =========================
    # ROUND SETUP
    # =========================

    def new_round(self):
        self.deck = create_deck()

        self.player.reset()
        self.dealer.reset()

        for ai in self.ais:
            ai.reset()

        for _ in range(2):
            self.player.hand.append(self.deck.pop())
            self.dealer.hand.append(self.deck.pop())
            for ai in self.ais:
                ai.hand.append(self.deck.pop())

        self.state = BETTING
        self.reveal = False
        self.message = "Adjust bet"

    # =========================
    # BETTING
    # =========================

    def bet_plus(self):
        if self.state == BETTING:
            self.bet_input += 10

    def bet_minus(self):
        if self.state == BETTING:
            self.bet_input = max(10, self.bet_input - 10)

    def confirm_bet(self):
        if self.state == BETTING:
            self.player.bet = self.bet_input
            self.state = PLAYING
            self.message = "Hit or Stand"

    # =========================
    # PLAYER ACTIONS
    # =========================

    def hit(self):
        if self.state == PLAYING:
            self.player.hand.append(self.deck.pop())
            if hand_value(self.player.hand) > 21:
                self.ai_turns()

    def stand(self):
        if self.state == PLAYING:
            self.ai_turns()

    def next_round(self):
        if self.state == END:
            self.new_round()

    # =========================
    # AI TURN (HIDDEN PERSONALITY)
    # =========================

    def ai_turns(self):
        for ai in self.ais:
            while ai.should_hit():
                ai.hand.append(self.deck.pop())

        self.dealer_turn()

    def dealer_turn(self):
        while hand_value(self.dealer.hand) < 17:
            self.dealer.hand.append(self.deck.pop())

        self.resolve()

    # =========================
    def resolve(self):
        self.reveal = True

        pv = hand_value(self.player.hand)
        dv = hand_value(self.dealer.hand)

        if pv > 21:
            self.player.money -= self.player.bet
            self.message = "Bust"
        elif dv > 21 or pv > dv:
            self.player.money += self.player.bet
            self.message = "Win"
        elif pv < dv:
            self.player.money -= self.player.bet
            self.message = "Lose"
        else:
            self.message = "Push"

        self.state = END

    # =========================
    # INPUT
    # =========================

    def click(self, pos):
        for b in self.buttons:
            b.click(pos)

    # =========================
    # DRAWING
    # =========================

    def draw_card(self, x, y, card):
        r, v, s = card
        rect = pygame.Rect(x, y, 60, 90)

        pygame.draw.rect(screen, (255, 255, 255), rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, 2)

        screen.blit(font.render(f"{r}{s}", True, (0, 0, 0)), (x + 10, y + 30))

    def draw_hidden_card(self, x, y):
        rect = pygame.Rect(x, y, 60, 90)
        pygame.draw.rect(screen, (40, 40, 140), rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, 2)

    def draw_hand(self, hand, x, y, label, hidden=False):
        screen.blit(font.render(label, True, (255, 255, 255)), (x, y - 25))

        for i, c in enumerate(hand):
            if hidden:
                self.draw_hidden_card(x + i * 70, y)
            else:
                self.draw_card(x + i * 70, y, c)

    # =========================
    def draw(self):
        screen.fill((20, 120, 20))

        self.draw_hand(self.dealer.hand, 350, 50, "Dealer", not self.reveal)

        for i, ai in enumerate(self.ais):
            self.draw_hand(ai.hand, 50, 180 + i * 120, f"AI-{i+1}", not self.reveal)

        self.draw_hand(self.player.hand, 350, 520, "YOU")

        pygame.draw.rect(screen, (30, 30, 30), (900, 0, 300, HEIGHT))

        screen.blit(big_font.render(f"Money: ${self.player.money}", True, (255, 255, 255)), (920, 30))
        screen.blit(big_font.render(f"Bet: ${self.bet_input}", True, (255, 255, 255)), (920, 70))
        screen.blit(big_font.render(self.message, True, (255, 255, 0)), (350, 650))

        for b in self.buttons:
            b.draw()

# =========================
# RUN
# =========================

game = Game()
clock = pygame.time.Clock()

running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            game.click(event.pos)

    game.draw()
    pygame.display.flip()

pygame.quit()