# Intento_de_ser_vivo.py
import random
import numpy as np

# --- Parámetros globales compartidos por cualquier ser vivo ---
ENERGIA_MAX = 100.0
FUERZA_MUTACION = 0.1        # desviación estándar del ruido gaussiano en mutaciones
RANGO_PROB_MUT = (0.01, 0.08)


class SerVivo:
    def __init__(self, fila, columna, energia=None, gasto_metabolico=None, sexo=None, prob_mut=None):
        self.fila = fila
        self.columna = columna

        self.sexo = sexo if sexo is not None else random.choice(["M", "H"])
        self.prob_mut = prob_mut if prob_mut is not None else random.uniform(*RANGO_PROB_MUT)

        # gasto_metabolico depende de la especie -> el rango se define en la subclase,
        # por eso acá solo se usa el valor si ya viene dado (heredado o pasado a mano)
        self.gasto_metabolico = gasto_metabolico

        self.energia = energia if energia is not None else ENERGIA_MAX / 2

    def esta_vivo(self):
        return self.energia > 0

    def mutar(self, valor, rango):
        if random.random() < self.prob_mut:
            valor += random.gauss(0, FUERZA_MUTACION)
            valor = np.clip(valor, rango[0], rango[1])
        return valor

    def mover(self, shape):
        #movimiento aleatorio simple.
        # Las subclases pueden sobreescribir esto con movimiento "a voluntad".
        df, dc = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
        self.fila = np.clip(self.fila + df, 0, shape[0] - 1)
        self.columna = np.clip(self.columna + dc, 0, shape[1] - 1)

    def accion_especifica(self, entorno):
        # Cada subclase define qué hace acá: comer pasto, cazar, etc.
        raise NotImplementedError("Cada subclase debe implementar accion_especifica()")

    def step(self, entorno):
        self.mover(entorno.shape)
        self.accion_especifica(entorno)
        self.energia -= self.gasto_metabolico
        self.energia = min(self.energia, ENERGIA_MAX)

    def puede_reproducirse(self):
        return self.energia >= 0.4 * ENERGIA_MAX