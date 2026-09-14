import tkinter as tk


class TarjetaMetrica(tk.Frame):

    def __init__(
        self,
        parent,
        titulo,
        valor
    ):
        super().__init__(
            parent,
            bg="white",
            highlightbackground="#DCE3EC",
            highlightthickness=1,
        )

        tk.Label(
            self,
            text=titulo,
            bg="white",
            fg="#64748B",
            font=("Segoe UI", 9),
        ).pack(
            anchor="w",
            padx=15,
            pady=(15, 5)
        )

        tk.Label(
            self,
            text=str(valor),
            bg="white",
            fg="#1E293B",
            font=("Segoe UI", 20, "bold"),
        ).pack(
            anchor="w",
            padx=15,
            pady=(0, 15)
        )