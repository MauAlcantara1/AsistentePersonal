import customtkinter as ctk
import threading
from core.tareas.modo_clase import recuperar_nota, configurar_boveda
from core.tareas.modo_exposicion import inicio

class ModoClaseMenuView(ctk.CTkFrame):
    def __init__(self, parent, stt_engine, on_navigate):
        super().__init__(parent, fg_color="#161D2F", corner_radius=0)
        self.stt = stt_engine
        self.on_navigate = on_navigate

        self.card = ctk.CTkFrame(self, fg_color="#1E293B", corner_radius=15, border_width=1, border_color="#334155")
        self.card.pack(pady=20, padx=30, fill="both", expand=True)

        self.lbl_titulo = ctk.CTkLabel(
            self.card, text="Asistente Académico Agnes", font=("Segoe UI", 18, "bold"), text_color="#818CF8"
        )
        self.lbl_titulo.pack(pady=(15, 5))

        self.lbl_subtitulo = ctk.CTkLabel(
            self.card, text="Selecciona un modo de operación", font=("Segoe UI", 11), text_color="#64748B"
        )
        self.lbl_subtitulo.pack(pady=(0, 10))

        # Opción 1: Iniciar apuntes
        self.btn_apuntes = ctk.CTkButton(
            self.card, text="1. Tomar apuntes de clase", font=("Segoe UI", 12, "bold"),
            fg_color="#2563EB", hover_color="#1D4ED8", corner_radius=8,
            command=self._iniciar_tomar_apuntes
        )
        self.btn_apuntes.pack(pady=6, fill="x", padx=30)

        # Opción 2: Recuperar nota
        self.btn_recuperar = ctk.CTkButton(
            self.card, text="2. Recuperar nota pendiente", font=("Segoe UI", 12, "bold"),
            fg_color="#0D9488", hover_color="#0F766E", corner_radius=8,
            command=self._reintentar_nota_pendiente
        )
        self.btn_recuperar.pack(pady=6, fill="x", padx=30)

        # Opción 3: Exposición
        self.btn_expo = ctk.CTkButton(
            self.card, text="3. Modo Exposición", font=("Segoe UI", 12, "bold"),
            fg_color="#2563EB", hover_color="#1D4ED8", corner_radius=8,
            command=self._asistente_exposicion
        )
        self.btn_expo.pack(pady=6, fill="x", padx=30)

        # Opción 4: Configurar Bóveda
        self.btn_boveda = ctk.CTkButton(
            self.card, text="4. Configurar Bóveda Obsidian", font=("Segoe UI", 12, "bold"),
            fg_color="#2563EB", hover_color="#1D4ED8", corner_radius=8,
            command=self._configuracion_boveda
        )
        self.btn_boveda.pack(pady=6, fill="x", padx=30)

        # Opción 5: Regresar al menú principal
        self.btn_regresar = ctk.CTkButton(
            self.card, text="5. Volver al Menú Principal", font=("Segoe UI", 12, "bold"),
            fg_color="#EF4444", hover_color="#B91C1C", corner_radius=8,
            command=self._regresar
        )
        self.btn_regresar.pack(pady=6, fill="x", padx=30)

        self.lbl_estado = ctk.CTkLabel(
            self.card, text="Agnes lista para ayudarte", font=("Segoe UI", 15, "italic"), text_color="#F59E0B"
        )
        self.lbl_estado.pack(pady=(10, 10))

    def _iniciar_tomar_apuntes(self):
        self.on_navigate("tomar_apuntes")

    def _reintentar_nota_pendiente(self):
        # Callback para actualizar el estado en tiempo real dentro del hilo principal de CustomTkinter
        def actualizar_label(texto):
            color = "#EF4444" if "ERROR" in texto or "vacío" in texto or "No se encontró" in texto else "#10B981"
            if "Sintetizando" in texto or "Localizando" in texto:
                color = "#818CF8"
            
            self.after(0, lambda: self.lbl_estado.configure(text=texto, text_color=color))

        # Notificación inicial
        self.lbl_estado.configure(text="Iniciando recuperación...", text_color="#818CF8")

        # Ejecutamos la tarea en segundo plano sin congelar la GUI
        threading.Thread(
            target=recuperar_nota,
            kwargs={"status_callback": actualizar_label},
            daemon=True
        ).start()

    def _asistente_exposicion(self):
        self.lbl_estado.configure(text="Asistente de exposición activo...", text_color="#818CF8")
        threading.Thread(target=self._run_task, args=(inicio,), daemon=True).start()

    def _configuracion_boveda(self):
        self.on_navigate("configurar_boveda")

    def _regresar(self):
        self.on_navigate("menu_principal")

    def _run_task(self, func):
        func()
        self.after(0, lambda: self.lbl_estado.configure(text="Agnes lista para ayudarte", text_color="#F59E0B"))