import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
from Grafo import Grafo

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("MST Visualizer: Kruskal & Prim")
        self.geometry("1100x700")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- PANEL LATERAL ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")

        lbl_titulo = ctk.CTkLabel(self.sidebar_frame, text="Controles", font=ctk.CTkFont(size=20, weight="bold"))
        lbl_titulo.grid(row=0, column=0, padx=20, pady=(20, 10))

        # 1. Botón Cargar
        self.btn_cargar = ctk.CTkButton(self.sidebar_frame, text="1. Cargar Grafo Casas", command=self.cargar_ejemplo_casas)
        self.btn_cargar.grid(row=1, column=0, padx=20, pady=10)

        # 2. Separador visual
        linea = ctk.CTkLabel(self.sidebar_frame, text="-----------------")
        linea.grid(row=2, column=0, pady=10)

        # 3. Botones de Resolver
        self.btn_kruskal = ctk.CTkButton(self.sidebar_frame, text="2. Resolver Kruskal", fg_color="green", command=self.resolver_con_kruskal)
        self.btn_kruskal.grid(row=3, column=0, padx=20, pady=10)
        # Desactivados al inicio hasta que cargues el grafo
        self.btn_kruskal.configure(state="disabled") 

        self.btn_prim = ctk.CTkButton(self.sidebar_frame, text="3. Resolver Prim", fg_color="#D35B58", command=self.resolver_con_prim)
        self.btn_prim.grid(row=4, column=0, padx=20, pady=10)
        self.btn_prim.configure(state="disabled")

        # Label de resultado
        self.lbl_info = ctk.CTkLabel(self.sidebar_frame, text="Costo Total: ---", font=ctk.CTkFont(size=14))
        self.lbl_info.grid(row=5, column=0, padx=20, pady=20)

        # --- ÁREA GRÁFICA ---
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.fig, self.ax = plt.subplots(figsize=(5, 4), dpi=100)
        self.ax.axis("off")
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

        # Variables de estado
        self.mi_grafo = None
        self.G_visual = None
        self.posiciones = None

    def cargar_ejemplo_casas(self):
        self.mi_grafo = Grafo(8)
        datos = [
            (0, 1, 300), (0, 2, 200), (0, 3, 500),
            (1, 2, 300), (2, 3, 200), (1, 4, 300),
            (3, 5, 600), (2, 4, 500), (2, 6, 700),
            (2, 5, 300), (4, 6, 400), (6, 7, 200), (5, 7, 100),
            (2, 7, 9000) # La arista fantasma
        ]
        
        for u, v, w in datos:
            self.mi_grafo.agregar_arista(u, v, w)
        
        # Habilitar botones
        self.btn_kruskal.configure(state="normal")
        self.btn_prim.configure(state="normal")
        self.lbl_info.configure(text="Costo Total: ---")
        
        self.dibujar_grafo_base()

    def dibujar_grafo_base(self):
        self.ax.clear()
        self.G_visual = nx.Graph()
        
        for u, v, w in self.mi_grafo.grafo:
            self.G_visual.add_edge(u, v, weight=w)

        if self.posiciones is None:
            self.posiciones = nx.spring_layout(self.G_visual, seed=42)

        # Dibujar todo en GRIS (estado neutro)
        nx.draw_networkx_nodes(self.G_visual, self.posiciones, ax=self.ax, node_size=700, node_color="#3B8ED0")
        nx.draw_networkx_labels(self.G_visual, self.posiciones, ax=self.ax, font_color="white", font_weight="bold")
        nx.draw_networkx_edges(self.G_visual, self.posiciones, ax=self.ax, edge_color="lightgray", width=1.5)
        
        # Etiquetas de peso
        labels = nx.get_edge_attributes(self.G_visual, 'weight')
        nx.draw_networkx_edge_labels(self.G_visual, self.posiciones, edge_labels=labels, ax=self.ax, font_size=8)

        self.ax.set_title("Red de Distribución (Sin Resolver)")
        self.canvas.draw()

    # --- LÓGICA DE RESOLUCIÓN ---
    def resolver_con_kruskal(self):
        # 1. Ejecutar algoritmo (recibimos la lista gracias al return que agregaste)
        aristas_mst = self.mi_grafo.kruskal_mst()
        
        # 2. Calcular costo para mostrarlo
        costo = sum([w for u, v, w in aristas_mst])
        self.lbl_info.configure(text=f"Costo Kruskal: {costo}")
        
        # 3. Pintar solución en VERDE
        self.resaltar_solucion(aristas_mst, "Solución Kruskal", "green")

    def resolver_con_prim(self):
        aristas_mst = self.mi_grafo.prim_mst()
        costo = sum([w for u, v, w in aristas_mst])
        self.lbl_info.configure(text=f"Costo Prim: {costo}")
        
        # 3. Pintar solución en ROJO/CORAL
        self.resaltar_solucion(aristas_mst, "Solución Prim", "#D35B58")

    def resaltar_solucion(self, aristas_solucion, titulo, color_destacado):
        self.ax.clear()
        
        # Creamos un conjunto (set) de las conexiones ganadoras para buscarlas rápido
        # Guardamos (min, max) para que no importe el orden (0,1) o (1,0)
        conexiones_ganadoras = set()
        for u, v, w in aristas_solucion:
            conexiones_ganadoras.add(tuple(sorted((u, v))))

        # Clasificamos los colores de TODAS las aristas del gráfico
        colores_aristas = []
        anchos_aristas = []
        
        for u, v in self.G_visual.edges():
            # Verificamos si esta arista está en la lista ganadora
            if tuple(sorted((u, v))) in conexiones_ganadoras:
                colores_aristas.append(color_destacado) # Pintar
                anchos_aristas.append(3.0)              # Hacer más gruesa
            else:
                colores_aristas.append("lightgray")     # Dejar gris
                anchos_aristas.append(1.0)              # Hacer delgada

        # DIBUJAR DE NUEVO
        nx.draw_networkx_nodes(self.G_visual, self.posiciones, ax=self.ax, node_size=700, node_color="#3B8ED0")
        nx.draw_networkx_labels(self.G_visual, self.posiciones, ax=self.ax, font_color="white", font_weight="bold")
        
        # Aquí pasamos la lista de colores que calculamos arriba
        nx.draw_networkx_edges(self.G_visual, self.posiciones, ax=self.ax, 
                             edge_color=colores_aristas, width=anchos_aristas)
        
        labels = nx.get_edge_attributes(self.G_visual, 'weight')
        nx.draw_networkx_edge_labels(self.G_visual, self.posiciones, edge_labels=labels, ax=self.ax, font_size=8)

        self.ax.set_title(titulo)
        self.canvas.draw()

    def on_closing(self):
        plt.close('all')
        self.quit()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()