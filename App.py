import customtkinter as ctk
import tkinter as tk
from tkinter import simpledialog

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class EditorGrafos(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Editor de Grafos Interactivo (MST)")
        self.geometry("1200x800")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- BARRA DE HERRAMIENTAS ---
        self.toolbar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.toolbar.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(self.toolbar, text="Herramientas", font=("Arial", 20, "bold")).pack(pady=20)

        self.modo_actual = "NODO" 

        # Botones de Edición
        self.btn_nodo = ctk.CTkButton(self.toolbar, text="🔵 Crear Nodo", fg_color="#3B8ED0", 
                                      command=lambda: self.cambiar_modo("NODO"))
        self.btn_nodo.pack(pady=10, padx=20)

        self.btn_conectar = ctk.CTkButton(self.toolbar, text="🔗 Conectar", fg_color="gray", 
                                          command=lambda: self.cambiar_modo("CONECTAR"))
        self.btn_conectar.pack(pady=10, padx=20)

        self.btn_mover = ctk.CTkButton(self.toolbar, text="✋ Mover", fg_color="gray", 
                                       command=lambda: self.cambiar_modo("MOVER"))
        self.btn_mover.pack(pady=10, padx=20)
        
        # Botón Limpiar
        ctk.CTkButton(self.toolbar, text="🗑️ Limpiar Todo", fg_color="#C0392B", 
                      command=self.limpiar_todo).pack(pady=20, padx=20)

        self.lbl_info = ctk.CTkLabel(self.toolbar, text="Click para crear nodos.", text_color="gray")
        self.lbl_info.pack(side="bottom", pady=20)

        # --- LIENZO ---
        self.canvas = tk.Canvas(self, bg="white", highlightthickness=0)
        self.canvas.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # --- LÓGICA DE DATOS ---
        self.nodos = []   
        self.aristas = [] 
        self.contador_nodos = 0
        
        # Variables de estado
        self.nodo_seleccionado = None     
        self.nodo_origen_conexion = None  

        # Eventos
        self.canvas.bind("<Button-1>", self.al_hacer_click)
        self.canvas.bind("<B1-Motion>", self.al_arrastrar)
        self.canvas.bind("<ButtonRelease-1>", self.al_soltar)

    def cambiar_modo(self, nuevo_modo):
        self.modo_actual = nuevo_modo
        self.nodo_origen_conexion = None 
        self.restaurar_colores_nodos()   

        btn_activos = {"NODO": self.btn_nodo, "CONECTAR": self.btn_conectar, "MOVER": self.btn_mover}
        colores = {"NODO": "#3B8ED0", "CONECTAR": "#E59113", "MOVER": "#2CC985"}

        for modo, btn in btn_activos.items():
            if modo == nuevo_modo:
                btn.configure(fg_color=colores[modo])
            else:
                btn.configure(fg_color="gray")
        
        msgs = {
            "NODO": "Click en espacio vacío\npara crear nodo.",
            "CONECTAR": "Click en Nodo A (Origen)\nluego en Nodo B (Destino).",
            "MOVER": "Arrastra los nodos para\nacomodarlos."
        }
        self.lbl_info.configure(text=msgs[nuevo_modo])

    def al_hacer_click(self, event):
        x, y = event.x, event.y
        
        # --- CORRECCIÓN AQUÍ ---
        # Usamos find_overlapping con un pequeño rectángulo (x-5, y-5) alrededor del mouse
        # Esto nos asegura que REALMENTE estemos tocando un objeto.
        items_tocados = self.canvas.find_overlapping(x-5, y-5, x+5, y+5)
        
        nodo_id = None
        
        # Revisamos si alguno de los objetos tocados es un nodo
        for item in items_tocados:
            tags = self.canvas.gettags(item)
            if "nodo" in tags or "texto" in tags:
                for t in tags:
                    if t.startswith("grupo_"):
                        nodo_id = int(t.split("_")[1])
                        break
            if nodo_id is not None: break # Ya encontramos uno, dejamos de buscar

        # --- LÓGICA SEGÚN MODO ---
        if self.modo_actual == "NODO":
            if nodo_id is None: # Si NO tocamos ningún nodo, creamos uno nuevo
                self.crear_nodo(x, y)

        elif self.modo_actual == "MOVER":
            if nodo_id is not None:
                self.nodo_seleccionado = nodo_id

        elif self.modo_actual == "CONECTAR":
            if nodo_id is not None:
                if self.nodo_origen_conexion is None:
                    self.nodo_origen_conexion = nodo_id
                    self.canvas.itemconfig(f"circulo_{nodo_id}", outline="red", width=3)
                    self.lbl_info.configure(text=f"Origen: Nodo {nodo_id}\nSelecciona el destino...")
                
                elif nodo_id != self.nodo_origen_conexion:
                    self.crear_arista(self.nodo_origen_conexion, nodo_id)
                    self.restaurar_colores_nodos()
                    self.nodo_origen_conexion = None
                    self.lbl_info.configure(text="¡Conexión creada!\nSelecciona otro origen.")

    def al_arrastrar(self, event):
        if self.modo_actual == "MOVER" and self.nodo_seleccionado is not None:
            x, y = event.x, event.y
            
            nodo = self.nodos[self.nodo_seleccionado]
            nodo['x'] = x
            nodo['y'] = y

            self.canvas.coords(nodo['tag_circulo'], x-20, y-20, x+20, y+20)
            self.canvas.coords(nodo['tag_texto'], x, y)
            
            self.actualizar_aristas_de_nodo(self.nodo_seleccionado)

    def al_soltar(self, event):
        self.nodo_seleccionado = None

    def crear_nodo(self, x, y):
        idx = self.contador_nodos
        tag_grupo = f"grupo_{idx}"
        tag_circulo = f"circulo_{idx}"
        
        circ = self.canvas.create_oval(x-20, y-20, x+20, y+20, fill="#3B8ED0", outline="black", width=2, tags=("nodo", tag_grupo, tag_circulo))
        txt = self.canvas.create_text(x, y, text=str(idx), fill="white", font=("Arial", 12, "bold"), tags=("texto", tag_grupo))
        
        self.nodos.append({'id': idx, 'x': x, 'y': y, 'tag_circulo': circ, 'tag_texto': txt})
        self.contador_nodos += 1

    def crear_arista(self, u_id, v_id):
        # Primero validamos que NO exista ya una conexión entre estos dos
        # (Para evitar duplicados visuales)
        for arista in self.aristas:
            if (arista['u'] == u_id and arista['v'] == v_id) or (arista['u'] == v_id and arista['v'] == u_id):
                print("¡Ya existe esa conexión!")
                return

        peso_str = ctk.CTkInputDialog(text=f"Peso entre {u_id} y {v_id}:", title="Definir Peso").get_input()
        if not peso_str or not peso_str.isdigit(): return

        peso = int(peso_str)
        nodo_u = self.nodos[u_id]
        nodo_v = self.nodos[v_id]

        linea = self.canvas.create_line(nodo_u['x'], nodo_u['y'], nodo_v['x'], nodo_v['y'], 
                                        fill="gray", width=2, tags="arista")
        self.canvas.tag_lower(linea)

        mx = (nodo_u['x'] + nodo_v['x']) / 2
        my = (nodo_u['y'] + nodo_v['y']) / 2
        
        bg_rect = self.canvas.create_rectangle(mx-10, my-10, mx+10, my+10, fill="white", outline="white", tags="arista")
        lbl_peso = self.canvas.create_text(mx, my, text=str(peso), fill="black", font=("Arial", 10), tags="arista")
        self.canvas.tag_lower(bg_rect, linea)

        self.aristas.append({
            'u': u_id, 'v': v_id, 'w': peso,
            'tag_linea': linea, 'tag_texto': lbl_peso, 'tag_bg': bg_rect
        })

    def actualizar_aristas_de_nodo(self, nodo_id):
        for arista in self.aristas:
            if arista['u'] == nodo_id or arista['v'] == nodo_id:
                u = self.nodos[arista['u']]
                v = self.nodos[arista['v']]
                
                self.canvas.coords(arista['tag_linea'], u['x'], u['y'], v['x'], v['y'])
                
                mx, my = (u['x'] + v['x']) / 2, (u['y'] + v['y']) / 2
                self.canvas.coords(arista['tag_texto'], mx, my)
                self.canvas.coords(arista['tag_bg'], mx-10, my-10, mx+10, my+10)

    def restaurar_colores_nodos(self):
        for nodo in self.nodos:
            self.canvas.itemconfig(nodo['tag_circulo'], outline="black", width=2)

    def limpiar_todo(self):
        self.canvas.delete("all")
        self.nodos = []
        self.aristas = []
        self.contador_nodos = 0
        self.nodo_origen_conexion = None

if __name__ == "__main__":
    app = EditorGrafos()
    app.mainloop()