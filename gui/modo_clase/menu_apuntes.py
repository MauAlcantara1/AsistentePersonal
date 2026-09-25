import os
import customtkinter as ctk
import threading
from core.tareas.modo_clase import (
    obtener_carpetas_disponibles,
    crear_carpeta_fisica,
    procesar_y_guardar_nota_gui,
    guardar_estado_temporal,
    leer_estado_temporal,
    eliminar_estado_temporal
)
from core.prompts.academico import obtener_lista_materias_db


class TomarApuntesView(ctk.CTkFrame):
    def __init__(self, parent, stt_engine, on_navigate):
        super().__init__(parent, fg_color="#161D2F", corner_radius=0)
        self.stt = stt_engine
        self.on_navigate = on_navigate

        # Variables de estado internas
        self.carpeta_seleccionada = None
        self.materia_seleccionada = None
        self.grabando = False
        self.pausado = False

        # Tarjeta contenedor principal
        self.card = ctk.CTkFrame(self, fg_color="#1E293B", corner_radius=15, border_width=1, border_color="#334155")
        self.card.pack(pady=20, padx=25, fill="both", expand=True)

        self.lbl_titulo = ctk.CTkLabel(
            self.card, text="✦ TOMA DE APUNTES ✦", font=("Segoe UI", 18, "bold"), text_color="#818CF8"
        )
        self.lbl_titulo.pack(pady=(15, 5))

        # ==========================================
        # PASO 1: PANEL DE CONFIGURACIÓN PREVIA
        # ==========================================
        self.panel_paso1 = ctk.CTkFrame(self.card, fg_color="transparent")
        self.panel_paso1.pack(fill="both", expand=True, padx=15)

        # 1. Selector de Carpeta de Bóveda
        self.lbl_carpeta = ctk.CTkLabel(self.panel_paso1, text="Carpeta de Bóveda:", font=("Segoe UI", 11), text_color="#94A3B8")
        self.lbl_carpeta.pack(anchor="w", padx=20, pady=(5, 0))

        self.frame_carpeta_controls = ctk.CTkFrame(self.panel_paso1, fg_color="transparent")
        self.frame_carpeta_controls.pack(pady=(0, 10))

        self.combo_carpeta = ctk.CTkOptionMenu(
            self.frame_carpeta_controls, 
            values=["Cargando..."], 
            width=220, fg_color="#0F172A"
        )
        self.combo_carpeta.pack(side="left", padx=(0, 5))

        self.btn_nueva_carpeta = ctk.CTkButton(
            self.frame_carpeta_controls, text="+", width=30, 
            fg_color="#2563EB", hover_color="#1D4ED8",
            command=self._crear_nueva_carpeta_dialog
        )
        self.btn_nueva_carpeta.pack(side="left")

        # 2. Selector de Materia desde PostgreSQL
        self.lbl_materia = ctk.CTkLabel(self.panel_paso1, text="Materia o Asignatura:", font=("Segoe UI", 11), text_color="#94A3B8")
        self.lbl_materia.pack(anchor="w", padx=20, pady=(5, 0))

        materias_db = obtener_lista_materias_db()

        self.combo_materia = ctk.CTkOptionMenu(
            self.panel_paso1,
            values=materias_db if materias_db else ["General"],
            width=260,
            fg_color="#0F172A"
        )
        self.combo_materia.pack(pady=(0, 5))

        self.txt_nueva_materia = ctk.CTkEntry(
            self.panel_paso1, 
            placeholder_text="O escribe aquí si es una materia nueva...", 
            width=260, 
            fg_color="#0F172A"
        )
        self.txt_nueva_materia.pack(pady=(0, 10))

        self.btn_ir_paso2 = ctk.CTkButton(
            self.panel_paso1, text="Continuar a Grabación ➔", 
            font=("Segoe UI", 12, "bold"), fg_color="#2563EB", hover_color="#1D4ED8",
            command=self._transicion_a_paso2
        )
        self.btn_ir_paso2.pack(pady=10)

        # ==========================================
        # PASO 2: PANEL DE GRABACIÓN ACTIVA
        # ==========================================
        self.panel_paso2 = ctk.CTkFrame(self.card, fg_color="transparent")

        self.lbl_indicador_grabando = ctk.CTkLabel(
            self.panel_paso2, text="● GRABANDO CLASE", font=("Segoe UI", 14, "bold"), text_color="#EF4444"
        )
        self.lbl_indicador_grabando.pack(pady=10)

        self.txt_transcripcion_vovo = ctk.CTkTextbox(self.panel_paso2, width=320, height=120, fg_color="#0F172A")
        self.txt_transcripcion_vovo.pack(pady=10)

        self.frame_audio_controls = ctk.CTkFrame(self.panel_paso2, fg_color="transparent")
        self.frame_audio_controls.pack(pady=10)

        self.btn_pausa = ctk.CTkButton(
            self.frame_audio_controls, text="Pausar", width=100,
            fg_color="#F59E0B", hover_color="#D97706",
            command=self._toggle_pausa
        )
        self.btn_pausa.pack(side="left", padx=5)

        self.btn_detener = ctk.CTkButton(
            self.frame_audio_controls, text="Detener y Guardar", width=140,
            fg_color="#EF4444", hover_color="#B91C1C",
            command=self._detener_y_procesar
        )
        self.btn_detener.pack(side="left", padx=5)

        # ==========================================
        # PASO 3: PANEL DE RESULTADO
        # ==========================================
        self.panel_paso3 = ctk.CTkFrame(self.card, fg_color="transparent")

        self.lbl_estado_final = ctk.CTkLabel(
            self.panel_paso3, text="Sintetizando apunte con Gemini...", 
            font=("Segoe UI", 13, "italic"), text_color="#818CF8"
        )
        self.lbl_estado_final.pack(pady=30)

        self.btn_finalizar = ctk.CTkButton(
            self.panel_paso3, text="Volver al Menú", 
            fg_color="#2563EB", hover_color="#1D4ED8",
            command=lambda: self.on_navigate("modo_clase")
        )

        self._cargar_carpetas_iniciales()

    # ==========================================
    # LÓGICA DE CONTROL Y NAVEGACIÓN
    # ==========================================

    def _cargar_carpetas_iniciales(self):
        carpetas = obtener_carpetas_disponibles()
        if carpetas:
            self.combo_carpeta.configure(values=carpetas)
            self.combo_carpeta.set(carpetas[0])
        else:
            self.combo_carpeta.configure(values=["Sin carpetas"])
            self.combo_carpeta.set("Sin carpetas")

    def _crear_nueva_carpeta_dialog(self):
        dialog = ctk.CTkInputDialog(text="Ingresa el nombre de la nueva carpeta:", title="Nueva Carpeta")
        nombre_nueva = dialog.get_input()
        
        if nombre_nueva and nombre_nueva.strip():
            exito, msg = crear_carpeta_fisica(nombre_nueva)
            if exito:
                self._cargar_carpetas_iniciales()
                self.combo_carpeta.set(nombre_nueva.strip())
            else:
                print(f"[Sistema]: {msg}")

    def _transicion_a_paso2(self):
        materia_nueva = self.txt_nueva_materia.get().strip()
        
        if materia_nueva:
            self.materia_seleccionada = materia_nueva
        else:
            self.materia_seleccionada = self.combo_materia.get()

        self.carpeta_seleccionada = self.combo_carpeta.get()

        # Limpiar cualquier respaldo temporal previo
        eliminar_estado_temporal()

        self.panel_paso1.pack_forget()
        self.panel_paso2.pack(fill="both", expand=True, padx=15)

        self.grabando = True
        self.pausado = False
        threading.Thread(target=self._hilo_grabacion_core, daemon=True).start()

    def _toggle_pausa(self):
        self.pausado = not self.pausado
        if self.pausado:
            self.btn_pausa.configure(text="Reanudar", fg_color="#2563EB", hover_color="#1D4ED8")
            self.lbl_indicador_grabando.configure(text="⏸ GRABACIÓN PAUSADA", text_color="#F59E0B")
        else:
            self.btn_pausa.configure(text="Pausar", fg_color="#F59E0B", hover_color="#D97706")
            self.lbl_indicador_grabando.configure(text="● GRABANDO CLASE", text_color="#EF4444")

    def _detener_y_procesar(self):
        self.grabando = False
        
        self.lbl_estado_final.configure(
            text=f"Sintetizando apunte de '{self.materia_seleccionada}' con Gemini...",
            text_color="#818CF8"
        )
        self.btn_finalizar.pack_forget()

        self.panel_paso2.pack_forget()
        self.panel_paso3.pack(fill="both", expand=True, padx=15)
        
        threading.Thread(target=self._hilo_guardado_core, daemon=True).start()

    def _hilo_grabacion_core(self):
        """Bucle en segundo plano para capturar audio y actualizar el JSON temporal."""
        texto_acumulado = ""
        while self.grabando:
            if self.pausado:
                continue
            
            texto = self.stt.listen()
            if texto and self.grabando and not self.pausado:
                texto_acumulado += texto + " "
                
                # Guarda continuamente transcripción + carpeta + materia en JSON
                guardar_estado_temporal(
                    self.carpeta_seleccionada, 
                    self.materia_seleccionada, 
                    texto_acumulado.strip()
                )
                
                self.after(0, lambda t=texto: self._append_texto_transcripcion(t))

    def _append_texto_transcripcion(self, texto):
        self.txt_transcripcion_vovo.insert("end", texto + " ")
        self.txt_transcripcion_vovo.see("end")

    def _hilo_guardado_core(self):
        """Procesa la nota con Gemini a partir del archivo JSON respaldado."""
        datos = leer_estado_temporal()
        
        if not datos or not datos.get("transcripcion", "").strip():
            self.after(0, lambda: self._mostrar_resultado_final(
                "No se detectó texto grabado. Proceso cancelado.", 
                "#EF4444"
            ))
            return

        texto_total = datos["transcripcion"].strip()
        materia = datos.get("materia", self.materia_seleccionada)
        carpeta = datos.get("carpeta", self.carpeta_seleccionada)

        try:
            ruta_final = procesar_y_guardar_nota_gui(
                texto_total, 
                carpeta, 
                materia
            )
            
            msg = (
                f"¡Apunte procesado con éxito por Gemini! ✨\n\n"
                f"Materia: {materia.title()}\n"
                f"Ubicación:\n{ruta_final}"
            )
            self.after(0, lambda: self._mostrar_resultado_final(msg, "#10B981"))

        except Exception as e:
            msg = (
                f"[ERROR]: Falló el procesamiento con Gemini.\n"
                f"Tu nota está resguardada en el archivo temporal para reintentar más tarde."
            )
            self.after(0, lambda: self._mostrar_resultado_final(msg, "#EF4444"))

    def _mostrar_resultado_final(self, mensaje, color):
        self.lbl_estado_final.configure(text=mensaje, text_color=color)
        self.btn_finalizar.pack(pady=20)