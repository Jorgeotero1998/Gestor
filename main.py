import customtkinter as ctk
import json
import os
import shutil
from datetime import datetime

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class Gestor(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Gestor")
        self.geometry("1100x750")
        
        self.archivo = "datos.json"
        self.backup = "datos_backup.json"
        self.tareas = self.cargar_datos()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar()
        self.main_panel()
        self.refrescar()

    def sidebar(self):
        self.side = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.side.grid(row=0, column=0, sticky="nsew")
        
        self.lbl_titulo = ctk.CTkLabel(self.side, text="Gestor", font=("Segoe UI", 24, "bold"))
        self.lbl_titulo.pack(pady=40)

        self.btn_export = ctk.CTkButton(self.side, text="Exportar Reporte", fg_color="#28a745", hover_color="#218838", command=self.exportar_reporte)
        self.btn_export.pack(pady=10, padx=20)

        self.total_lbl = ctk.CTkLabel(self.side, text="Pendientes: 0", font=("Segoe UI", 13))
        self.total_lbl.pack(pady=10)

        self.progreso = ctk.CTkProgressBar(self.side, width=170)
        self.progreso.pack(pady=10)
        
        self.btn_tema = ctk.CTkButton(self.side, text="Alternar Tema", command=self.alternar_tema, fg_color="#333333")
        self.btn_tema.pack(side="bottom", pady=30, padx=20)

    def main_panel(self):
        self.area = ctk.CTkFrame(self, fg_color="transparent")
        self.area.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        self.area.grid_columnconfigure(0, weight=1)
        self.area.grid_rowconfigure(2, weight=1)

        self.buscador = ctk.CTkEntry(self.area, placeholder_text="🔍 Filtrar tareas...", height=45)
        self.buscador.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        self.buscador.bind("<KeyRelease>", lambda e: self.refrescar())

        self.input_box = ctk.CTkFrame(self.area, fg_color="#1e1e1e", corner_radius=12)
        self.input_box.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        self.txt_input = ctk.CTkEntry(self.input_box, placeholder_text="¿Nuevo objetivo?", border_width=0, height=50)
        self.txt_input.pack(side="left", fill="x", expand=True, padx=20, pady=15)
        self.txt_input.bind("<Return>", lambda e: self.add())

        self.opt_prio = ctk.CTkOptionMenu(self.input_box, values=["Baja", "Media", "Alta"], width=110)
        self.opt_prio.set("Media")
        self.opt_prio.pack(side="left", padx=10)

        self.btn_add = ctk.CTkButton(self.input_box, text="+", width=50, height=45, command=self.add)
        self.btn_add.pack(side="left", padx=15)

        self.scroll = ctk.CTkScrollableFrame(self.area, label_text="Tareas Registradas")
        self.scroll.grid(row=2, column=0, sticky="nsew")
        self.scroll.grid_columnconfigure(0, weight=1)

    def cargar_datos(self):
        if os.path.exists(self.archivo):
            try:
                with open(self.archivo, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: return []
        return []

    def guardar_datos(self):
        with open(self.archivo, "w", encoding="utf-8") as f:
            json.dump(self.tareas, f, indent=4)
        shutil.copy(self.archivo, self.backup)

    def exportar_reporte(self):
        with open("Reporte_Gestor.txt", "w", encoding="utf-8") as f:
            f.write(f"REPORTE GESTOR - {datetime.now().strftime('%d/%m/%Y')}\n")
            f.write("-" * 50 + "\n")
            for t in self.tareas:
                estado = "[OK]" if t['s'] == "Hecho" else "[..]"
                f.write(f"{estado} ({t['p']}) {t['t']} - Creado: {t['f']}\n")
        os.startfile("Reporte_Gestor.txt")

    def add(self):
        t = self.txt_input.get()
        if t:
            self.tareas.append({"t": t, "p": self.opt_prio.get(), "s": "Pendiente", "f": datetime.now().strftime("%d/%m %H:%M")})
            self.guardar_datos()
            self.txt_input.delete(0, 'end')
            self.refrescar()

    def refrescar(self):
        for w in self.scroll.winfo_children(): w.destroy()
        filtro = self.buscador.get().lower()
        colores_prio = {"Alta": "#ff4d4d", "Media": "#ffaa00", "Baja": "#3399ff"}
        colores_estado = {"Pendiente": "#777777", "En Proceso": "#3b8ed0", "Hecho": "#28a745"}

        self.tareas.sort(key=lambda x: (x.get("s") == "Hecho", ["Alta", "Media", "Baja"].index(x.get("p", "Media"))))

        p_count = 0
        for i, t in enumerate(self.tareas):
            if filtro in t['t'].lower():
                item = ctk.CTkFrame(self.scroll, fg_color="#262626", height=70)
                item.pack(fill="x", pady=5, padx=5)
                
                info = ctk.CTkFrame(item, fg_color="transparent")
                info.pack(side="left", fill="both", expand=True, padx=20)
                
                ctk.CTkLabel(info, text=t['t'], font=("Segoe UI", 14, "bold"), text_color=colores_prio.get(t['p'], "white")).pack(anchor="w", pady=(8,0))
                ctk.CTkLabel(info, text=f"{t['f']} | {t['p']}", font=("Segoe UI", 10), text_color="gray").pack(anchor="w", pady=(0,8))

                menu = ctk.CTkOptionMenu(item, values=["Pendiente", "En Proceso", "Hecho"], 
                                         command=lambda v, idx=i: self.cambiar_estado(idx, v),
                                         fg_color=colores_estado.get(t['s'], "#777777"), width=120)
                menu.set(t['s'])
                menu.pack(side="right", padx=15)
                
                if t['s'] != "Hecho": p_count += 1

        self.total_lbl.configure(text=f"Pendientes: {p_count}")
        prog = (sum(1 for t in self.tareas if t['s'] == "Hecho") / len(self.tareas)) if self.tareas else 0
        self.progreso.set(prog)

    def cambiar_estado(self, i, v):
        self.tareas[i]["s"] = v
        self.guardar_datos()
        self.refrescar()

    def alternar_tema(self):
        m = "light" if ctk.get_appearance_mode() == "Dark" else "dark"
        ctk.set_appearance_mode(m)

if __name__ == "__main__":
    app = Gestor()
    app.mainloop()
