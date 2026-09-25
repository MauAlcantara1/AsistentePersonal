# main.py

import customtkinter as ctk
from core.configuracion.api_manager import obtener_api_key
from core.voice.texto_voz import SpeechToText
from gui.configuraciones.api_view import ApiConfigView
from gui.inicio.menu_view import MenuView
from gui.modo_clase.asistente_academico import ModoClaseMenuView
from gui.modo_clase.menu_apuntes import TomarApuntesView
from gui.configuraciones.boveda import Configuraciones

class AgnesApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Asistente Agnes")
        self.geometry("480x480")
        self.resizable(False, False)
        self.configure(fg_color="#161D2F")

        self.stt = SpeechToText()

        self.container = ctk.CTkFrame(self, fg_color="#161D2F", corner_radius=0)
        self.container.pack(fill="both", expand=True)

        self.vista_actual = None

        # Evaluamos la API al inicio
        if not obtener_api_key():
            self.navegar_a("api_config")
        else:
            self.navegar_a("menu_principal")

    def navegar_a(self, nombre_vista):
        """Manejador central de cambio de pantallas."""
        if self.vista_actual:
            self.vista_actual.destroy()

        if nombre_vista == "api_config":
            self.vista_actual = ApiConfigView(
                self.container, 
                on_success_callback=lambda: self.navegar_a("menu_principal")
            )
        elif nombre_vista == "menu_principal":
            # Pasamos self.stt Y TAMBIÉN self.navegar_a
            self.vista_actual = MenuView(
                self.container, 
                stt_engine=self.stt, 
                on_navigate=self.navegar_a
            )
        elif nombre_vista == "modo_clase":
            self.vista_actual = ModoClaseMenuView(
                self.container, 
                stt_engine=self.stt, 
                on_navigate=self.navegar_a
            )
        elif nombre_vista == "tomar_apuntes":
            self.vista_actual = TomarApuntesView(
                self.container,
                stt_engine=self.stt,
                on_navigate=self.navegar_a
            )

        elif nombre_vista == "configurar_boveda":
            self.vista_actual = Configuraciones(
                self.container,
                stt_engine=self.stt,
                on_navigate=self.navegar_a
            )

        self.vista_actual.pack(fill="both", expand=True)

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    app = AgnesApp()
    app.mainloop()