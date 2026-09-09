import numpy as np
from noise import pnoise2

#Entorno: Matriz de 300x300
SHAPE = (300, 300)
PASTO_MAX=1.0
#Casilla (pasto, fertilidad).
#pasto += tasa_crecimiento[estacion_actual] * fertilidad*(1-pasto/PASTO_MAX)

#estaciones: primavera(0), verano(1), otoño(2), invierno(3)
Tasa_crecimiento = [
    0.08,
    0.04,
    0.00,
    -0.08
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

    def actualizar_estacion(self, ticks_por_Estacion=100):
        self.estacion = (self.tick_actual // ticks_por_Estacion) % 4

    def crecer_pasto(self):
        tasa = Tasa_crecimiento[self.estacion]
        crecimiento=tasa*self.fertilidad*(1-self.pasto/PASTO_MAX)
        self.pasto =np.clip(self.pasto + crecimiento, 0, PASTO_MAX)

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