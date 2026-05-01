"""Calculator application - with light/dark theme support."""

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from .engine import evaluate, set_trig_mode, is_deg_mode

MAPPING = {
    "/": "/", "*": "*", "-": "-",
    "sin": "sin(", "cos": "cos(", "tan": "tan(",
    "asin": "asin(", "acos": "acos(", "atan": "atan(",
    "log": "log(", "ln": "ln(",
    "x^y": "**", "^2": "**2", "^3": "**3",
    "pi": "pi",
}

THEMES = {
    "dark": {
        "bg": (0.1, 0.1, 0.12, 1),
        "expr": (0.5, 0.5, 0.55, 1),
        "result": (1, 1, 1, 1),
        "num": {"bg": (0.25, 0.25, 0.3, 1), "fg": (1, 1, 1, 1)},
        "op":  {"bg": (0.35, 0.35, 0.5, 1), "fg": (1, 1, 1, 1)},
        "sci": {"bg": (0.2, 0.18, 0.25, 1), "fg": (0.7, 0.7, 1, 1), "size": 14},
        "eq":  {"bg": (0.2, 0.5, 0.8, 1), "fg": (1, 1, 1, 1)},
        "ac":  {"bg": (0.35, 0.15, 0.15, 1), "fg": (1, 0.7, 0.7, 1)},
        "del": {"bg": (0.3, 0.2, 0.15, 1), "fg": (1, 0.8, 0.7, 1)},
        "deg": {"bg": (0.15, 0.3, 0.15, 1), "fg": (0.7, 1, 0.7, 1)},
        "rad": {"bg": (0.3, 0.15, 0.15, 1), "fg": (1, 0.7, 0.7, 1)},
        "theme": {"bg": (0.2, 0.2, 0.25, 1), "fg": (0.7, 0.7, 0.8, 1)},
    },
    "light": {
        "bg": (0.93, 0.93, 0.95, 1),
        "expr": (0.4, 0.4, 0.45, 1),
        "result": (0.05, 0.05, 0.1, 1),
        "num": {"bg": (0.85, 0.85, 0.9, 1), "fg": (0.1, 0.1, 0.15, 1)},
        "op":  {"bg": (0.65, 0.65, 0.8, 1), "fg": (0.1, 0.1, 0.15, 1)},
        "sci": {"bg": (0.75, 0.73, 0.88, 1), "fg": (0.15, 0.15, 0.35, 1), "size": 14},
        "eq":  {"bg": (0.2, 0.5, 0.8, 1), "fg": (1, 1, 1, 1)},
        "ac":  {"bg": (0.85, 0.4, 0.4, 1), "fg": (1, 1, 1, 1)},
        "del": {"bg": (0.8, 0.5, 0.3, 1), "fg": (1, 1, 1, 1)},
        "deg": {"bg": (0.3, 0.6, 0.3, 1), "fg": (1, 1, 1, 1)},
        "rad": {"bg": (0.6, 0.3, 0.3, 1), "fg": (1, 1, 1, 1)},
        "theme": {"bg": (0.85, 0.85, 0.88, 1), "fg": (0.15, 0.15, 0.2, 1)},
    },
}


class CalculatorApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.expression = ""
        self.result = "0"
        self._just_evaluated = False
        self.theme = "dark"
        self._widgets = []

    def w(self, text, role, cb, size=20):
        colors = THEMES[self.theme][role]
        b = Button(
            text=text,
            font_size=dp(colors.get("size", size)),
            background_normal="",
            background_color=colors["bg"],
            color=colors["fg"],
        )
        b.role = role
        if cb:
            b.bind(on_release=cb)
        self._widgets.append(b)
        return b

    def build(self):
        Window.size = (400, 760)
        root = BoxLayout(orientation="vertical", spacing=dp(2), padding=dp(2))
        self.root_widget = root
        with root.canvas.before:
            self.bg_color = Color(rgba=THEMES[self.theme]["bg"])
            self.bg_rect = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=self._update_bg_rect, size=self._update_bg_rect)

        # === Display ===
        self.expr_label = Label(
            text="",
            font_size=dp(16),
            size_hint_y=0.07,
            color=THEMES[self.theme]["expr"],
            halign="right",
            valign="bottom",
            text_size=(0, 0),
            padding=(dp(8), dp(2)),
        )
        self.res_label = Label(
            text="0",
            font_size=dp(48),
            size_hint_y=0.15,
            bold=True,
            color=THEMES[self.theme]["result"],
            halign="right",
            valign="middle",
            text_size=(0, 0),
            padding=(dp(8), dp(2)),
        )
        self.expr_label.bind(size=lambda l, s: setattr(l, "text_size", (s[0] - dp(16), s[1])))
        self.res_label.bind(size=lambda l, s: setattr(l, "text_size", (s[0] - dp(16), s[1])))
        disp = BoxLayout(orientation="vertical", size_hint_y=0.22, spacing=dp(1))
        disp.add_widget(self.expr_label)
        disp.add_widget(self.res_label)
        root.add_widget(disp)

        # === Toggle bar: DEG + THEME ===
        bar = BoxLayout(orientation="horizontal", size_hint_y=0.05, spacing=dp(2))
        self.deg_btn = self.w("DEG", "deg", lambda _: self.toggle_trig_mode(), 14)
        bar.add_widget(self.deg_btn)
        self.theme_btn = self.w("DARK", "theme", lambda _: self.toggle_theme(), 14)
        bar.add_widget(self.theme_btn)
        root.add_widget(bar)

        # === Scientific grid ===
        sci = GridLayout(cols=6, spacing=dp(2), size_hint_y=0.26)
        for key in (
            "sin", "cos", "tan", "(", ")", "AC",
            "asin", "acos", "atan", "log", "ln", "DEL",
            "^2", "^3", "x^y", "pi", "e", "+/-",
        ):
            role = "ac" if key == "AC" else "del" if key == "DEL" else "sci"
            sci.add_widget(self.w(key, role, lambda _, k=key: self.press(k), 14))
        root.add_widget(sci)

        # === Number pad ===
        pad = GridLayout(cols=4, spacing=dp(2), size_hint_y=0.47)
        for row in (("1", "2", "3", "÷"), ("4", "5", "6", "×"),
                    ("7", "8", "9", "−"), ("0", ".", "=", "+")):
            for k in row:
                role = "eq" if k == "=" else "op" if k in ("÷", "×", "−", "+") else "num"
                pad.add_widget(self.w(k, role, lambda _, x=k: self.press(x)))
        root.add_widget(pad)

        return root

    # --- Theme ---

    def _update_bg_rect(self, *args):
        self.bg_rect.pos = self.root_widget.pos
        self.bg_rect.size = self.root_widget.size

    def apply_theme(self):
        t = THEMES[self.theme]
        self.bg_color.rgba = t["bg"]
        self.expr_label.color = t["expr"]
        self.res_label.color = t["result"]
        for w in self._widgets:
            s = t.get(w.role, t["num"])
            w.background_color = s["bg"]
            w.color = s["fg"]
        self.theme_btn.text = "LIGHT" if self.theme == "dark" else "DARK"
        self._update_deg_colors()

    def _update_deg_colors(self):
        t = THEMES[self.theme]
        deg = is_deg_mode()
        s = t["deg"] if deg else t["rad"]
        self.deg_btn.background_color = s["bg"]
        self.deg_btn.color = s["fg"]

    def toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self.apply_theme()

    # --- Actions ---

    def press(self, key):
        if key == "AC":
            self.expression = ""
            self.result = "0"
            self._just_evaluated = False
            self._update_display()
            return
        if key == "DEL":
            self.expression = self.expression[:-1]
            if not self.expression:
                self.result = "0"
            self._just_evaluated = False
            self._update_display()
            return
        if key == "=":
            if not self.expression:
                return
            res = evaluate(self.expression)
            expr = self.expression
            self.expression = res if res not in ("Error", "Overflow", "") else self.expression
            self.result = res
            self._just_evaluated = True
            self._update_display(show_expr=expr)
            return
        if key == "+/-":
            if self.expression:
                if not self.expression.startswith("-("):
                    self.expression = f"-({self.expression})"
                else:
                    self.expression = self.expression[2:-1]
            self._just_evaluated = False
            self._update_display()
            return
        if self._just_evaluated and key.isdigit():
            self.expression = ""
            self.result = "0"
            self._just_evaluated = False
        self._just_evaluated = False
        insert = MAPPING.get(key, key)
        self.expression += insert
        if insert == "(" and len(self.expression) > 1:
            prev = self.expression[-2]
            if prev.isdigit() or prev in (")", "i"):
                self.expression = self.expression[:-1] + "*("
        self._update_display()

    def toggle_trig_mode(self):
        deg = not is_deg_mode()
        set_trig_mode(deg)
        self.deg_btn.text = "DEG" if deg else "RAD"
        self._update_deg_colors()

    def _update_display(self, show_expr=None):
        self.expr_label.text = show_expr or self.expression
        self.res_label.text = self.result if self.result else "0"
