import customtkinter as ctk
import tkinter as tk
from tkinter import simpledialog, messagebox
from Grafo import Grafo

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class EditorGrafos(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Visualizador MST Final (Nodos 1-based)")
        self.geometry("1200x800")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- BARRA DE HERRAMIENTAS ---
        self.toolbar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.toolbar.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(self.toolbar, text="Herramientas", font=("Arial", 20, "bold")).pack(pady=20)

        self.modo_actual = "NODO" 

        # --- BOTONES DE EDICIÓN ---
        self.btn_nodo = ctk.CTkButton(self.toolbar, text="🔵 Crear Nodo", fg_color="#3B8ED0", 
                                      command=lambda: self.cambiar_modo("NODO"))
        self.btn_nodo.pack(pady=10, padx=20)

        self.btn_conectar = ctk.CTkButton(self.toolbar, text="🔗 Conectar", fg_color="gray", 
                                          command=lambda: self.cambiar_modo("CONECTAR"))
        self.btn_conectar.pack(pady=10, padx=20)

        self.btn_mover = ctk.CTkButton(self.toolbar, text="✋ Mover", fg_color="gray", 
                                       command=lambda: self.cambiar_modo("MOVER"))
        self.btn_mover.pack(pady=10, padx=20)
        
        self.btn_borrar = ctk.CTkButton(self.toolbar, text="❌ Borrar (Goma)", fg_color="gray", hover_color="#C0392B",
                                       command=lambda: self.cambiar_modo("BORRAR"))
        self.btn_borrar.pack(pady=10, padx=20)

        ctk.CTkLabel(self.toolbar, text="-----------------").pack(pady=5)
        
        ctk.CTkButton(self.toolbar, text="🗑️ Limpiar Todo", fg_color="#922B21", 
                      command=self.limpiar_todo).pack(pady=10, padx=20)

        ctk.CTkLabel(self.toolbar, text="-----------------").pack(pady=5)

        # --- BOTONES DE RESOLUCIÓN ---
        self.lbl_algo = ctk.CTkLabel(self.toolbar, text="Algoritmos", font=("Arial", 16, "bold"))
        self.lbl_algo.pack(pady=5)

        self.btn_kruskal = ctk.CTkButton(self.toolbar, text="Resolver Kruskal", fg_color="green", 
                                         command=lambda: self.resolver("KRUSKAL"))
        self.btn_kruskal.pack(pady=10, padx=20)

        self.btn_prim = ctk.CTkButton(self.toolbar, text="Resolver Prim", fg_color="#D35B58", 
                                      command=lambda: self.resolver("PRIM"))
        self.btn_prim.pack(pady=10, padx=20)

        self.lbl_costo = ctk.CTkLabel(self.toolbar, text="Costo Total: ---", font=("Arial", 14))
        self.lbl_costo.pack(pady=20)

        self.lbl_info = ctk.CTkLabel(self.toolbar, text="Click para crear nodos.", text_color="gray")
        self.lbl_info.pack(side="bottom", pady=20)

        # --- LIENZO ---
        self.canvas = tk.Canvas(self, bg="white", highlightthickness=0)
        self.canvas.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # --- DATOS ---
        self.nodos = []   
        self.aristas = [] 
        self.contador_nodos = 0
        self.nodo_seleccionado = None     
        self.nodo_origen_conexion = None  

        # Eventos
        self.canvas.bind("<Button-1>", self.al_hacer_click)
        self.canvas.bind("<B1-Motion>", self.al_arrastrar)
        self.canvas.bind("<ButtonRelease-1>", self.al_soltar)

    def cambiar_modo(self, nuevo_modo):
        self.modo_actual = nuevo_modo
        self.nodo_origen_conexion = None 
        self.restaurar_visual_aristas() 
        self.restaurar_colores_nodos()   
        self.lbl_costo.configure(text="Costo Total: ---")

        btn_activos = {
            "NODO": self.btn_nodo, 
            "CONECTAR": self.btn_conectar, 
            "MOVER": self.btn_mover,
            "BORRAR": self.btn_borrar
        }
        colores = {
            "NODO": "#3B8ED0", 
            "CONECTAR": "#E59113", 
            "MOVER": "#2CC985",
            "BORRAR": "#E74C3C" 
        }

        for modo, btn in btn_activos.items():
            if modo == nuevo_modo:
                btn.configure(fg_color=colores[modo])
            else:
                btn.configure(fg_color="gray")
        
        msgs = {
            "NODO": "Click en espacio vacío\npara crear nodo.",
            "CONECTAR": "Click en Nodo A (Origen)\nluego en Nodo B (Destino).",
            "MOVER": "Arrastra los nodos para\nacomodarlos.",
            "BORRAR": "Click en un Nodo o Arista\npara eliminarlo."
        }
        self.lbl_info.configure(text=msgs.get(nuevo_modo, ""))

    def al_hacer_click(self, event):
        x, y = event.x, event.y
        items_tocados = self.canvas.find_overlapping(x-5, y-5, x+5, y+5)
        
        obj_tocado = None
        tipo_obj = None

        for item in items_tocados:
            tags = self.canvas.gettags(item)
            if "nodo" in tags or "texto" in tags:
                for t in tags:
                    if t.startswith("grupo_"):
                        obj_tocado = int(t.split("_")[1])
                        tipo_obj = "NODO"
                        break
            elif "arista" in tags and tipo_obj != "NODO":
                tipo_obj = "ARISTA"
                obj_tocado = item 
            
            if tipo_obj == "NODO": break 

        # --- LÓGICA ---
        if self.modo_actual == "NODO":
            if tipo_obj is None: 
                self.crear_nodo(x, y)

        elif self.modo_actual == "MOVER":
            if tipo_obj == "NODO":
                self.nodo_seleccionado = obj_tocado

        elif self.modo_actual == "CONECTAR":
            if tipo_obj == "NODO":
                nodo_id = obj_tocado
                if self.nodo_origen_conexion is None:
                    self.nodo_origen_conexion = nodo_id
                    self.canvas.itemconfig(f"circulo_{nodo_id}", outline="red", width=3)
                    # VISUAL: Mostramos ID + 1
                    self.lbl_info.configure(text=f"Origen: Nodo {nodo_id + 1}\nSelecciona el destino...")
                
                elif nodo_id != self.nodo_origen_conexion:
                    self.crear_arista(self.nodo_origen_conexion, nodo_id)
                    self.restaurar_colores_nodos()
                    self.nodo_origen_conexion = None
                    self.lbl_info.configure(text="¡Conexión creada!\nSelecciona otro origen.")
        
        elif self.modo_actual == "BORRAR":
            if tipo_obj == "NODO":
                self.eliminar_nodo(obj_tocado)
            elif tipo_obj == "ARISTA":
                self.eliminar_arista_por_tag(obj_tocado)

    def al_arrastrar(self, event):
        if self.modo_actual == "MOVER" and self.nodo_seleccionado is not None:
            x, y = event.x, event.y
            x = max(20, min(self.canvas.winfo_width()-20, x))
            y = max(20, min(self.canvas.winfo_height()-20, y))

            nodo = next((n for n in self.nodos if n['id'] == self.nodo_seleccionado), None)
            if nodo:
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
        
        # VISUAL: Aquí sumamos 1 al texto para que el usuario vea 1, 2, 3...
        txt = self.canvas.create_text(x, y, text=str(idx + 1), fill="white", font=("Arial", 12, "bold"), tags=("texto", tag_grupo))
        
        self.nodos.append({'id': idx, 'x': x, 'y': y, 'tag_circulo': circ, 'tag_texto': txt})
        self.contador_nodos += 1

    def crear_arista(self, u_id, v_id):
        for arista in self.aristas:
            if (arista['u'] == u_id and arista['v'] == v_id) or (arista['u'] == v_id and arista['v'] == u_id):
                return

        # VISUAL: Pedimos peso mostrando IDs + 1
        peso_str = ctk.CTkInputDialog(text=f"Peso entre {u_id + 1} y {v_id + 1}:", title="Definir Peso").get_input()
        if not peso_str or not peso_str.isdigit(): return

        peso = int(peso_str)
        
        nodo_u = next(n for n in self.nodos if n['id'] == u_id)
        nodo_v = next(n for n in self.nodos if n['id'] == v_id)

        linea = self.canvas.create_line(nodo_u['x'], nodo_u['y'], nodo_v['x'], nodo_v['y'], 
                                        fill="gray", width=2, tags="arista")
        
        mx, my = (nodo_u['x'] + nodo_v['x']) / 2, (nodo_u['y'] + nodo_v['y']) / 2
        bg_rect = self.canvas.create_rectangle(mx-15, my-10, mx+15, my+10, fill="white", outline="white", tags="arista")
        lbl_peso = self.canvas.create_text(mx, my, text=str(peso), fill="black", font=("Arial", 10), tags="arista")

        self.canvas.tag_lower(linea) 

        self.aristas.append({
            'u': u_id, 'v': v_id, 'w': peso,
            'tag_linea': linea, 'tag_texto': lbl_peso, 'tag_bg': bg_rect
        })

    def eliminar_nodo(self, nodo_id):
        nodo = next((n for n in self.nodos if n['id'] == nodo_id), None)
        if not nodo: return

        self.canvas.delete(nodo['tag_circulo'])
        self.canvas.delete(nodo['tag_texto'])
        self.nodos.remove(nodo)

        aristas_a_borrar = [a for a in self.aristas if a['u'] == nodo_id or a['v'] == nodo_id]
        for arista in aristas_a_borrar:
            self.borrar_visual_arista(arista)
            self.aristas.remove(arista)

    def eliminar_arista_por_tag(self, tag_canvas):
        arista_encontrada = None
        for arista in self.aristas:
            if tag_canvas in (arista['tag_linea'], arista['tag_texto'], arista['tag_bg']):
                arista_encontrada = arista
                break
        
        if arista_encontrada:
            self.borrar_visual_arista(arista_encontrada)
            self.aristas.remove(arista_encontrada)

    def borrar_visual_arista(self, arista):
        self.canvas.delete(arista['tag_linea'])
        self.canvas.delete(arista['tag_texto'])
        self.canvas.delete(arista['tag_bg'])

    def actualizar_aristas_de_nodo(self, nodo_id):
        for arista in self.aristas:
            if arista['u'] == nodo_id or arista['v'] == nodo_id:
                u = next(n for n in self.nodos if n['id'] == arista['u'])
                v = next(n for n in self.nodos if n['id'] == arista['v'])
                
                self.canvas.coords(arista['tag_linea'], u['x'], u['y'], v['x'], v['y'])
                
                mx, my = (u['x'] + v['x']) / 2, (u['y'] + v['y']) / 2
                self.canvas.coords(arista['tag_texto'], mx, my)
                self.canvas.coords(arista['tag_bg'], mx-15, my-10, mx+15, my+10)

    def resolver(self, algoritmo):
        if not self.aristas:
            messagebox.showinfo("Error", "¡Dibuja algunas conexiones primero!")
            return

        if not self.nodos: return
        max_id = max(n['id'] for n in self.nodos)
        
        g = Grafo(max_id + 1)

        for arista in self.aristas:
            g.agregar_arista(arista['u'], arista['v'], arista['w'])

        resultado = []
        color_solucion = ""
        
        if algoritmo == "KRUSKAL":
            resultado = g.kruskal_mst()
            color_solucion = "#00FF00" 
            self.lbl_costo.configure(text=f"Costo Kruskal: {sum(w for u,v,w in resultado)}")
        else:
            resultado = g.prim_mst()
            color_solucion = "#FF4444"
            self.lbl_costo.configure(text=f"Costo Prim: {sum(w for u,v,w in resultado)}")

        self.pintar_solucion(resultado, color_solucion)

    def pintar_solucion(self, aristas_ganadoras, color):
        self.restaurar_visual_aristas()
        ganadoras = set()
        for u, v, w in aristas_ganadoras:
            ganadoras.add(tuple(sorted((u, v))))

        for arista in self.aristas:
            par = tuple(sorted((arista['u'], arista['v'])))
            if par in ganadoras:
                self.canvas.itemconfig(arista['tag_linea'], fill=color, width=4)
                self.canvas.tag_raise(arista['tag_linea'])
                self.canvas.tag_raise(arista['tag_bg'])
                self.canvas.tag_raise(arista['tag_texto'])

    def restaurar_visual_aristas(self):
        for arista in self.aristas:
            self.canvas.itemconfig(arista['tag_linea'], fill="gray", width=2)
            self.canvas.tag_lower(arista['tag_linea'])

    def restaurar_colores_nodos(self):
        for nodo in self.nodos:
            self.canvas.itemconfig(nodo['tag_circulo'], outline="black", width=2)

    def limpiar_todo(self):
        self.canvas.delete("all")
        self.nodos = []
        self.aristas = []
        self.contador_nodos = 0
        self.nodo_origen_conexion = None
        self.lbl_costo.configure(text="Costo Total: ---")

if __name__ == "__main__":
    app = EditorGrafos()
    app.mainloop()