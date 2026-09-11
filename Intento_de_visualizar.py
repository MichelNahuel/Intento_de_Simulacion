import numpy as np
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from Intento_de_ambiente import PASTO_MAX, SEMILLA, Entorno, fijar_semilla
from Intento_de_herbivoro import crear_poblacion_inicial, simular_tick

#Steup inicial
fijar_semilla(SEMILLA)
entorno = Entorno(seed=1)
poblacion = crear_poblacion_inicial(50, entorno.shape)

#historial de poblacion
historial_poblacion = []
historial_ticks = []

fig, (ax_mapa, ax_pop) =plt.subplots(1, 2, figsize=(13,6))
img = ax_mapa.imshow(entorno.pasto, cmap='Greens', vmin=0, vmax=PASTO_MAX)

#Colorinchis segun el sexo del animal
colores = {'M':'royalblue', 'H':'deeppink'}
scatter = ax_mapa.scatter([],[],s=15)

titulo= ax_mapa.set_title("Simulacion de un medioambiente funcional, Nahuel Michel")

linea_pop, = ax_pop.plot([], [], color='darkgreen')
ax_pop.set_xlabel("Tick")
ax_pop.set_ylabel("Cantidad de herbivoros")
ax_pop.set_title("poblacion en el tiempo")

def estacion_actual(tick):
    estaciones = ["Primavera", "Verano", "Otoño", "Invierno"]
    ticks_por_estacion = 100
    indice_estacion = (tick // ticks_por_estacion) % len(estaciones)
    return estaciones[indice_estacion]

def actualizar(frame):
    global poblacion

    # mismas reglas que la corrida por consola (ver simular_tick en Intento_de_herbivoro.py)
    poblacion = simular_tick(entorno, poblacion)

    #registrar en el historial
    historial_poblacion.append(len(poblacion))
    historial_ticks.append(entorno.tick_actual)

    #redibujar pasto
    img.set_data(entorno.pasto)

#redibujar herbivoros (columna = x, fila = y en el sactter)
    if poblacion:
        xs = [c.columna for c in poblacion]
        ys = [c.fila for c in poblacion]
        cs = [colores[c.sexo] for c in poblacion]
        scatter.set_offsets(np.column_stack([xs, ys]))
        scatter.set_color(cs)
    else:
        scatter.set_offsets(np.empty((0, 2)))
    titulo.set_text(f"Tick: {entorno.tick_actual} | Estacion: {estacion_actual(entorno.tick_actual)} | Poblacion: {len(poblacion)}")

    #Redibujar curva de poblacion
    linea_pop.set_data(historial_ticks, historial_poblacion)
    ax_pop.relim()
    ax_pop.autoscale_view()

    return img, scatter, linea_pop, titulo

ani = animation.FuncAnimation(fig, actualizar, frames=100, interval=50, blit=False)
plt.show()
