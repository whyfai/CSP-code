import tkinter as tk
from tkinter import ttk


from impact_model import calculate_impacts

BAR_COLORS = ["#3366cc", "#dc3912", "#ff9900", "#109618"]
APP_BG = "#f3efe6"
CARD_BG = "#fbf9f4"
TITLE_COLOR = "#1f2a37"
TEXT_COLOR = "#2c3e50"
MUTED_TEXT = "#566573"
ACCENT = "#c27d28"
BASELINE_CRUDE_PRICE = 50.0
MIN_CRUDE_PRICE = 30.0
MAX_CRUDE_PRICE = 200.0
DEPENDENT_LABELS = ["Transportation", "Food Cost", "Annual Expenditure", "Healthcare"]
VALUE_UNIT = "CPI"


class OilImpactApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Crude Oil Price Impact Simulator")
        self.geometry("980x640")
        self.minsize(940, 600)
        self.configure(bg=APP_BG)

        self.crude_price = tk.DoubleVar(value=80.0)
        self.crude_price_entry = tk.StringVar(value="80.0")
        self.metric_value_vars = {name: tk.StringVar() for name in DEPENDENT_LABELS}
        self.metric_change_vars = {name: tk.StringVar() for name in DEPENDENT_LABELS}

        self._build_ui()
        self.update_simulation()

    def _configure_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("App.TFrame", background=APP_BG)
        style.configure("Card.TFrame", background=CARD_BG)

        style.configure(
            "Title.TLabel",
            background=APP_BG,
            foreground=TITLE_COLOR,
            font=("Segoe UI", 22, "bold"),
        )
        style.configure(
            "SubTitle.TLabel",
            background=APP_BG,
            foreground=MUTED_TEXT,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Section.TLabel",
            background=CARD_BG,
            foreground=TEXT_COLOR,
            font=("Segoe UI", 11, "bold"),
        )
        style.configure(
            "Body.TLabel",
            background=CARD_BG,
            foreground=TEXT_COLOR,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Value.TLabel",
            background=CARD_BG,
            foreground=ACCENT,
            font=("Segoe UI", 10, "bold"),
        )
        style.configure(
            "CrudeBadge.TLabel",
            background=CARD_BG,
            foreground=ACCENT,
            font=("Segoe UI", 12, "bold"),
        )

        style.configure(
            "Card.TLabelframe",
            background=CARD_BG,
            borderwidth=1,
            relief="solid",
        )
        style.configure(
            "Card.TLabelframe.Label",
            background=CARD_BG,
            foreground=TEXT_COLOR,
            font=("Segoe UI", 10, "bold"),
        )

        style.configure(
            "Accent.Horizontal.TScale",
            background=CARD_BG,
            troughcolor="#e7ddca",
        )

        style.configure(
            "BoxTitle.TLabel",
            background=CARD_BG,
            foreground=TEXT_COLOR,
            font=("Segoe UI", 11, "bold"),
        )
        style.configure(
            "BoxValue.TLabel",
            background=CARD_BG,
            foreground=ACCENT,
            font=("Segoe UI", 18, "bold"),
        )
        style.configure(
            "BoxChange.TLabel",
            background=CARD_BG,
            foreground=MUTED_TEXT,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Tab.TFrame",
            background=APP_BG,
        )

    def _build_ui(self) -> None:
        self._configure_styles()

        frame = ttk.Frame(self, style="App.TFrame", padding=18)
        frame.pack(fill="both", expand=True)

        title = ttk.Label(frame, text="Crude Oil Impact Simulator", style="Title.TLabel")
        title.pack(anchor="w")

        explanation = ttk.Label(
            frame,
            text=(
                "Move the slider to simulate crude oil price shifts. "
                "Estimated downstream costs and the comparison to baseline update instantly."
            ),
            style="SubTitle.TLabel",
            wraplength=900,
        )
        explanation.pack(anchor="w", pady=(4, 16))

        controls_card = ttk.Frame(frame, style="Card.TFrame", padding=14)
        controls_card.pack(fill="x", pady=(0, 14))

        slider_row = ttk.Frame(controls_card, style="Card.TFrame")
        slider_row.pack(fill="x")

        ttk.Label(slider_row, text="Crude oil price ($/barrel)", style="Section.TLabel").pack(side="left")
        slider = ttk.Scale(
            slider_row,
            from_=MIN_CRUDE_PRICE,
            to=MAX_CRUDE_PRICE,
            variable=self.crude_price,
            style="Accent.Horizontal.TScale",
            command=self._on_slider_change,
        )
        slider.pack(side="left", fill="x", expand=True, padx=12)

        self.crude_value_label = ttk.Label(slider_row, width=12, anchor="e", style="CrudeBadge.TLabel")
        self.crude_value_label.pack(side="left")

        input_row = ttk.Frame(controls_card, style="Card.TFrame")
        input_row.pack(fill="x", pady=(10, 0))

        ttk.Label(input_row, text="Or type a price", style="Body.TLabel").pack(side="left")
        self.crude_entry = ttk.Entry(input_row, textvariable=self.crude_price_entry, width=12)
        self.crude_entry.pack(side="left", padx=(10, 8))
        self.crude_entry.bind("<Return>", self._apply_manual_crude_price_event)
        self.crude_entry.bind("<FocusOut>", self._apply_manual_crude_price_event)

        ttk.Button(input_row, text="Apply", command=self.apply_manual_crude_price).pack(side="left")

        ttk.Label(
            controls_card,
            text="Tip: dependent values are shown in CPI units. Percent change compares against a $50-per-barrel baseline.",
            style="Body.TLabel",
        ).pack(anchor="w", pady=(8, 0))

        content_row = ttk.Frame(frame, style="App.TFrame")
        content_row.pack(fill="both", expand=True)
        content_row.columnconfigure(0, weight=1)
        content_row.rowconfigure(0, weight=1)

        self.notebook = ttk.Notebook(content_row)
        self.notebook.grid(row=0, column=0, sticky="nsew")

        self.summary_tab = ttk.Frame(self.notebook, style="Tab.TFrame", padding=6)
        self.trend_tab = ttk.Frame(self.notebook, style="Tab.TFrame", padding=6)
        self.notebook.add(self.summary_tab, text="Summary")
        self.notebook.add(self.trend_tab, text="Trend Graph")

        self.summary_tab.columnconfigure(0, weight=1)
        self.summary_tab.rowconfigure(0, weight=1)
        self.trend_tab.columnconfigure(0, weight=1)
        self.trend_tab.rowconfigure(0, weight=1)

        summary_card = ttk.Frame(self.summary_tab, style="Card.TFrame", padding=12)
        summary_card.grid(row=0, column=0, sticky="nsew")
        summary_card.columnconfigure(0, weight=1)
        summary_card.rowconfigure(2, weight=1)

        summary_header = ttk.Label(
            summary_card,
            text="Current model outputs",
            style="Section.TLabel",
        )
        summary_header.grid(row=0, column=0, sticky="w")

        boxes_frame = ttk.Frame(summary_card, style="Card.TFrame")
        boxes_frame.grid(row=1, column=0, sticky="nsew", pady=(12, 0))
        for column in range(2):
            boxes_frame.columnconfigure(column, weight=1)
        for row in range(2):
            boxes_frame.rowconfigure(row, weight=1)

        self.metric_cards: dict[str, dict[str, tk.StringVar]] = {}
        for index, name in enumerate(DEPENDENT_LABELS):
            row = index // 2
            column = index % 2
            card = ttk.Frame(boxes_frame, style="Card.TFrame", padding=16)
            card.grid(row=row, column=column, sticky="nsew", padx=8, pady=8)
            card.columnconfigure(0, weight=1)

            ttk.Label(card, text=name, style="BoxTitle.TLabel").grid(row=0, column=0, sticky="w")
            ttk.Label(card, textvariable=self.metric_value_vars[name], style="BoxValue.TLabel").grid(
                row=1, column=0, sticky="w", pady=(8, 2)
            )
            ttk.Label(card, textvariable=self.metric_change_vars[name], style="BoxChange.TLabel").grid(
                row=2, column=0, sticky="w"
            )

            self.metric_cards[name] = {
                "value": self.metric_value_vars[name],
                "change": self.metric_change_vars[name],
            }

        self.trend_canvas = tk.Canvas(
            self.trend_tab,
            width=860,
            height=500,
            bg="#fffef9",
            highlightthickness=0,
            bd=0,
        )
        self.trend_canvas.grid(row=0, column=0, sticky="nsew")

    def update_simulation(self) -> None:
        crude_price = round(self.crude_price.get(), 2)
        impacts = calculate_impacts(crude_price)
        baseline_impacts = calculate_impacts(BASELINE_CRUDE_PRICE)

        self.crude_value_label.configure(text=f"${impacts['Crude Oil']:.2f}")

        for name in DEPENDENT_LABELS:
            current_value = impacts[name]
            baseline_value = baseline_impacts[name]
            percent_change = self._percent_change(current_value, baseline_value)

            self.metric_value_vars[name].set(f"{current_value:,.2f} {VALUE_UNIT}")
            self.metric_change_vars[name].set(
                f"{percent_change:+.1f}% vs ${BASELINE_CRUDE_PRICE:.0f}/barrel"
            )

        self._draw_trend_graph()

    def _percent_change(self, current_value: float, baseline_value: float) -> float:
        if baseline_value == 0:
            return 0.0
        return ((current_value - baseline_value) / baseline_value) * 100

    def _draw_trend_graph(self) -> None:
        self.trend_canvas.delete("all")

        chart_left, chart_top = 68, 30
        chart_width, chart_height = 730, 380
        chart_right = chart_left + chart_width
        chart_bottom = chart_top + chart_height

        x_values = list(range(30, 201, 10))
        baseline_impacts = calculate_impacts(BASELINE_CRUDE_PRICE)
        trend_data = {
            label: [calculate_impacts(float(price))[label] for price in x_values]
            for label in DEPENDENT_LABELS
        }
        percent_change_data = {
            label: [self._percent_change(value, baseline_impacts[label]) for value in series]
            for label, series in trend_data.items()
        }
        y_values = [value for series in percent_change_data.values() for value in series]
        y_min = min(y_values)
        y_max = max(y_values)
        if y_min == y_max:
            y_max = y_min + 1

        def map_x(price: float) -> float:
            return chart_left + ((price - x_values[0]) / (x_values[-1] - x_values[0])) * chart_width

        def map_y(value: float) -> float:
            return chart_bottom - ((value - y_min) / (y_max - y_min)) * chart_height

        self.trend_canvas.create_text(
            chart_left,
            10,
            text="Dependent variable trends by crude oil price",
            fill=TITLE_COLOR,
            anchor="w",
            font=("Segoe UI", 12, "bold"),
        )
        self.trend_canvas.create_text(
            chart_left,
            26,
            text="X axis: crude oil ($/barrel)   |   Y axis: percent change from $50 baseline",
            fill=MUTED_TEXT,
            anchor="w",
            font=("Segoe UI", 9),
        )

        for i in range(6):
            y = chart_top + (i * chart_height / 5)
            self.trend_canvas.create_line(chart_left, y, chart_right, y, fill="#e9e2d4", width=1)

        for i in range(6):
            x = chart_left + (i * chart_width / 5)
            self.trend_canvas.create_line(x, chart_top, x, chart_bottom, fill="#f2ebe0", width=1)

        zero_y = map_y(0)
        self.trend_canvas.create_line(chart_left, zero_y, chart_right, zero_y, fill="#94a3b8", width=2)

        self.trend_canvas.create_line(chart_left, chart_bottom, chart_right, chart_bottom, fill="#b7ad97", width=2)
        self.trend_canvas.create_line(chart_left, chart_top, chart_left, chart_bottom, fill="#b7ad97", width=2)

        for i, price in enumerate(x_values[::2]):
            x = map_x(price)
            self.trend_canvas.create_text(
                x,
                chart_bottom + 16,
                text=f"${price}",
                fill=MUTED_TEXT,
                font=("Segoe UI", 8),
            )

        y_ticks = 5
        for i in range(y_ticks + 1):
            value = y_min + (i * (y_max - y_min) / y_ticks)
            y = map_y(value)
            self.trend_canvas.create_text(
                chart_left - 8,
                y,
                text=f"{value:+.0f}%",
                fill=MUTED_TEXT,
                anchor="e",
                font=("Segoe UI", 8),
            )

        for index, label in enumerate(DEPENDENT_LABELS):
            points: list[float] = []
            for price, value in zip(x_values, percent_change_data[label], strict=True):
                points.extend([map_x(float(price)), map_y(value)])

            self.trend_canvas.create_line(*points, fill=BAR_COLORS[index], width=3, smooth=True)
            last_x, last_y = points[-2], points[-1]
            self.trend_canvas.create_oval(last_x - 4, last_y - 4, last_x + 4, last_y + 4, fill=BAR_COLORS[index], outline="")

        legend_x = chart_right - 190
        legend_y = chart_top + 16
        self.trend_canvas.create_rectangle(
            legend_x - 12,
            legend_y - 12,
            legend_x + 178,
            legend_y + 88,
            fill="#fffdf8",
            outline="#e6dcc7",
        )
        for index, label in enumerate(DEPENDENT_LABELS):
            y = legend_y + (index * 20)
            self.trend_canvas.create_line(legend_x, y, legend_x + 22, y, fill=BAR_COLORS[index], width=3)
            self.trend_canvas.create_text(
                legend_x + 28,
                y,
                text=label,
                fill=TEXT_COLOR,
                anchor="w",
                font=("Segoe UI", 8, "bold"),
            )

        self.trend_canvas.create_text(
            chart_left,
            chart_bottom + 34,
            text="Each line shows its own percent change from the $50 baseline so the curves are directly comparable.",
            fill=MUTED_TEXT,
            anchor="w",
            font=("Segoe UI", 8),
        )

    def _on_slider_change(self, _value: str) -> None:
        self.crude_price_entry.set(f"{self.crude_price.get():.2f}")
        self.update_simulation()

    def _apply_manual_crude_price_event(self, _event: tk.Event | None = None) -> None:
        self.apply_manual_crude_price()

    def apply_manual_crude_price(self) -> None:
        try:
            value = float(self.crude_price_entry.get())
        except ValueError:
            self.crude_price_entry.set(f"{self.crude_price.get():.2f}")
            return

        value = max(MIN_CRUDE_PRICE, min(MAX_CRUDE_PRICE, value))
        self.crude_price.set(value)
        self.crude_price_entry.set(f"{value:.2f}")
        self.update_simulation()


def main() -> None:
    app = OilImpactApp()
    app.mainloop()


if __name__ == "__main__":
    main()
