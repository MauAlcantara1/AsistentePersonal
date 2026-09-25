import customtkinter as ctk
from core.configuracion.api_manager import guardar_api_key

class ApiConfigView(ctk.CTkFrame):
    def __init__(self, parent, on_success_callback):
        # Fondo temático azul nocturno
        super().__init__(parent, fg_color="#161D2F", corner_radius=0)
        self.on_success = on_success_callback

        # Tarjeta central con estética de Agnes
        self.card = ctk.CTkFrame(self, fg_color="#1E293B", corner_radius=15, border_width=1, border_color="#334155")
        self.card.pack(pady=30, padx=30, fill="both", expand=True)

        # Encabezado con detalles dorados y azules celestes
        self.lbl_titulo = ctk.CTkLabel(
            self.card, 
            text="★ Agnes AI ★", 
            font=("Segoe UI", 20, "bold"),
            text_color="#F59E0B"
        )
        self.lbl_titulo.pack(pady=(25, 5))

        self.lbl_subtitulo = ctk.CTkLabel(
            self.card, 
            text="Configuración Inicial de Sistema", 
            font=("Segoe UI", 12),
            text_color="#818CF8"
        )
        self.lbl_subtitulo.pack(pady=(0, 15))

        self.lbl_instruccion = ctk.CTkLabel(
            self.card, 
            text="No se encontró una API Key de Gemini válida.\nIngresa tu clave para sincronizar con Agnes:",
            font=("Segoe UI", 11),
            text_color="#94A3B8"
        )
        self.lbl_instruccion.pack(pady=10)

        # Campo de entrada azul oscuro con borde dorado al enfocar
        self.txt_api = ctk.CTkEntry(
            self.card, 
            placeholder_text="AIzaSy...", 
            width=280, 
            show="*",
            fg_color="#0F172A",
            text_color="#F8FAFC",
            border_color="#334155",
            border_width=1
        )
        self.txt_api.pack(pady=10)

        self.lbl_error = ctk.CTkLabel(self.card, text="", font=("Segoe UI", 11), text_color="#F87171")
        self.lbl_error.pack(pady=2)

        # Botón primario azul vestimenta
        self.btn_guardar = ctk.CTkButton(
            self.card, 
            text="Guardar y Conectar", 
            font=("Segoe UI", 13, "bold"),
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            text_color="#FFFFFF",
            corner_radius=8,
            command=self._guardar
        )
        self.btn_guardar.pack(pady=(15, 25))

    def _guardar(self):
        key = self.txt_api.get().strip()
        if not key:
            self.lbl_error.configure(text="La API Key no puede estar vacía.")
            return

        guardar_api_key(key)
        self.on_success()