import tkinter as tk
from tkinter import ttk


from impact_model import calculate_impacts


class OilImpactApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Crude Oil Price Impact Simulator")
        self.geometry("900x580")

        self.crude_price = tk.DoubleVar(value=80.0)
        self.output_vars = {
            "Transportation": tk.StringVar(),
            "Food Logistics": tk.StringVar(),
            "Flight Tickets": tk.StringVar(),
            "Household Energy": tk.StringVar(),
        }

        self._build_ui()
        self.update_simulation()

    def _build_ui(self) -> None:
        frame = ttk.Frame(self, padding=16)
        frame.pack(fill="both", expand=True)

        title = ttk.Label(
            frame,
            text="How crude oil prices affect everyday costs",
            font=("TkDefaultFont", 16, "bold"),
        )
        title.pack(anchor="w", pady=(0, 10))

        explanation = ttk.Label(
            frame,
            text=(
                "Move the slider to increase/decrease crude oil price per barrel. "
                "The chart and estimated dependent costs update instantly."
            ),
            wraplength=840,
        )
        explanation.pack(anchor="w", pady=(0, 12))

        slider_row = ttk.Frame(frame)
        slider_row.pack(fill="x", pady=(0, 14))

        ttk.Label(slider_row, text="Crude oil price ($/barrel):").pack(side="left")
        slider = ttk.Scale(
            slider_row,
            from_=30,
            to=200,
            variable=self.crude_price,
            command=lambda _v: self.update_simulation(),
        )
        slider.pack(side="left", fill="x", expand=True, padx=10)

        self.crude_value_label = ttk.Label(slider_row, width=12)
        self.crude_value_label.pack(side="left")

        self.canvas = tk.Canvas(frame, width=850, height=280, bg="white", highlightthickness=1)
        self.canvas.pack(fill="x", pady=(0, 12))

        values_frame = ttk.LabelFrame(frame, text="Estimated Cost Impact", padding=12)
        values_frame.pack(fill="x")

        for i, (name, value_var) in enumerate(self.output_vars.items()):
            ttk.Label(values_frame, text=name + ":", width=18).grid(row=i, column=0, sticky="w", padx=(0, 8), pady=3)
            ttk.Label(values_frame, textvariable=value_var, font=("TkDefaultFont", 10, "bold")).grid(
                row=i, column=1, sticky="w", pady=3
            )

    def update_simulation(self) -> None:
        impacts = calculate_impacts(round(self.crude_price.get(), 2))
        self.crude_value_label.configure(text=f"${impacts['Crude Oil']:.2f}")

        for name, var in self.output_vars.items():
            var.set(f"${impacts[name]:.2f}")

        self._draw_chart(impacts)

    def _draw_chart(self, impacts: dict[str, float]) -> None:
        self.canvas.delete("all")

        labels = [
            "Crude Oil",
            "Transportation",
            "Food Logistics",
            "Flight Tickets",
            "Household Energy",
        ]
        values = [impacts[key] for key in labels]

        chart_left, chart_top = 60, 20
        chart_width, chart_height = 760, 230
        bar_space = chart_width / len(values)
        bar_width = bar_space * 0.55

        max_value = max(values) if values else 1

        self.canvas.create_line(chart_left, chart_top + chart_height, chart_left + chart_width, chart_top + chart_height)

        colors = ["#3366cc", "#dc3912", "#ff9900", "#109618", "#990099"]

        for i, (label, value) in enumerate(zip(labels, values, strict=True)):
            x0 = chart_left + (i * bar_space) + (bar_space - bar_width) / 2
            x1 = x0 + bar_width
            bar_h = (value / max_value) * (chart_height - 20)
            y0 = chart_top + chart_height - bar_h
            y1 = chart_top + chart_height

            self.canvas.create_rectangle(x0, y0, x1, y1, fill=colors[i], outline="")
            self.canvas.create_text((x0 + x1) / 2, y0 - 10, text=f"${value:.1f}")
            self.canvas.create_text((x0 + x1) / 2, y1 + 15, text=label, width=120)


def main() -> None:
    app = OilImpactApp()
    app.mainloop()


if __name__ == "__main__":
    main()
