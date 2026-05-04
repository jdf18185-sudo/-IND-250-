import pygame
import sys
import random
import time
import math

pygame.init()

# ── Constants ──────────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 1280, 780
FPS = 60

# Colors
C_FELT       = (22,  101,  52)   # dark green felt
C_FELT_LIGHT = (34,  120,  68)
C_GOLD       = (212, 175,  55)
C_WHITE      = (255, 255, 255)
C_BLACK      = (  0,   0,   0)
C_RED        = (200,  30,  30)
C_DARK_RED   = (139,   0,   0)
C_GRAY       = (160, 160, 160)
C_DARK_GRAY  = ( 60,  60,  60)
C_PANEL      = ( 10,  60,  30)
C_BTN        = ( 15,  80,  45)
C_BTN_HOV    = ( 25, 120,  65)
C_BTN_DIS    = ( 50,  70,  55)
C_YELLOW     = (255, 215,   0)
C_TILT_RED   = (220,  50,  50)
C_BLUE_TINT  = ( 50, 100, 180)

SUITS   = ['♠', '♥', '♦', '♣']
RANKS   = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
RED_SUITS = {'♥', '♦'}

FONT_PATH = None  # use pygame default

def make_font(size, bold=False):
    return pygame.font.SysFont("segoeui", size, bold=bold)

# Fonts
F_HUGE   = make_font(64, bold=True)
F_BIG    = make_font(36, bold=True)
F_MED    = make_font(24, bold=True)
F_SMALL  = make_font(18)
F_TINY   = make_font(14)
F_RANK   = make_font(28, bold=True)
F_SUIT   = make_font(22)

# ── Card Drawing ───────────────────────────────────────────────────────────────
CARD_W, CARD_H = 72, 100

def draw_card(surf, x, y, rank=None, suit=None, face_down=False, small=False):
    w, h = (50, 70) if small else (CARD_W, CARD_H)
    rect = pygame.Rect(x, y, w, h)

    # Shadow
    shadow = pygame.Rect(x+4, y+4, w, h)
    pygame.draw.rect(surf, (0, 0, 0, 80), shadow, border_radius=8)

    if face_down:
        pygame.draw.rect(surf, (30, 30, 120), rect, border_radius=8)
        pygame.draw.rect(surf, C_GOLD, rect, 2, border_radius=8)
        # pattern
        inner = rect.inflate(-8, -8)
        pygame.draw.rect(surf, (50, 50, 160), inner, border_radius=4)
        for i in range(0, inner.width, 8):
            pygame.draw.line(surf, (70, 70, 180), (inner.x+i, inner.y), (inner.x+i, inner.bottom), 1)
    else:
        pygame.draw.rect(surf, C_WHITE, rect, border_radius=8)
        pygame.draw.rect(surf, C_DARK_GRAY, rect, 2, border_radius=8)
        color = C_RED if suit in RED_SUITS else C_BLACK
        fnt_r = make_font(20 if small else 26, bold=True)
        fnt_s = make_font(16 if small else 20)
        r_surf = fnt_r.render(rank, True, color)
        s_surf = fnt_s.render(suit, True, color)
        surf.blit(r_surf, (x+4, y+2))
        surf.blit(s_surf, (x+4, y+2+r_surf.get_height()))
        # center suit
        cs = make_font(28 if small else 36)
        c_surf = cs.render(suit, True, color)
        surf.blit(c_surf, (x + w//2 - c_surf.get_width()//2, y + h//2 - c_surf.get_height()//2))

# ── Deck / Hand helpers ────────────────────────────────────────────────────────
def new_deck():
    deck = [(r, s) for s in SUITS for r in RANKS]
    random.shuffle(deck)
    return deck

def card_value(rank):
    if rank in ('J','Q','K'): return 10
    if rank == 'A': return 11
    return int(rank)

def hand_total(hand):
    total = 0
    aces = 0
    for r, s in hand:
        v = card_value(r)
        if v == 11: aces += 1
        total += v
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total

def is_bust(hand): return hand_total(hand) > 21
def is_blackjack(hand): return len(hand) == 2 and hand_total(hand) == 21

# ── Button ─────────────────────────────────────────────────────────────────────
class Button:
    def __init__(self, x, y, w, h, label, color=C_BTN, hover=C_BTN_HOV, disabled_color=C_BTN_DIS):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.color = color
        self.hover = hover
        self.disabled_color = disabled_color
        self.enabled = True

    def draw(self, surf):
        mx, my = pygame.mouse.get_pos()
        hov = self.rect.collidepoint(mx, my) and self.enabled
        c = self.hover if hov else (self.color if self.enabled else self.disabled_color)
        pygame.draw.rect(surf, c, self.rect, border_radius=10)
        pygame.draw.rect(surf, C_GOLD, self.rect, 2, border_radius=10)
        txt = F_MED.render(self.label, True, C_WHITE if self.enabled else C_GRAY)
        surf.blit(txt, txt.get_rect(center=self.rect.center))

    def clicked(self, event):
        return (self.enabled and event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1 and self.rect.collidepoint(event.pos))

# ── AI Player ──────────────────────────────────────────────────────────────────
PERSONALITIES = ['Safe', 'Normal', 'Aggressive']

class AIPlayer:
    def __init__(self, name, money=1000):
        self.name   = name
        self.money  = money
        self.hand   = []
        self.bet    = 50
        self.stood  = False
        self.bust   = False
        self.done   = False
        self.eliminated = False

        # Psychology
        self.personality = random.choice(PERSONALITIES)
        self.tilt        = 0.0      # 0-1
        self.history     = []       # last 5: True=win False=loss
        self.hesitation  = 0.0      # seconds remaining before acting
        self.action_due  = False

    def assign_personality(self):
        self.personality = random.choice(PERSONALITIES)

    def compute_bet(self):
        base = {'Safe': 30, 'Normal': 50, 'Aggressive': 70}[self.personality]
        tilt_mod = int(self.tilt * 40) * (1 if random.random() > 0.4 else -1)
        bet = base + tilt_mod + random.randint(-10, 10)
        bet = max(10, min(bet, self.money, 200))
        bet = round(bet / 10) * 10
        self.bet = bet

    def update_tilt(self, won):
        self.history.append(won)
        if len(self.history) > 5:
            self.history.pop(0)
        losses = self.history.count(False)
        self.tilt = min(1.0, losses / 5.0)

    def decide(self):
        total = hand_total(self.hand)
        threshold = {'Safe': 16, 'Normal': 15, 'Aggressive': 13}[self.personality]
        # Tilt shifts threshold down (riskier)
        threshold -= int(self.tilt * 3)
        # Bluff: occasionally stand on weak hand
        bluff_chance = 0.05 + self.tilt * 0.10
        if total < 16 and random.random() < bluff_chance:
            return 'stand'
        noise = random.uniform(-2, 2)
        return 'hit' if (total + noise) <= threshold else 'stand'

    def start_hesitation(self):
        total = hand_total(self.hand)
        confidence = (total / 21.0)
        base = 0.3 + (1 - confidence) * 1.5
        self.hesitation = base + random.uniform(-0.2, 0.4) + self.tilt * 0.5
        self.hesitation = max(0.2, self.hesitation)
        self.action_due = True

# ── Game States ────────────────────────────────────────────────────────────────
STATE_MENU   = 'menu'
STATE_GAME   = 'game'

PHASE_BET    = 'bet'
PHASE_PLAYER = 'player'
PHASE_AI     = 'ai'
PHASE_DEALER = 'dealer'
PHASE_RESOLVE= 'resolve'

# ── Main Game ──────────────────────────────────────────────────────────────────
class BlackjackGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("♠ Casino Blackjack ♠")
        self.clock  = pygame.time.Clock()
        self.state  = STATE_MENU
        self.num_ai = 2
        self._build_menu()

    # ── MENU ──────────────────────────────────────────────────────────────────
    def _build_menu(self):
        self.menu_start_btn = Button(WIDTH//2 - 110, 520, 220, 56, "▶  START GAME",
                                     color=(20,90,40), hover=(30,140,60))
        self.ai_minus = Button(WIDTH//2 - 80, 400, 50, 50, "−")
        self.ai_plus  = Button(WIDTH//2 + 30, 400, 50, 50, "+")

    def _draw_menu(self):
        self.screen.fill(C_FELT)
        # decorative lines
        for i in range(0, WIDTH, 60):
            pygame.draw.line(self.screen, C_FELT_LIGHT, (i, 0), (i, HEIGHT), 1)

        title = F_HUGE.render("♠  CASINO BLACKJACK  ♠", True, C_GOLD)
        self.screen.blit(title, title.get_rect(center=(WIDTH//2, 150)))

        sub = F_MED.render("One Player vs AI Opponents & Dealer", True, C_WHITE)
        self.screen.blit(sub, sub.get_rect(center=(WIDTH//2, 220)))

        # AI selector
        panel = pygame.Rect(WIDTH//2 - 200, 360, 400, 130)
        pygame.draw.rect(self.screen, C_PANEL, panel, border_radius=14)
        pygame.draw.rect(self.screen, C_GOLD,  panel, 2,  border_radius=14)
        lbl = F_MED.render("Number of AI Players", True, C_GOLD)
        self.screen.blit(lbl, lbl.get_rect(center=(WIDTH//2, 382)))
        num = F_BIG.render(str(self.num_ai), True, C_WHITE)
        self.screen.blit(num, num.get_rect(center=(WIDTH//2, 423)))
        self.ai_minus.draw(self.screen)
        self.ai_plus.draw(self.screen)

        self.menu_start_btn.draw(self.screen)

        tip = F_SMALL.render("Fully-featured AI with tilt, bluff & hesitation psychology", True, C_GRAY)
        self.screen.blit(tip, tip.get_rect(center=(WIDTH//2, 620)))

    def _handle_menu(self, event):
        if self.ai_minus.clicked(event):
            self.num_ai = max(0, self.num_ai - 1)
        if self.ai_plus.clicked(event):
            self.num_ai = min(4, self.num_ai + 1)
        if self.menu_start_btn.clicked(event):
            self._init_game()

    # ── GAME INIT ─────────────────────────────────────────────────────────────
    def _init_game(self):
        self.state = STATE_GAME
        ai_names = ["Alex", "Jordan", "Sam", "Riley", "Morgan"]
        random.shuffle(ai_names)
        self.ai_players = [AIPlayer(ai_names[i]) for i in range(self.num_ai)]
        self.player_money = 1000
        self.player_hand  = []
        self.player_bet   = 50
        self.player_stood = False
        self.player_bust  = False
        self.dealer_hand  = []
        self.deck         = new_deck()
        self.phase        = PHASE_BET
        self.message      = ""
        self.results      = {}   # name→result string
        self.ai_turn_idx  = 0
        self.ai_timer     = 0.0
        self._build_buttons()

    def _build_buttons(self):
        bw, bh = 120, 48
        gap = 14
        bx = WIDTH - bw - 20
        by = HEIGHT - 5*(bh+gap) - 10
        self.btn_hit   = Button(bx, by + 0*(bh+gap), bw, bh, "Hit")
        self.btn_stand = Button(bx, by + 1*(bh+gap), bw, bh, "Stand")
        self.btn_bp    = Button(bx, by + 2*(bh+gap), bw, bh, "Bet +10")
        self.btn_bm    = Button(bx, by + 3*(bh+gap), bw, bh, "Bet −10")
        self.btn_next  = Button(bx, by + 4*(bh+gap), bw, bh, "Next Round",
                                color=(80,30,10), hover=(120,50,15))
        self.buttons = [self.btn_hit, self.btn_stand, self.btn_bp, self.btn_bm, self.btn_next]

    def _deal_new_round(self):
        if len(self.deck) < 20:
            self.deck = new_deck()
        self.player_hand  = [self.deck.pop(), self.deck.pop()]
        self.player_stood = False
        self.player_bust  = False
        self.dealer_hand  = [self.deck.pop(), self.deck.pop()]
        self.results      = {}
        self.message      = ""
        for ai in self.ai_players:
            if not ai.eliminated:
                ai.hand   = [self.deck.pop(), self.deck.pop()]
                ai.stood  = False
                ai.bust   = False
                ai.done   = False
                ai.assign_personality()
                ai.compute_bet()
                ai.action_due = False
                ai.hesitation = 0.0
        self.ai_turn_idx = 0
        self.phase = PHASE_PLAYER
        self._update_buttons()

    def _update_buttons(self):
        in_player = self.phase == PHASE_PLAYER
        in_bet    = self.phase == PHASE_BET
        in_resolve= self.phase == PHASE_RESOLVE
        self.btn_hit.enabled   = in_player and not self.player_stood
        self.btn_stand.enabled = in_player and not self.player_stood
        self.btn_bp.enabled    = in_bet
        self.btn_bm.enabled    = in_bet
        self.btn_next.enabled  = in_resolve or in_bet

    # ── GAME LOOP ─────────────────────────────────────────────────────────────
    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if self.state == STATE_MENU:
                    self._handle_menu(event)
                else:
                    self._handle_game(event)

            if self.state == STATE_MENU:
                self._draw_menu()
            else:
                self._update_game(dt)
                self._draw_game()

            pygame.display.flip()

    def _handle_game(self, event):
        if self.phase == PHASE_BET:
            if self.btn_bp.clicked(event):
                self.player_bet = min(self.player_bet + 10, self.player_money)
            if self.btn_bm.clicked(event):
                self.player_bet = max(10, self.player_bet - 10)
            if self.btn_next.clicked(event):
                self._deal_new_round()

        elif self.phase == PHASE_PLAYER:
            if self.btn_hit.clicked(event):
                self.player_hand.append(self.deck.pop())
                if is_bust(self.player_hand):
                    self.player_bust = True
                    self._end_player_turn()
                elif hand_total(self.player_hand) == 21:
                    self._end_player_turn()
                self._update_buttons()
            if self.btn_stand.clicked(event):
                self.player_stood = True
                self._end_player_turn()

        elif self.phase == PHASE_RESOLVE:
            if self.btn_next.clicked(event):
                self.phase = PHASE_BET
                self._update_buttons()

    def _end_player_turn(self):
        self.phase = PHASE_AI
        # find first non-eliminated AI
        active = [i for i, a in enumerate(self.ai_players) if not a.eliminated]
        if active:
            self.ai_turn_idx = active[0]
            self.ai_players[self.ai_turn_idx].start_hesitation()
        else:
            self.phase = PHASE_DEALER
        self._update_buttons()

    def _update_game(self, dt):
        if self.phase == PHASE_AI:
            active = [i for i, a in enumerate(self.ai_players) if not a.eliminated]
            if not active:
                self.phase = PHASE_DEALER
                return

            ai = self.ai_players[self.ai_turn_idx]
            if ai.done:
                # move to next AI
                remaining = [i for i in active if i > self.ai_turn_idx]
                if remaining:
                    self.ai_turn_idx = remaining[0]
                    self.ai_players[self.ai_turn_idx].start_hesitation()
                else:
                    self.phase = PHASE_DEALER
                return

            if ai.action_due:
                ai.hesitation -= dt
                if ai.hesitation <= 0:
                    ai.action_due = False
                    decision = ai.decide()
                    if decision == 'hit':
                        ai.hand.append(self.deck.pop())
                        if is_bust(ai.hand) or hand_total(ai.hand) >= 21:
                            if is_bust(ai.hand): ai.bust = True
                            ai.done = True
                        else:
                            ai.start_hesitation()  # think again
                    else:
                        ai.stood = True
                        ai.done  = True

        elif self.phase == PHASE_DEALER:
            # dealer plays instantly (visual delay handled by draw)
            while hand_total(self.dealer_hand) < 17:
                self.dealer_hand.append(self.deck.pop())
            self._resolve()

    def _resolve(self):
        self.phase = PHASE_RESOLVE
        d_total = hand_total(self.dealer_hand)
        d_bust  = d_total > 21

        # Player
        p_total = hand_total(self.player_hand)
        if self.player_bust:
            res = "Bust 💸"
            self.player_money -= self.player_bet
        elif d_bust or p_total > d_total:
            if is_blackjack(self.player_hand) and not is_blackjack(self.dealer_hand):
                res = "Blackjack! 🎉"
                self.player_money += int(self.player_bet * 1.5)
            else:
                res = "Win! ✅"
                self.player_money += self.player_bet
        elif p_total == d_total:
            res = "Push 🤝"
        else:
            res = "Lose 💸"
            self.player_money -= self.player_bet

        self.results['YOU'] = res

        # AIs
        for ai in self.ai_players:
            if ai.eliminated: continue
            a_total = hand_total(ai.hand)
            if ai.bust:
                won = False; ar = "Bust"
                ai.money -= ai.bet
            elif d_bust or a_total > d_total:
                won = True;  ar = "Win"
                ai.money += ai.bet
            elif a_total == d_total:
                won = None;  ar = "Push"
            else:
                won = False; ar = "Lose"
                ai.money -= ai.bet
            self.results[ai.name] = ar
            if won is not None:
                ai.update_tilt(won)
            if ai.money <= 0:
                ai.money = 0
                ai.eliminated = True

        self.player_money = max(0, self.player_money)
        self._update_buttons()
        self.message = "Round over! Press Next Round to continue."

    # ── DRAWING ───────────────────────────────────────────────────────────────
    def _draw_game(self):
        surf = self.screen
        surf.fill(C_FELT)
        # grid
        for i in range(0, WIDTH, 80):
            pygame.draw.line(surf, C_FELT_LIGHT, (i, 0), (i, HEIGHT), 1)
        for j in range(0, HEIGHT, 80):
            pygame.draw.line(surf, C_FELT_LIGHT, (0, j), (WIDTH, j), 1)

        self._draw_dealer(surf)
        self._draw_player(surf)
        self._draw_ai_panels(surf)
        self._draw_hud(surf)
        self._draw_buttons(surf)
        self._draw_message(surf)

    def _draw_dealer(self, surf):
        panel = pygame.Rect(WIDTH//2 - 220, 10, 440, 140)
        pygame.draw.rect(surf, C_PANEL, panel, border_radius=12)
        pygame.draw.rect(surf, C_GOLD,  panel, 2,  border_radius=12)
        lbl = F_MED.render("DEALER", True, C_GOLD)
        surf.blit(lbl, (panel.x+12, panel.y+8))

        reveal = self.phase in (PHASE_RESOLVE, PHASE_DEALER)
        cx = panel.x + 14
        cy = panel.y + 36
        for i, card in enumerate(self.dealer_hand):
            fd = (i == 1 and not reveal)
            draw_card(surf, cx + i*(CARD_W+6), cy, card[0], card[1], face_down=fd)

        if reveal:
            total = hand_total(self.dealer_hand)
            t = F_MED.render(f"Total: {total}", True, C_RED if total > 21 else C_WHITE)
            surf.blit(t, (panel.right - t.get_width() - 12, panel.y + 8))

    def _draw_player(self, surf):
        panel = pygame.Rect(20, HEIGHT - 200, 620, 185)
        pygame.draw.rect(surf, C_PANEL, panel, border_radius=12)
        pygame.draw.rect(surf, C_GOLD,  panel, 2,  border_radius=12)

        lbl = F_MED.render("YOU", True, C_GOLD)
        surf.blit(lbl, (panel.x+12, panel.y+8))

        money_c = C_YELLOW if self.player_money > 500 else C_RED
        m = F_MED.render(f"${self.player_money}", True, money_c)
        surf.blit(m, (panel.x+12, panel.y+34))

        # bet info
        if self.phase == PHASE_BET:
            b = F_MED.render(f"Bet: ${self.player_bet}  (adjust below)", True, C_GRAY)
        else:
            b = F_MED.render(f"Bet: ${self.player_bet}", True, C_GRAY)
        surf.blit(b, (panel.x+12, panel.y+60))

        # cards
        cx = panel.x + 14
        cy = panel.y + 88
        for i, card in enumerate(self.player_hand):
            draw_card(surf, cx + i*(CARD_W+6), cy, card[0], card[1])

        if self.player_hand:
            total = hand_total(self.player_hand)
            col = C_RED if total > 21 else (C_YELLOW if total == 21 else C_WHITE)
            t = F_MED.render(f"{total}", True, col)
            surf.blit(t, (panel.right - t.get_width() - 12, panel.y+8))

        # result badge
        if 'YOU' in self.results:
            rb = F_BIG.render(self.results['YOU'], True, C_YELLOW)
            surf.blit(rb, (panel.right - rb.get_width() - 12, panel.y + 90))

    def _draw_ai_panels(self, surf):
        active = [a for a in self.ai_players if not a.eliminated]
        if not active: return
        panel_w = min(260, (WIDTH - 680) // max(1, len(active)) - 10)
        start_x = 660
        py = HEIGHT - 200

        for idx, ai in enumerate(active):
            px = start_x + idx * (panel_w + 10)
            panel = pygame.Rect(px, py, panel_w, 185)
            bg = C_PANEL
            if self.phase == PHASE_AI and idx == self._get_ai_active_local(active, ai):
                bg = (10, 50, 80)  # highlight active AI
            pygame.draw.rect(surf, bg, panel, border_radius=12)

            # tilt color border
            tilt_col = (
                int(C_GOLD[0] + ai.tilt*(C_TILT_RED[0]-C_GOLD[0])),
                int(C_GOLD[1] + ai.tilt*(C_TILT_RED[1]-C_GOLD[1])),
                int(C_GOLD[2] + ai.tilt*(C_TILT_RED[2]-C_GOLD[2])),
            )
            pygame.draw.rect(surf, tilt_col, panel, 2, border_radius=12)

            # Name + personality
            n = F_MED.render(ai.name, True, C_GOLD)
            surf.blit(n, (px+8, py+6))
            p_col = {'Safe': (100,200,100), 'Normal': C_GRAY, 'Aggressive': (220,100,100)}[ai.personality]
            ps = F_TINY.render(ai.personality, True, p_col)
            surf.blit(ps, (px + panel_w - ps.get_width() - 6, py+10))

            # Money
            mc = C_YELLOW if ai.money > 300 else C_RED
            ms = F_SMALL.render(f"${ai.money}  Bet:${ai.bet}", True, mc)
            surf.blit(ms, (px+8, py+32))

            # Tilt bar
            tbar_rect = pygame.Rect(px+8, py+54, panel_w-16, 8)
            pygame.draw.rect(surf, C_DARK_GRAY, tbar_rect, border_radius=4)
            fill_w = int((panel_w-16) * ai.tilt)
            if fill_w > 0:
                pygame.draw.rect(surf, C_TILT_RED, pygame.Rect(px+8, py+54, fill_w, 8), border_radius=4)
            tl = F_TINY.render("TILT", True, C_GRAY)
            surf.blit(tl, (px+8, py+64))

            # Cards (hidden — show card backs)
            for ci in range(len(ai.hand)):
                cx = px + 8 + ci * 34
                cy = py + 82
                if cx + 30 < px + panel_w:
                    draw_card(surf, cx, cy, face_down=True, small=True)

            # Hesitation indicator
            if self.phase == PHASE_AI and ai.action_due:
                dots = int(time.time() * 3) % 4
                ht = F_SMALL.render("Thinking" + "."*dots, True, C_BLUE_TINT)
                surf.blit(ht, (px+8, py+155))

            # Result
            if ai.name in self.results:
                rc = C_YELLOW if self.results[ai.name] == 'Win' else (C_GRAY if self.results[ai.name]=='Push' else C_RED)
                rt = F_SMALL.render(self.results[ai.name], True, rc)
                surf.blit(rt, (px + panel_w - rt.get_width() - 8, py+155))

    def _get_ai_active_local(self, active_list, ai):
        for i, a in enumerate(active_list):
            if a is ai: return i
        return -1

    def _draw_hud(self, surf):
        # Phase indicator
        phase_labels = {
            PHASE_BET: "💰 PLACE YOUR BET",
            PHASE_PLAYER: "🎮 YOUR TURN",
            PHASE_AI: "🤖 AI TURN",
            PHASE_DEALER: "🃏 DEALER TURN",
            PHASE_RESOLVE: "🏁 ROUND OVER",
        }
        pl = F_BIG.render(phase_labels.get(self.phase, ""), True, C_GOLD)
        surf.blit(pl, pl.get_rect(center=(WIDTH//2, HEIGHT - 250)))

        # Eliminated notice
        elim = [a.name for a in self.ai_players if a.eliminated]
        if elim:
            et = F_SMALL.render("Eliminated: " + ", ".join(elim), True, C_RED)
            surf.blit(et, (10, HEIGHT - 220))

    def _draw_buttons(self, surf):
        for btn in self.buttons:
            btn.draw(surf)

    def _draw_message(self, surf):
        if self.message:
            mt = F_SMALL.render(self.message, True, C_WHITE)
            surf.blit(mt, mt.get_rect(center=(WIDTH//2 - 60, HEIGHT - 30)))

# ── Entry ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    game = BlackjackGame()
    game.run()