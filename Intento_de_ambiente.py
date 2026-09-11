import random
import numpy as np
from noise import pnoise2

#Entorno: Matriz de 300x300
SHAPE = (300, 300)
PASTO_MAX=1.0

# Semilla de la simulación: controla todo lo aleatorio (posiciones iniciales, genes,
# movimiento, mutaciones y pasto inicial).
# None = cada corrida sale distinta. Un número (ej: 42) = la corrida se repite exacta,
# útil para comparar si un cambio en el código mejoró algo o fue suerte.
# La fertilidad NO depende de esto: tiene su propia semilla fija (Entorno(seed=1)).
SEMILLA = None

def fijar_semilla(semilla):
    """Fija las semillas de random y numpy. Si semilla es None no hace nada."""
    if semilla is not None:
        random.seed(semilla)
        np.random.seed(semilla)

#Casilla (pasto, fertilidad).
#Tasa positiva (crece):  pasto += tasa * fertilidad * (1-pasto/PASTO_MAX)
#Tasa negativa (se seca): pasto += tasa * pasto   -> pierde un % de lo que tiene

#estaciones: primavera(0), verano(1), otoño(2), invierno(3)
Tasa_crecimiento = [
    0.08,
    0.04,
    -0.005,  # otoño: se seca de a poco (pierde ~40% en 100 ticks)
    -0.02    # invierno: se seca fuerte (queda ~13% en 100 ticks)
] #Tasa de crecimiento del pasto por estación

def generar_fertilidad(shape, escala=50.0, seed=0):
    """Fertilidad generada con ruido Perlin."""
    fert=np.zeros(shape,dtype=np.float32)
    for i in range(shape[0]):
        for j in range(shape[1]):
            fert[i,j] = pnoise2(i / escala, j / escala, base=seed)
    #Normalizar de [-1,1] aprox a [0,1]
    fert = (fert - fert.min()) / (fert.max() - fert.min())
    return fert
class Entorno:
    def __init__(self, shape=SHAPE, seed=0):
        self.shape = shape
        self.fertilidad = generar_fertilidad(shape, seed=seed)
        self.pasto=np.random.uniform(0,0.3,size=shape).astype(np.float32)
        self.tick_actual=0
        self.estacion=0 #0: primavera, 1: verano, 2: otoño, 3: invierno

        # Registro de herbívoros, actualizado al inicio de cada tick (ver registrar_herbivoros).
        # Sirve para que los animales se perciban entre ellos.
        self.registrar_herbivoros([])

    def registrar_herbivoros(self, poblacion):
        """Anota dónde está cada herbívoro:
        - herbivoros: cuántos hay en cada celda
        - vecinos_herbivoros: cuántos hay en el bloque 3x3 alrededor de cada celda
        - fertiles_herbivoros["M"] / ["H"]: cuántos machos / hembras que pueden aparearse hay
          en cada celda (sirve para descartar rápido las zonas sin posibles parejas)
        - celdas_fertiles_herbivoros["M"] / ["H"]: {(fila, columna): [individuos fértiles de ese sexo]}"""
        self.herbivoros = np.zeros(self.shape, dtype=np.int32)
        self.fertiles_herbivoros = {"M": np.zeros(self.shape, dtype=np.int32),
                                    "H": np.zeros(self.shape, dtype=np.int32)}
        self.celdas_fertiles_herbivoros = {"M": {}, "H": {}}
        for h in poblacion:
            self.herbivoros[h.fila, h.columna] += 1
            if h.puede_reproducirse():
                self.fertiles_herbivoros[h.sexo][h.fila, h.columna] += 1
                self.celdas_fertiles_herbivoros[h.sexo].setdefault((h.fila, h.columna), []).append(h)
        # Suma de cada bloque 3x3: se suma el mapa desplazado en las 9 posiciones del bloque
        con_borde = np.pad(self.herbivoros, 1)
        self.vecinos_herbivoros = sum(
            con_borde[i:i + self.shape[0], j:j + self.shape[1]]
            for i in range(3) for j in range(3)
        )

    def actualizar_estacion(self, ticks_por_Estacion=100):
        self.estacion = (self.tick_actual // ticks_por_Estacion) % 4

    def crecer_pasto(self):
        tasa = Tasa_crecimiento[self.estacion]
        if tasa >= 0:
            # Crecimiento logístico: rápido con poco pasto, se frena al acercarse a PASTO_MAX
            crecimiento = tasa * self.fertilidad * (1 - self.pasto / PASTO_MAX)
        else:
            # Secado: cada celda pierde un porcentaje de lo que tiene, así las celdas
            # llenas pierden más pasto que las ya comidas (antes pasaba al revés)
            crecimiento = tasa * self.pasto
        self.pasto = np.clip(self.pasto + crecimiento, 0, PASTO_MAX)

    def step(self):
        self.tick_actual += 1
        self.actualizar_estacion()
        self.crecer_pasto()

    def consumir(self, fila, columna, cantidad):
        comido=min(cantidad, self.pasto[fila, columna])
        self.pasto[fila, columna] -= comido
        return comido

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    entorno=Entorno(seed=1)
    for _ in range(200):
        entorno.step()

    fig, axs =plt.subplots(1,2,figsize=(10,5))
    axs[0].imshow(entorno.fertilidad, cmap='YlGn')
    axs[0].set_title('Fertilidad (fija)')
    axs[1].imshow(entorno.pasto, cmap='Greens', vmin=0, vmax=PASTO_MAX)
    axs[1].set_title(f"Pasto (tick {entorno.tick_actual}, estacion {entorno.estacion})")
    plt.show()