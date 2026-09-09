import random
import numpy as np
from Intento_de_ambiente import Entorno
from Intento_de_ser_vivo import SerVivo, ENERGIA_MAX, FUERZA_MUTACION, RANGO_PROB_MUT

# --- Parámetros específicos del herbívoro ---
RANGO_GASTO_METABOLICO = (0.1, 1.5)   # cuánta energía gasta por tick
RANGO_EFICIENCIA_COMER = (1.1, 2.0)   # cuánta energía obtiene por unidad de pasto consumido
CANTIDAD_COMER = 0.3                  # cuánto pasto intenta comer por tick
COSTO_REPRODUCCION = 20.0             # energía que le cuesta reproducirse
n = 100
t = 1500

class Herbivoro(SerVivo):
    def __init__(self, fila, columna, energia=None, gasto_metabolico=None,
                 eficiencia_comer=None, sexo=None, prob_mut=None):

        # Si no se pasa, se genera aleatorio dentro del rango propio de esta especie
        gasto_metabolico = gasto_metabolico if gasto_metabolico is not None else random.uniform(*RANGO_GASTO_METABOLICO)

        super().__init__(fila, columna, energia=energia, gasto_metabolico=gasto_metabolico, sexo=sexo, prob_mut=prob_mut)

        self.eficiencia_comer = eficiencia_comer if eficiencia_comer is not None else random.uniform(*RANGO_EFICIENCIA_COMER)

    def accion_especifica(self, entorno):
        # Esto reemplaza al viejo método comer() -- se llama automáticamente desde step() en SerVivo
        cantidad_comida = entorno.consumir(self.fila, self.columna, CANTIDAD_COMER)
        self.energia += cantidad_comida * self.eficiencia_comer

    def reproducion_asexual(self):
        self.energia -= COSTO_REPRODUCCION

        gasto_hijo = self.mutar(self.gasto_metabolico, RANGO_GASTO_METABOLICO)
        eficiencia_hijo = self.mutar(self.eficiencia_comer, RANGO_EFICIENCIA_COMER)
        prob_mut_hijo = self.mutar(self.prob_mut, (0.01, 0.08))

        hijo = Herbivoro(
            fila=self.fila, columna=self.columna,
            energia=COSTO_REPRODUCCION,
            gasto_metabolico=gasto_hijo,
            eficiencia_comer=eficiencia_hijo,
            prob_mut=prob_mut_hijo,
            sexo=random.choice(["M", "H"]),
        )
        return hijo


def crear_poblacion_inicial(n, shape):
    poblacion = []
    for _ in range(n):
        fila = random.randint(0, shape[0] - 1)
        columna = random.randint(0, shape[1] - 1)
        poblacion.append(Herbivoro(fila, columna))
    return poblacion


if __name__ == "__main__":
    entorno = Entorno(seed=1)
    poblacion = crear_poblacion_inicial(n, entorno.shape)

    for tick in range(t):
        entorno.step()
        for h in poblacion:
            h.step(entorno)

        nuevos = []
        for h in poblacion:
            if h.esta_vivo() and h.puede_reproducirse():
                nuevos.append(h.reproducion_asexual())
        poblacion.extend(nuevos)

        poblacion = [h for h in poblacion if h.esta_vivo()]

        if tick % 20 == 0:
            print(f"Tick {tick}: Poblacion viva: {len(poblacion)}")

    print(f"Final: Poblacion viva: {len(poblacion)}, de los {n} iniciales")