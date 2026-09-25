import customtkinter as ctk
import threading
import os
from core.configuracion.archivo_configuracion import cargar_configuracion
from core.configuracion.archivo_configuracion import configurar_boveda
from tkinter import filedialog


config = cargar_configuracion()

RUTA_BOVEDA = config["ruta_boveda"]
RUTA_NOTAS = os.path.join(RUTA_BOVEDA)

COLOR_BG = "#161D2F"
COLOR_CARD = "#1E293B"
COLOR_BORDE = "#334155"
COLOR_ACCENT = "#818CF8"
COLOR_MUTED = "#64748B"
COLOR_WARN = "#F59E0B"
COLOR_TERMINAL = "#0F172A"  


class Configuraciones(ctk.CTkFrame):
    def __init__(self, parent, stt_engine, on_navigate):
        super().__init__(parent, fg_color=COLOR_BG, corner_radius=0)
        self.stt = stt_engine
        self.on_navigate = on_navigate

        # ---------- Tarjeta principal ----------
        self.card = ctk.CTkFrame(
            self, fg_color=COLOR_CARD, corner_radius=15,
            border_width=1, border_color=COLOR_BORDE
        )
        self.card.pack(pady=20, padx=30, fill="both", expand=True)

        # ---------- Encabezado ----------
        self.lbl_titulo = ctk.CTkLabel(
            self.card, text="ASISTENTE ACADÉMICO Agnes",
            font=("Segoe UI", 18, "bold"), text_color=COLOR_ACCENT
        )
        self.lbl_titulo.pack(pady=(20, 2))

        self.lbl_subtitulo = ctk.CTkLabel(
            self.card, text="C O N F I G U R A C I Ó N   D E   B Ó V E D A",
            font=("Segoe UI", 10), text_color=COLOR_MUTED
        )
        self.lbl_subtitulo.pack(pady=(0, 15))

        self._separador()

        # ---------- Bloque: ruta actual ----------
        self.frame_ruta_actual = ctk.CTkFrame(self.card, fg_color="transparent")
        self.frame_ruta_actual.pack(fill="x", padx=20, pady=(10, 10))

        self.lbl_texto = ctk.CTkLabel(
            self.frame_ruta_actual, text="RUTA ACTUAL",
            font=("Segoe UI", 10, "bold"), text_color=COLOR_WARN
        )
        self.lbl_texto.pack(anchor="w")

        self.box_ruta = ctk.CTkFrame(
            self.frame_ruta_actual, fg_color=COLOR_TERMINAL, corner_radius=8,
            border_width=1, border_color=COLOR_BORDE
        )
        self.box_ruta.pack(fill="x", pady=(6, 0))

        self.lbl_ruta = ctk.CTkLabel(
            self.box_ruta, text=f"{RUTA_NOTAS}",
            font=("Consolas", 12), text_color=COLOR_WARN,
            wraplength=420, justify="left", anchor="w"
        )
        self.lbl_ruta.pack(fill="x", padx=12, pady=10)

        self._separador()

        # ---------- Bloque: selector de nueva ruta ----------
        self.frame_selector_wrap = ctk.CTkFrame(self.card, fg_color="transparent")
        self.frame_selector_wrap.pack(fill="x", padx=20, pady=(18, 5))

        self.lbl_selector = ctk.CTkLabel(
            self.frame_selector_wrap, text="NUEVA RUTA",
            font=("Segoe UI", 10, "bold"), text_color=COLOR_MUTED
        )
        self.lbl_selector.pack(anchor="w", pady=(0, 6))

        self.frame_selector = ctk.CTkFrame(self.frame_selector_wrap, fg_color="transparent")
        self.frame_selector.pack(fill="x")

        self.entry_ruta = ctk.CTkEntry(
            self.frame_selector,
            placeholder_text="Selecciona tu nueva ruta",
            fg_color=COLOR_TERMINAL, border_color=COLOR_BORDE,
            text_color=COLOR_ACCENT, font=("Consolas", 11)
        )
        self.entry_ruta.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.btn_examinar = ctk.CTkButton(
            self.frame_selector,
            text="Examinar...",
            width=100,
            fg_color=COLOR_ACCENT, hover_color="#6366F1",
            text_color="#0F172A", font=("Segoe UI", 11, "bold"),
            command=self.seleccionar_carpeta
        )
        self.btn_examinar.pack(side="left")

        # ---------- Bloque: estado (indicador tipo HUD) ----------
        self.frame_estado = ctk.CTkFrame(self.card, fg_color="transparent")
        self.frame_estado.pack(pady=(18, 20))

        self.dot_estado = ctk.CTkLabel(
            self.frame_estado, text="●", font=("Segoe UI", 12),
            text_color=COLOR_MUTED, width=15
        )
        self.dot_estado.pack(side="left")

        self.lbl_estado = ctk.CTkLabel(
            self.frame_estado, text="En espera",
            font=("Segoe UI", 11), text_color=COLOR_MUTED
        )
        self.lbl_estado.pack(side="left")
        
        self.btn_regresar = ctk.CTkButton(
            self.card, text="Volver al Menú Principal", font=("Segoe UI", 12, "bold"),
            fg_color="#EF4444", hover_color="#B91C1C", corner_radius=8,
            command=self._regresar
        )
        self.btn_regresar.pack(pady=5, fill="x", padx=20)

        self.btn_regresar_anterior = ctk.CTkButton(
            self.card, text="Volver al Menú Anterior", font=("Segoe UI", 12, "bold"),
            fg_color="#EF4444", hover_color="#B91C1C", corner_radius=8,
            command=self._regresar_anteior
        )
        self.btn_regresar_anterior.pack(pady=5, fill="x", padx=20)


    def _separador(self):
        """Línea delgada tipo HUD para dividir secciones."""
        linea = ctk.CTkFrame(self.card, fg_color=COLOR_BORDE, height=1)
        linea.pack(fill="x", padx=20)

    def seleccionar_carpeta(self):
        directorio = filedialog.askdirectory(title="Selecciona la nueva ruta")

        if not directorio:
            return

        self.entry_ruta.configure(state="normal")
        self.entry_ruta.delete(0, "end")
        self.entry_ruta.insert(0, directorio)
        self.entry_ruta.configure(state="readonly")

        self._set_estado("Actualizando...", COLOR_WARN)

        def actualizar_label(texto):
            self.after(0, lambda: self._set_estado(texto, COLOR_ACCENT))

        def tarea():
            configurar_boveda(directorio, status_callback=actualizar_label)

        threading.Thread(target=tarea, daemon=True).start()

    def _set_estado(self, texto, color):
        self.dot_estado.configure(text_color=color)
        self.lbl_estado.configure(text=texto, text_color=color)

    def _regresar(self):
        self.on_navigate("menu_principal")
    
    def _regresar_anteior(self):
        self.on_navigate("modo_clase")