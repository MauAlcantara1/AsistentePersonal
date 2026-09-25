import customtkinter as ctk
from tkinter import filedialog

class ConfiguracionBoveda(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Título de la sección
        self.label_titulo = ctk.CTkLabel(
            self, 
            text="Ubicación de la Bóveda", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.label_titulo.pack(pady=(10, 5), padx=10, anchor="w")

        # Contenedor horizontal para el cuadro de texto y el botón
        self.frame_selector = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_selector.pack(fill="x", padx=10, pady=5)

        # Entrada de texto (deshabilitada para evitar edición manual errónea)
        self.entry_ruta = ctk.CTkEntry(
            self.frame_selector, 
            placeholder_text="Ninguna carpeta seleccionada...",
            width=300
        )
        self.entry_ruta.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Botón para examinar/buscar
        self.btn_examinar = ctk.CTkButton(
            self.frame_selector, 
            text="Examinar...", 
            width=100,
            command=self.seleccionar_carpeta
        )
        self.btn_examinar.pack(side="right")

    def seleccionar_carpeta(self):
        # Abre el diálogo nativo del sistema para elegir carpeta
        directorio = filedialog.askdirectory(title="Seleccionar carpeta de la Bóveda")
        
        if directorio:
            # Actualiza el campo de texto con la ruta seleccionada
            self.entry_ruta.configure(state="normal") # Habilita para escribir
            self.entry_ruta.delete(0, "end")
            self.entry_ruta.insert(0, directorio)
            self.entry_ruta.configure(state="readonly") # Bloquea para lectura únicamente

# --- Ejemplo de uso directo ---
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = ctk.CTk()
    app.geometry("500x200")
    app.title("Configuración")

    vista = ConfiguracionBoveda(app)
    vista.pack(fill="both", expand=True, padx=20, pady=20)

    app.mainloop()