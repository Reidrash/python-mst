# Esta clase nos permite armar el grafo para posteriormente dibujarlo.
import heapq #import necesario para hacer uso de una cola de prioridad

class Grafo:
    # Constructor para el grafo, donde tenemos dos atributos:
    # V (vertices) : La cantidad de nodos que contiene el grafo
    # grafo : Una lista que guarda todas las conexiones.

    # Vemos que, gracias al constructor, podemos crear un grafo con V vertices y sin aristas. Es decir, estamos
    # creando unicamente los nodos sin conectarlos
    def __init__(self, vertices):
        self.V = vertices  # Cantidad de nodos (vertices)
        self.grafo = []    # Aquí guardaremos las aristas: [origen, destino, peso]. Pero guardaremos listas dentro de la lista general. Es decir, cada elemento de grafo
                           # será una lista de 3 elementos con la información de cada uno de sus nodos.

    # Método para agregar una conexión (arista)
    def agregar_arista(self, origin, destination, weight):
        self.grafo.append([origin, destination, weight])


    # --- Lógica de Union-Find (Para detectar ciclos) ---

    # Método FIND: Busca quién es el "padre" o jefe del nodo 'i'
    def find(self, parent, i):
        if parent[i] == i:
            return i
        return self.find(parent, parent[i])

    # Método UNION: Une dos subconjuntos en uno solo
    def union(self, parent, rank, x, y):
        raiz_x = self.find(parent, x)
        raiz_y = self.find(parent, y)

        # Unimos el árbol más pequeño al más grande (para mantenerlo balanceado)
        if rank[raiz_x] < rank[raiz_y]:
            parent[raiz_x] = raiz_y
        elif rank[raiz_x] > rank[raiz_y]:
            parent[raiz_y] = raiz_x
        else:
            parent[raiz_y] = raiz_x
            rank[raiz_x] += 1

    # --- Algoritmo de Kruskal ---
    def kruskal_mst(self):
        resultado = []  # Aquí guardaremos el Árbol de Expansión Mínima final
        
        # PASO 1: Ordenar todas las aristas de menor a mayor peso
        # Para esto, la función sorted va a tomar dos parámetros, el grafo y una función lambda que nombra cada elemento como un item y hace
        # que solo tome el segundo item (el peso).
        # La función lambda es una función desechable que nos permite manejar todo de manera rápida sin darle un nombre y sin dejarla tirada
        # sin usar después. Esto es porque estamos intentando ordenar una lista de listas, cosa bastante compleja aunque tengamos disponible
        # la función sort. Debemos indicar apropiadamente sobre qué criterio ordenaremos las aristas.
        
        self.grafo = sorted(self.grafo, key=lambda item: item[2])
        # La funcion lambda tiene la siguiente estructura: lambda argumentos: expresion
        # sorted va a tomar la primera arista, digamos que es la siguiente: [0, 1, 10]
        # Esa arista se pasa como el parámetro item y se regresa lo que se encuentra en
        # la posición 2 de item, en este caso, el 10 que sería el peso de la arista.

        parent = []
        rank = []

        # Inicializamos: Cada nodo es su propio padre y tiene rango 0
        for node in range(self.V):
            parent.append(node)
            rank.append(0)

        i = 0 # Índice para recorrer las aristas ordenadas
        e = 0 # Índice para contar cuántas aristas hemos agregado al resultado

        # Iteramos hasta tener (V-1) aristas, que es lo necesario para conectar V nodos
        while e < self.V - 1 and i < len(self.grafo):
            # Tomamos la arista más pequeña (porque ya ordenamos la lista)

            # En esta linea, se obtienen los elementos de self.grafo y se colocan en 3 variables diferentes. Python permite hacer
            # esto en una sola linea
            origin, destination, weight = self.grafo[i]
            i = i + 1

            # PASO 2: Verificar ciclos
            x = self.find(parent, origin)
            y = self.find(parent, destination)

            # Si x != y, significa que NO tienen el mismo jefe, por lo tanto NO forman ciclo.
            if x != y:
                e = e + 1
                resultado.append([origin, destination, weight])
                self.union(parent, rank, x, y) # Los unimos en el mismo conjunto
            # Si x == y, significa que ya están conectados, así que ignoramos la arista (no hacemos nada)

        # Imprimimos el resultado en consola
        print("Aristas en el Árbol de Expansión Mínima (MST):")
        costo_total = 0
        for origin, destination, weight in resultado:
            costo_total += weight
            print(f"Conexión: Nodo {origin} -- Nodo {destination}  (Costo: {weight})")
        print(f"---------------------------------------")
        print(f"COSTO MÍNIMO TOTAL: {costo_total}")

    # --- Algoritmo de Prim ---
    def prim_mst(self):
        # PASO 1: Transformar la lista de aristas a una Lista de Adyacencia
        # Esto nos permite saber rápidamente quiénes son los vecinos de un nodo.
        # Creamos un diccionario donde la clave es el nodo y el valor es una lista de (vecino, peso)
        adj = {i: [] for i in range(self.V)}
        
        for u, v, w in self.grafo:
            adj[u].append((v, w))
            adj[v].append((u, w)) # Importante: Como es no dirigido, va en ambos sentidos

        # PASO 2: Inicializar variables
        # La "Min-Heap" (Cola de Prioridad) guardará: (peso, nodo_actual, nodo_padre)
        # Empezamos arbitrariamente en el nodo 0 con costo 0.
        min_heap = [(0, 0, -1)] 
        
        visitados = set() # Un conjunto para recordar qué casas ya conectamos (evita ciclos)
        mst_aristas = []  # Aquí guardaremos el resultado final
        costo_total = 0

        print("\n--- SOLUCIÓN DEL ALGORITMO DE PRIM ---")

        # PASO 3: El ciclo principal (Mientras haya opciones en la cola)
        while min_heap:
            # Obtenemos la conexión más barata disponible en toda la frontera de exploración
            peso, u, padre = heapq.heappop(min_heap)

            # Si el nodo 'u' ya está conectado a la red, lo ignoramos
            if u in visitados:
                continue

            # --- Si no estaba visitado, lo aceptamos en el árbol ---
            visitados.add(u)
            costo_total += peso
            
            # Guardamos la conexión (excepto para el nodo inicial que no tiene padre)
            if padre != -1:
                mst_aristas.append([padre, u, peso])
                print(f"Conexion: Nodo {padre} -- Nodo {u}  (Costo: {peso})")

            # PASO 4: Explorar vecinos
            # Miramos a todos los vecinos del nodo recién agregado ('u')
            for v, w in adj[u]:
                if v not in visitados:
                    # Agregamos posibles caminos a la cola. 
                    # heapq se encargará de ordenar automáticamente para que el menor quede arriba.
                    heapq.heappush(min_heap, (w, v, u))

        print(f"---------------------------------------")
        print(f"COSTO MÍNIMO TOTAL (PRIM): {costo_total}")

# --- BLOQUE DE PRUEBA ---
if __name__ == "__main__":
    # Son 8 casas (Nodos 0 al 7)
    g = Grafo(8)
    
    # Cargamos tus datos
    # [Origen, Destino, Peso]
    g.agregar_arista(0, 1, 300)
    g.agregar_arista(0, 2, 200)
    g.agregar_arista(0, 3, 500)
    g.agregar_arista(1, 2, 300)
    g.agregar_arista(2, 3, 200)
    g.agregar_arista(1, 4, 300)
    g.agregar_arista(3, 5, 600)
    g.agregar_arista(2, 4, 500)
    g.agregar_arista(2, 6, 700)
    g.agregar_arista(2, 7, 900) 
    g.agregar_arista(2, 5, 300)
    g.agregar_arista(4, 6, 400)
    g.agregar_arista(6, 7, 200)
    g.agregar_arista(5, 7, 100)

    # Ejecutar kruskal 
    g.kruskal_mst()

    # Ejecutar Prim
    g.prim_mst()