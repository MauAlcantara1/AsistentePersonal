import customtkinter as ctk
import threading
from core.tareas.modulo_asistente import inicio_uno

class MenuView(ctk.CTkFrame):
    def __init__(self, parent, stt_engine, on_navigate):
        super().__init__(parent, fg_color="#161D2F", corner_radius=0)
        self.stt = stt_engine
        self.on_navigate = on_navigate  # Callback para cambiar de vista

        self.card = ctk.CTkFrame(self, fg_color="#1E293B", corner_radius=15, border_width=1, border_color="#334155")
        self.card.pack(pady=25, padx=30, fill="both", expand=True)

        self.lbl_titulo = ctk.CTkLabel(
            self.card, text="Asistente Agnes", font=("Segoe UI", 18, "bold"), text_color="#818CF8"
        )
        self.lbl_titulo.pack(pady=(20, 5))

        self.lbl_subtitulo = ctk.CTkLabel(
            self.card, text="Selecciona un modo de operación", font=("Segoe UI", 11), text_color="#64748B"
        )
        self.lbl_subtitulo.pack(pady=(0, 15))

        # Opción 1: Ir a Submenú Académico
        self.btn_clase = ctk.CTkButton(
            self.card, 
            text="1. Modo Clase (Grabación)", 
            font=("Segoe UI", 12, "bold"),
            fg_color="#2563EB", hover_color="#1D4ED8", corner_radius=8,
            command=self._ir_a_modo_clase
        )
        self.btn_clase.pack(pady=8, fill="x", padx=30)

        # Opción 2: Asistente Personal
        self.btn_asistente = ctk.CTkButton(
            self.card, 
            text="2. Asistente Personal", 
            font=("Segoe UI", 12, "bold"),
            fg_color="#0D9488", hover_color="#0F766E", corner_radius=8,
            command=self._ejecutar_asistente_personal
        )
        self.btn_asistente.pack(pady=8, fill="x", padx=30)

        # Opción 3: Salir
        self.btn_salir = ctk.CTkButton(
            self.card, 
            text="3. Salir", 
            font=("Segoe UI", 12, "bold"),
            fg_color="#EF4444", hover_color="#B91C1C", corner_radius=8,
            command=self.master.destroy
        )
        self.btn_salir.pack(pady=8, fill="x", padx=30)

        self.lbl_estado = ctk.CTkLabel(
            self.card, text="Agnes lista para ayudarte", font=("Segoe UI", 11, "italic"), text_color="#F59E0B"
        )
        self.lbl_estado.pack(pady=(15, 10))

    def _ir_a_modo_clase(self):
        # Llama a main.py para cambiar la pantalla
        self.on_navigate("modo_clase")

    def _ejecutar_asistente_personal(self):
        self.lbl_estado.configure(text="Asistente personal en ejecución...", text_color="#818CF8")
        threading.Thread(target=self._run_task, args=(inicio_uno,), daemon=True).start()

    def _run_task(self, func):
        func()
        self.after(0, lambda: self.lbl_estado.configure(text="Agnes lista para ayudarte", text_color="#F59E0B"))