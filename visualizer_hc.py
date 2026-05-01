"""
visualizer_hc.py  ─  Visualizador Pygame para Hill Climbing y Simulated Annealing
==================================================================================
Coloca este archivo en la misma carpeta que hc.py y utils.py.
Requiere: Python 3.8+ y pygame  →  pip install pygame

Controles:
  ESPACIO   Play / Pause
  N         Siguiente paso
  R         Reiniciar
  1         Hill Climbing
  2         Simulated Annealing
  ↑ / ↓    Velocidad (más rápido / más lento)
  ESC       Salir
"""

import sys
import time
import math
import random

import pygame

try:
    import utils
    import hc_visual as hc
except ImportError:
    print("ERROR: no se encontraron hc.py o utils.py en el directorio actual.")
    sys.exit(1)


# ═══════════════════════════════════════════════════════════════════════════════
#  PALETA DE COLORES  (fondo oscuro, estilo consistente con semanas anteriores)
# ═══════════════════════════════════════════════════════════════════════════════

C = {
    "bg":            (15,  17,  23),
    "panel":         (22,  25,  35),
    "panel_border":  (40,  45,  60),
    "empty":         (28,  32,  45),
    "grid_line":     (35,  40,  55),
    "text":          (210, 215, 230),
    "text_dim":      (100, 110, 135),
    "text_hi":       (255, 255, 255),
    "accent":        ( 80, 160, 255),
    "btn":           (40,  48,  70),
    "btn_hover":     (55,  65,  95),
    "btn_active":    (60,  90, 160),
    "btn_border":    (70,  80, 110),
    "success":       ( 80, 220, 140),
    "warning":       (255, 180,  50),
    "error":         (230,  80,  80),
    # Colores semánticos para el mapa
    "hospital":      ( 70, 160, 255),   # hospital en reposo
    "hospital_sel":  (255, 200,  50),   # hospital seleccionado (activo)
    "hospital_move": (255, 120,  50),   # hospital candidato a moverse
    "house":         (255, 180,  80),   # casa
    "candidate":     (100, 230, 170),   # casilla candidata (destino del movimiento)
    "accepted":      ( 60, 220, 120),   # movimiento aceptado
    "rejected":      (210,  70,  70),   # movimiento rechazado
    "best_move":     (180, 100, 255),   # mejor movimiento de la iteración
}

SPEEDS       = [1.2, 0.6, 0.3, 0.15, 0.06, 0.02]
SPEED_LABELS = ["×½", "×1", "×2", "×4", "×10", "×30"]
DEFAULT_SPEED_IDX = 2

CELL_SIZE    = 80
PANEL_WIDTH  = 360   # wider panel so text never wraps awkwardly
MARGIN       = 16

ALGO_NAMES   = ["Hill Climbing", "Sim. Annealing"]

# Parámetros por defecto para Simulated Annealing
SA_T_INITIAL   = 100.0
SA_T_MIN       = 0.1
SA_COOLING     = 0.995

# Mapa de ejemplo (tomado de main.py)
DEFAULT_MAP = [
    [None, None, None, None, utils.OBJECT_HOSPITAL, None, None, None, utils.OBJECT_HOUSE, None],
    [None, None, utils.OBJECT_HOUSE, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None, None],
    [None, utils.OBJECT_HOUSE, None, None, None, None, None, None, None, utils.OBJECT_HOSPITAL],
    [None, None, None, None, None, None, utils.OBJECT_HOUSE, None, None, None],
]


# ═══════════════════════════════════════════════════════════════════════════════
#  HELPERS DE COLOR
# ═══════════════════════════════════════════════════════════════════════════════

def _lerp_color(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))

def _darken(c, factor):
    return tuple(max(0, int(v * factor)) for v in c)

def _ease(t):
    return 1 - (1 - t) ** 2


# ═══════════════════════════════════════════════════════════════════════════════
#  ESTADO DE LA APLICACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

class AppState:
    def __init__(self, initial_map):
        self.initial_map  = initial_map
        self.rows         = len(initial_map)
        self.cols         = len(initial_map[0])

        self.algo_idx     = 0          # 0 = Hill Climbing, 1 = SA
        self.speed_idx    = DEFAULT_SPEED_IDX

        # Estado del generador
        self.generator    = None
        self.step_state   = None       # último estado emitido

        # Métricas
        self.iterations   = 0
        self.steps_taken  = 0
        self.initial_cost = utils.cost(initial_map)
        self.best_cost_seen = self.initial_cost

        # Control
        self.playing      = False
        self.done         = False
        self._last_step_t = 0.0

        # Animación highlight
        self._flash       = {}  # pos → (color, phase 0→1)

        self.reset()

    # ── Propiedades ───────────────────────────────────────────────────────────
    @property
    def algo_name(self):
        return ALGO_NAMES[self.algo_idx]

    @property
    def speed_s(self):
        return SPEEDS[self.speed_idx]

    @property
    def speed_label(self):
        return SPEED_LABELS[self.speed_idx]

    # ── Control ───────────────────────────────────────────────────────────────
    def reset(self):
        import copy
        map_copy = copy.deepcopy(self.initial_map)
        if self.algo_idx == 0:
            self.generator = hc.hill_climbing_steps(map_copy)
        else:
            self.generator = hc.simulated_annealing_steps(
                map_copy, SA_T_MIN, SA_T_INITIAL, SA_COOLING
            )
        self.step_state = {
            "grid": self.initial_map,
            "current_cost": self.initial_cost,
            "hospital": None,
            "candidate_move": None,
            "candidate_map": self.initial_map,
            "candidate_cost": self.initial_cost,
            "best_map": self.initial_map,
            "best_cost": self.initial_cost,
            "accepted": False,
            "done": False,
            "message": "Listo. Presiona ▶ o N para comenzar.",
        }
        self.iterations      = 0
        self.steps_taken     = 0
        self.initial_cost    = utils.cost(self.initial_map)
        self.best_cost_seen  = self.initial_cost
        self.playing         = False
        self.done            = False
        self._last_step_t    = 0.0
        self._flash          = {}

    def set_algo(self, idx):
        self.algo_idx = idx
        self.reset()

    def toggle_play(self):
        if self.done:
            return
        self.playing = not self.playing

    def step(self):
        if self.done:
            return
        try:
            state = next(self.generator)
            self._apply_state(state)
        except StopIteration:
            self.done    = True
            self.playing = False

    def _apply_state(self, state):
        self.step_state  = state
        self.steps_taken += 1

        if state["accepted"]:
            self.iterations += 1

        if state["best_cost"] < self.best_cost_seen:
            self.best_cost_seen = state["best_cost"]

        # Registrar flashes visuales
        if state["candidate_move"]:
            color = C["accepted"] if state["accepted"] else C["rejected"]
            self._flash[state["candidate_move"]] = [color, 0.0]
        if state["hospital"]:
            self._flash[state["hospital"]] = [C["hospital_sel"], 0.0]

        if state["done"]:
            self.done    = True
            self.playing = False

    def auto_step(self):
        if not self.playing or self.done:
            return
        now = time.time()
        if now - self._last_step_t >= self.speed_s:
            self._last_step_t = now
            self.step()

    def tick_animations(self, dt):
        for k in list(self._flash.keys()):
            self._flash[k][1] = min(1.0, self._flash[k][1] + dt * 4.0)
            if self._flash[k][1] >= 1.0:
                del self._flash[k]

    def speed_up(self):
        self.speed_idx = min(self.speed_idx + 1, len(SPEEDS) - 1)

    def speed_down(self):
        self.speed_idx = max(self.speed_idx - 1, 0)


# ═══════════════════════════════════════════════════════════════════════════════
#  RENDERIZADO
# ═══════════════════════════════════════════════════════════════════════════════

class Renderer:
    def __init__(self, screen, fonts, state: AppState):
        self.screen = screen
        self.fonts  = fonts
        self.state  = state
        self.W, self.H = screen.get_size()

        # Calcular tamaño de celda dinámicamente
        avail_w = self.W - PANEL_WIDTH - 3 * MARGIN
        avail_h = self.H - 2 * MARGIN
        cs_w = avail_w // state.cols
        cs_h = avail_h // state.rows
        self.cell_size = max(40, min(cs_w, cs_h, 100))

        self.grid_x = MARGIN
        self.grid_y = MARGIN + (avail_h - state.rows * self.cell_size) // 2
        self.grid_w = state.cols * self.cell_size
        self.grid_h = state.rows * self.cell_size

        self.panel_x = self.grid_x + self.grid_w + MARGIN
        self.panel_y = MARGIN
        self.panel_w = PANEL_WIDTH
        self.panel_h = self.H - 2 * MARGIN

        self._ctrl_rects  = {}
        self._speed_rects = {}
        self._algo_rects  = []

    def draw(self):
        self._ctrl_rects  = {}
        self._speed_rects = {}
        self._algo_rects  = []
        self.screen.fill(C["bg"])
        self._draw_grid()
        self._draw_panel()
        pygame.display.flip()

    # ── Grilla ────────────────────────────────────────────────────────────────
    def _cell_rect(self, cx, cy):
        px = self.grid_x + cx * self.cell_size
        py = self.grid_y + cy * self.cell_size
        return pygame.Rect(px, py, self.cell_size, self.cell_size)

    def _draw_grid(self):
        s  = self.state
        ss = s.step_state

        current_grid     = ss["grid"]
        hospital_sel     = ss["hospital"]
        candidate_move   = ss["candidate_move"]
        best_map         = ss.get("best_map")

        for row in range(s.rows):
            for col in range(s.cols):
                pos  = (col, row)
                rect = self._cell_rect(col, row)
                cell = current_grid[row][col]

                # ── Fondo base
                pygame.draw.rect(self.screen, C["empty"], rect)

                # ── Highlight de flash animado
                if pos in s._flash:
                    flash_color, phase = s._flash[pos]
                    alpha_factor = 1.0 - _ease(phase)
                    blended = _lerp_color(C["empty"], flash_color, alpha_factor * 0.7)
                    pygame.draw.rect(self.screen, blended, rect)

                # ── Resaltar candidato
                if candidate_move and pos == tuple(candidate_move):
                    t = time.time()
                    pulse = 0.6 + 0.4 * abs(math.sin(t * 4))
                    color = _lerp_color(C["empty"], C["candidate"], pulse)
                    pygame.draw.rect(self.screen, color, rect)

                # ── Dibujar emoji o símbolo de objeto
                if cell == utils.OBJECT_HOSPITAL:
                    self._draw_cell_object(rect, "🏥", C["hospital_sel"] if pos == hospital_sel else C["hospital"])
                elif cell == utils.OBJECT_HOUSE:
                    self._draw_cell_object(rect, "🏠", C["house"])

                # ── Borde de grilla
                border_color = C["panel_border"]
                if pos == hospital_sel:
                    border_color = C["hospital_sel"]
                elif candidate_move and pos == tuple(candidate_move):
                    border_color = C["candidate"]
                pygame.draw.rect(self.screen, border_color, rect, 1)

        # Borde del área
        border = pygame.Rect(self.grid_x - 2, self.grid_y - 2,
                             self.grid_w + 4, self.grid_h + 4)
        pygame.draw.rect(self.screen, C["panel_border"], border, 2, border_radius=6)

    def _draw_cell_object(self, rect, emoji, color):
        """Dibuja un símbolo de objeto en la celda con un indicador de color."""
        # Círculo de fondo
        pad    = self.cell_size // 5
        inner  = rect.inflate(-pad * 2, -pad * 2)
        pygame.draw.rect(self.screen, _darken(color, 0.35), inner, border_radius=6)
        pygame.draw.rect(self.screen, color, inner, 2, border_radius=6)
        # Texto emoji
        f    = self.fonts["emoji"]
        surf = f.render(emoji, True, C["text_hi"])
        self.screen.blit(surf, surf.get_rect(center=rect.center))

    # ── Panel lateral ─────────────────────────────────────────────────────────
    def _draw_panel(self):
        px, py, pw, ph = self.panel_x, self.panel_y, self.panel_w, self.panel_h

        panel_rect = pygame.Rect(px, py, pw, ph)
        pygame.draw.rect(self.screen, C["panel"], panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, C["panel_border"], panel_rect, 2, border_radius=10)

        cy = py + 12

        cy = self._panel_title("🏥 Hospital Optimizer", px, cy, pw)
        cy += 4

        cy = self._section_label("Algoritmo", px, cy, pw)
        cy = self._algo_buttons(px, cy, pw)
        cy += 6

        cy = self._section_label("Estado", px, cy, pw)
        s  = self.state
        ss = s.step_state

        if s.done:
            status_txt   = "✓ Óptimo local"
            status_color = C["success"]
        elif s.playing:
            status_txt   = "▶ Ejecutando…"
            status_color = C["warning"]
        else:
            status_txt   = "⏸ Pausado"
            status_color = C["text_dim"]

        cy = self._panel_kv("", status_txt, px, cy, pw, val_color=status_color, bold_val=True)
        cy += 1

        # Mensaje del último paso
        msg = ss.get("message", "")
        if msg:
            cy = self._wrapped_text(msg, px, cy, pw)
        cy += 4

        cy = self._section_label("Métricas", px, cy, pw)
        cy = self._panel_kv("Costo inicial",   str(s.initial_cost),    px, cy, pw)
        cy = self._panel_kv("Costo actual",    str(ss["current_cost"]), px, cy, pw,
                             val_color=C["warning"])
        cy = self._panel_kv("Mejor costo",     str(s.best_cost_seen),  px, cy, pw,
                             val_color=C["success"])

        improvement = s.initial_cost - s.best_cost_seen
        pct = (improvement / s.initial_cost * 100) if s.initial_cost > 0 else 0
        cy = self._panel_kv("Mejora",
                             f"{improvement} ({pct:.1f}%)",
                             px, cy, pw,
                             val_color=C["accent"])
        cy = self._panel_kv("Pasos",           str(s.steps_taken),     px, cy, pw)
        cy = self._panel_kv("Mejoras",         str(s.iterations),      px, cy, pw)

        # Temperatura (solo SA)
        if s.algo_idx == 1:
            temp = ss.get("temperature", 0)
            cy = self._panel_kv("Temperatura", f"{temp:.3f}", px, cy, pw,
                                val_color=C["error"])
            prob = ss.get("acceptance_prob", 0)
            cy = self._panel_kv("P(aceptar)", f"{prob:.4f}", px, cy, pw)

        cy += 4

        cy = self._section_label("Movimiento", px, cy, pw)
        h = ss.get("hospital")
        m = ss.get("candidate_move")
        cy = self._panel_kv("Hospital",    str(h) if h else "—", px, cy, pw,
                             val_color=C["hospital_sel"])
        cy = self._panel_kv("Candidato",   str(m) if m else "—", px, cy, pw,
                             val_color=C["candidate"])
        c_cost = ss.get("candidate_cost")
        cy = self._panel_kv("Costo cand.", str(c_cost) if c_cost is not None else "—",
                             px, cy, pw)
        accepted_txt = "✓ Sí" if ss.get("accepted") else ("✗ No" if h else "—")
        accepted_col = C["accepted"] if ss.get("accepted") else (C["rejected"] if h else C["text_dim"])
        cy = self._panel_kv("Aceptado", accepted_txt, px, cy, pw,
                             val_color=accepted_col, bold_val=True)
        cy += 4

        cy = self._section_label("Controles", px, cy, pw)
        cy = self._control_buttons(px, cy, pw)
        cy += 4

        cy = self._section_label("Velocidad", px, cy, pw)
        cy = self._speed_controls(px, cy, pw)
        cy += 6

        cy = self._section_label("Leyenda", px, cy, pw)
        legend = [
            (C["hospital"],     "Hospital"),
            (C["hospital_sel"], "Hospital activo"),
            (C["house"],        "Casa"),
            (C["candidate"],    "Destino candidato"),
            (C["accepted"],     "Movimiento aceptado"),
            (C["rejected"],     "Movimiento rechazado"),
        ]
        for color, label in legend:
            cy = self._legend_item(color, label, px, cy, pw)
        cy += 4

        cy = self._section_label("Atajos", px, cy, pw)
        shortcuts = [
            ("SPC", "Play / Pause"),
            ("N",   "Siguiente paso"),
            ("R",   "Reiniciar"),
            ("1/2", "Cambiar algoritmo"),
            ("↑↓",  "Velocidad"),
            ("ESC", "Salir"),
        ]
        for key, desc in shortcuts:
            cy = self._shortcut_row(key, desc, px, cy, pw)
            if cy > py + ph - 10:
                break

    # ── Helpers de panel ──────────────────────────────────────────────────────
    def _panel_title(self, text, px, cy, pw):
        f    = self.fonts["title"]
        surf = f.render(text, True, C["text_hi"])
        self.screen.blit(surf, (px + (pw - surf.get_width()) // 2, cy))
        return cy + surf.get_height() + 4

    def _section_label(self, text, px, cy, pw):
        f    = self.fonts["small_bold"]
        surf = f.render(text.upper(), True, C["accent"])
        self.screen.blit(surf, (px + 14, cy))
        line_y = cy + surf.get_height() + 2
        pygame.draw.line(self.screen, C["panel_border"],
                         (px + 14, line_y), (px + pw - 14, line_y))
        return line_y + 4

    def _panel_kv(self, key, val, px, cy, pw, val_color=None, bold_val=False):
        fk = self.fonts["small"]
        fv = self.fonts["small_bold"] if bold_val else self.fonts["small"]
        vc = val_color or C["text"]
        max_h = 0
        if key:
            sk = fk.render(key + ":", True, C["text_dim"])
            self.screen.blit(sk, (px + 14, cy))
            max_h = sk.get_height()
        sv = fv.render(str(val), True, vc)
        self.screen.blit(sv, (px + pw - 14 - sv.get_width(), cy))
        max_h = max(max_h, sv.get_height())
        return cy + max_h + 2

    def _wrapped_text(self, text, px, cy, pw):
        f     = self.fonts["small"]
        words = text.split()
        line  = ""
        max_w = pw - 28
        for word in words:
            test = line + (" " if line else "") + word
            if f.size(test)[0] > max_w:
                if line:
                    surf = f.render(line, True, C["text_dim"])
                    self.screen.blit(surf, (px + 14, cy))
                    cy  += surf.get_height() + 1
                line = word
            else:
                line = test
        if line:
            surf = f.render(line, True, C["text_dim"])
            self.screen.blit(surf, (px + 14, cy))
            cy += surf.get_height() + 1
        return cy

    def _algo_buttons(self, px, cy, pw):
        names  = ALGO_NAMES
        gap    = 6
        total  = pw - 28 - gap * (len(names) - 1)
        bw     = total // len(names)
        bh     = 28
        mouse  = pygame.mouse.get_pos()
        for i, name in enumerate(names):
            bx   = px + 14 + i * (bw + gap)
            rect = pygame.Rect(bx, cy, bw, bh)
            active = (i == self.state.algo_idx)
            hover  = rect.collidepoint(mouse) and not active
            bg = C["btn_active"] if active else (C["btn_hover"] if hover else C["btn"])
            bc = C["accent"]     if active else C["btn_border"]
            pygame.draw.rect(self.screen, bg, rect, border_radius=6)
            pygame.draw.rect(self.screen, bc, rect, 1, border_radius=6)
            f    = self.fonts["small_bold"] if active else self.fonts["small"]
            tc   = C["text_hi"] if active else C["text"]
            surf = f.render(name, True, tc)
            self.screen.blit(surf, surf.get_rect(center=rect.center))
            self._algo_rects.append((rect, i))
        return cy + bh + 2

    def _control_buttons(self, px, cy, pw):
        s     = self.state
        mouse = pygame.mouse.get_pos()
        label_play = "⏸ Pausa" if s.playing else "▶ Play"
        btns = [
            (label_play, "play_pause", not s.done),
            ("▷ Paso",   "step",       not s.done),
            ("↺ Reset",  "reset",      True),
        ]
        gap = 6
        bw  = (pw - 28 - gap * 2) // 3
        bh  = 28
        for i, (label, action, enabled) in enumerate(btns):
            bx   = px + 14 + i * (bw + gap)
            rect = pygame.Rect(bx, cy, bw, bh)
            hover = rect.collidepoint(mouse) and enabled
            bg  = C["btn_hover"] if hover else (C["btn"] if enabled else _darken(C["btn"], 0.55))
            tc  = C["text"] if enabled else C["text_dim"]
            pygame.draw.rect(self.screen, bg, rect, border_radius=6)
            pygame.draw.rect(self.screen, C["btn_border"], rect, 1, border_radius=6)
            surf = self.fonts["small"].render(label, True, tc)
            self.screen.blit(surf, surf.get_rect(center=rect.center))
            self._ctrl_rects[action] = rect
        return cy + bh + 2

    def _speed_controls(self, px, cy, pw):
        mouse = pygame.mouse.get_pos()
        bw, bh = 26, 26
        # Botón −
        rx = px + 14
        r  = pygame.Rect(rx, cy, bw, bh)
        hov = r.collidepoint(mouse)
        pygame.draw.rect(self.screen, C["btn_hover"] if hov else C["btn"], r, border_radius=5)
        pygame.draw.rect(self.screen, C["btn_border"], r, 1, border_radius=5)
        surf = self.fonts["bold"].render("−", True, C["text"])
        self.screen.blit(surf, surf.get_rect(center=r.center))
        self._speed_rects["slower"] = r
        # Etiqueta
        lsurf = self.fonts["small_bold"].render(self.state.speed_label, True, C["accent"])
        lx    = px + 14 + bw + (pw - 28 - 2 * bw - lsurf.get_width()) // 2
        self.screen.blit(lsurf, (lx, cy + (bh - lsurf.get_height()) // 2))
        # Botón +
        rx2 = px + pw - 14 - bw
        r2  = pygame.Rect(rx2, cy, bw, bh)
        hov2 = r2.collidepoint(mouse)
        pygame.draw.rect(self.screen, C["btn_hover"] if hov2 else C["btn"], r2, border_radius=5)
        pygame.draw.rect(self.screen, C["btn_border"], r2, 1, border_radius=5)
        surf2 = self.fonts["bold"].render("+", True, C["text"])
        self.screen.blit(surf2, surf2.get_rect(center=r2.center))
        self._speed_rects["faster"] = r2
        return cy + bh + 2

    def _legend_item(self, color, text, px, cy, pw):
        sq = 11
        sy = cy + 2
        pygame.draw.rect(self.screen, color,
                         pygame.Rect(px + 14, sy, sq, sq), border_radius=3)
        pygame.draw.rect(self.screen, C["text_dim"],
                         pygame.Rect(px + 14, sy, sq, sq), 1, border_radius=3)
        surf = self.fonts["small"].render(text, True, C["text_dim"])
        self.screen.blit(surf, (px + 14 + sq + 5, cy))
        return cy + surf.get_height() + 1

    def _shortcut_row(self, key, desc, px, cy, pw):
        sk = self.fonts["small_bold"].render(key, True, C["accent"])
        sd = self.fonts["small"].render(desc, True, C["text_dim"])
        self.screen.blit(sk, (px + 14, cy))
        self.screen.blit(sd, (px + pw - 14 - sd.get_width(), cy))
        return cy + max(sk.get_height(), sd.get_height()) + 1

    # ── Hit-testing ───────────────────────────────────────────────────────────
    def hit_algo(self, mp):
        for rect, idx in self._algo_rects:
            if rect.collidepoint(mp):
                return idx
        return None

    def hit_ctrl(self, mp):
        for action, rect in self._ctrl_rects.items():
            if rect.collidepoint(mp):
                return action
        return None

    def hit_speed(self, mp):
        for action, rect in self._speed_rects.items():
            if rect.collidepoint(mp):
                return action
        return None


# ═══════════════════════════════════════════════════════════════════════════════
#  BUCLE PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    pygame.init()
    pygame.display.set_caption("Hospital Optimizer — Hill Climbing / Simulated Annealing")

    initial_map = DEFAULT_MAP
    rows = len(initial_map)
    cols = len(initial_map[0])

    # ── Calcular tamaño de ventana ─────────────────────────────────────────────
    # El panel lateral necesita ~820px de alto para mostrar todo su contenido.
    # La ventana se dimensiona para que quepan tanto el mapa como el panel.
    PANEL_MIN_H = 820

    info   = pygame.display.Info()
    max_w  = int(info.current_w * 0.94)
    max_h  = int(info.current_h * 0.94)

    # Altura objetivo: la mayor entre el mínimo del panel y lo disponible en pantalla
    target_h = min(max(PANEL_MIN_H, max_h), max_h)

    cs_w = (max_w - PANEL_WIDTH - 3 * MARGIN) // cols
    cs_h = (target_h - 2 * MARGIN)             // rows
    cs   = max(48, min(cs_w, cs_h, 110))

    grid_h = rows * cs + 2 * MARGIN
    H      = max(grid_h, target_h)
    if H > max_h:
        H  = max_h
        cs = max(40, (H - 2 * MARGIN) // rows)
    W = MARGIN + cols * cs + MARGIN + PANEL_WIDTH + MARGIN

    global CELL_SIZE
    CELL_SIZE = cs

    screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)

    # Fuentes
    pygame.font.init()
    try:
        fn = pygame.font.match_font("segoeui,helveticaneue,arial,ubuntu,freesans")
        fonts = {
            "title":      pygame.font.Font(fn, 15),
            "bold":       pygame.font.Font(fn, 17),
            "small_bold": pygame.font.Font(fn, 13),
            "small":      pygame.font.Font(fn, 13),
        }
        fonts["title"].set_bold(True)
        fonts["bold"].set_bold(True)
        fonts["small_bold"].set_bold(True)
    except Exception:
        fonts = {k: pygame.font.SysFont("sans", sz)
                 for k, sz in [("title", 14), ("bold", 17),
                                ("small_bold", 13), ("small", 13)]}

    # Fuente emoji (separada para compatibilidad)
    try:
        ef = pygame.font.match_font("segoeuiemoji,notocoloremoji,applesymbols,symbola")
        fonts["emoji"] = pygame.font.Font(ef, cs // 2)
    except Exception:
        fonts["emoji"] = fonts["bold"]

    state    = AppState(initial_map)
    renderer = Renderer(screen, fonts, state)

    clock     = pygame.time.Clock()
    prev_time = time.time()

    running = True
    while running:
        now = time.time()
        dt  = now - prev_time
        prev_time = now

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEORESIZE:
                screen   = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                renderer = Renderer(screen, fonts, state)

            elif event.type == pygame.KEYDOWN:
                if   event.key == pygame.K_ESCAPE: running = False
                elif event.key == pygame.K_SPACE:  state.toggle_play()
                elif event.key == pygame.K_n:      state.step()
                elif event.key == pygame.K_r:      state.reset()
                elif event.key == pygame.K_1:      state.set_algo(0)
                elif event.key == pygame.K_2:      state.set_algo(1)
                elif event.key == pygame.K_UP:     state.speed_up()
                elif event.key == pygame.K_DOWN:   state.speed_down()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mp = event.pos
                idx = renderer.hit_algo(mp)
                if idx is not None:
                    state.set_algo(idx)
                    renderer = Renderer(screen, fonts, state)
                    continue
                action = renderer.hit_ctrl(mp)
                if action == "play_pause": state.toggle_play()
                elif action == "step":     state.step()
                elif action == "reset":
                    state.reset()
                    renderer = Renderer(screen, fonts, state)
                sv = renderer.hit_speed(mp)
                if sv == "faster": state.speed_up()
                elif sv == "slower": state.speed_down()

        state.auto_step()
        state.tick_animations(dt)
        renderer.draw()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()