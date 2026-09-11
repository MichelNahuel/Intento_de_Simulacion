import random
import numpy as np
from Intento_de_ambiente import Entorno, SEMILLA, fijar_semilla
from Intento_de_ser_vivo import SerVivo, ENERGIA_MAX

# --- Parámetros específicos del herbívoro ---
# Rangos de los genes
RANGO_GASTO_METABOLICO = (0.1, 1.5)       # cuánta energía gasta por tick
RANGO_EFICIENCIA_COMER = (1.1, 2.0)       # cuánta energía obtiene por unidad de pasto consumido
RANGO_VISION = (1.0, 6.0)                 # radio de visión en celdas (mantenerlo cuesta COSTO_VISION por unidad)
RANGO_VELOCIDAD = (0.5, 4.0)              # pasos por tick (cuesta COSTO_VELOCIDAD por unidad + COSTO_PASO por paso)
RANGO_COMUNITARIO = (-1.0, 1.0)           # -1 = evita a los demás, 0 = indiferente, 1 = busca estar cerca de otros
RANGO_EDAD_MADUREZ = (20.0, 150.0)        # edad (en ticks) a partir de la cual puede reproducirse
RANGO_GESTACION_HEMBRA = (10.0, 40.0)     # ticks que dura la gestación de una hembra
RANGO_GESTACION_MACHO = (5.0, 50.0)       # ticks que un macho espera, tras aparearse, para volver a aparearse
RANGO_ATRACTIVO = (0.0, 1.0)              # cuán atractivo es para el otro sexo (mostrarlo cuesta COSTO_ATRACTIVO)
RANGO_EXIGENCIA = (0.0, 1.0)              # atractivo mínimo que acepta en una pareja

FACTOR_COMER = 1.0                    # pasto que puede comer por tick = FACTOR_COMER * gasto_metabolico
PESO_COMUNITARIO = 0.1                # cuánto pesa cada vecino frente al pasto al elegir hacia dónde ir
PASTO_MINIMO_VISIBLE = 0.01           # por debajo de esto considera que en esa celda "no hay pasto"
n = 1000   # con pocos individuos casi no encuentran pareja y la población tiende a extinguirse
t = 1500

class Herbivoro(SerVivo):
    # --- Genes del herbívoro: {nombre: rango} ---
    # Se suman a los de SerVivo (prob_mut). Para agregar un gen nuevo alcanza con sumarlo acá:
    # se genera al azar, se hereda y muta solo.
    GENES = {
        **SerVivo.GENES,
        "gasto_metabolico": RANGO_GASTO_METABOLICO,
        "eficiencia_comer": RANGO_EFICIENCIA_COMER,
        "vision": RANGO_VISION,
        "velocidad": RANGO_VELOCIDAD,
        "comunitario": RANGO_COMUNITARIO,
        "edad_madurez": RANGO_EDAD_MADUREZ,
        "tiempo_gestacion_hembra": RANGO_GESTACION_HEMBRA,
        "tiempo_gestacion_macho": RANGO_GESTACION_MACHO,
        # Cortejo: cada individuo lleva los de los dos sexos, pero solo expresa los del suyo
        "atractivo_macho": RANGO_ATRACTIVO,
        "atractivo_hembra": RANGO_ATRACTIVO,
        "exigencia_macho": RANGO_EXIGENCIA,
        "exigencia_hembra": RANGO_EXIGENCIA,
    }

    # --- Parámetros de la especie (los usa SerVivo) ---
    APORTE_GESTACION = 1.0                     # energía por tick que la hembra le pasa a la cría
                                               # (la cría nace con tiempo_gestacion_hembra * APORTE_GESTACION)
    ENERGIA_MIN_GESTACION = 0.15 * ENERGIA_MAX # si la hembra baja de esto gestando, pierde la cría
    VEJEZ_POR_MADUREZ = 16                     # empieza a envejecer a 16 veces su edad de madurez
                                               # (ej: madura a los 50 ticks -> envejece desde los 800)
    FACTOR_VEJEZ_MINIMO = 0.2                  # al final conserva el 20% de su visión y velocidad

    def registro_de_fertiles(self, entorno, sexo):
        # Los herbívoros fértiles de cada sexo los anota el Entorno al inicio de cada tick
        return entorno.fertiles_herbivoros[sexo], entorno.celdas_fertiles_herbivoros[sexo]

    def mover(self, entorno):
        # Movimiento "a voluntad": reemplaza al movimiento aleatorio de SerVivo.
        # Decide a dónde ir y camina hacia ese destino; solo vuelve a mirar a su alrededor
        # cuando llega (así no recalcula en cada paso, que es lo más costoso de la simulación).
        # Devuelve cuántos pasos dio, porque cada paso cuesta energía.
        capacidad = FACTOR_COMER * self.gasto_metabolico
        radio = self.radio_vision_actual()                 # los ancianos ven menos
        fila_inicio, columna_inicio = self.fila, self.columna

        destino = None
        pasos_dados = 0
        for _ in range(self.pasos_este_tick()):            # los ancianos se mueven menos
            pasto_aca = entorno.pasto[self.fila, self.columna]

            # Si en su celda hay pasto suficiente para comer este tick, se queda pastando
            if pasto_aca >= capacidad:
                break

            # Elige destino si todavía no tiene uno, o si ya llegó al que tenía
            if radio > 0 and (destino is None or destino == (self.fila, self.columna)):
                destino = self.elegir_destino(entorno, radio, fila_inicio, columna_inicio)

            if destino is not None:
                self.paso_hacia(*destino)
            elif pasto_aca >= PASTO_MINIMO_VISIBLE:
                break   # no ve nada mejor que su celda, y en ella algo hay para comer: se queda
            else:
                # No ve nada mejor y su celda está vacía (o no ve nada, ej: muy anciano): explora al azar
                self.paso_al_azar(entorno)
            pasos_dados += 1

        return pasos_dados

    def elegir_destino(self, entorno, radio, fila_inicio, columna_inicio):
        """Mira las celdas a distancia <= radio y devuelve la más atractiva, combinando
        pasto y compañía según el gen comunitario. Devuelve None si su propia celda
        ya está entre las mejores.
        Se llama muchísimas veces, por eso usa la menor cantidad posible de operaciones de numpy:
        con ventanas tan chicas, lo que más tarda es cada llamada a numpy, no la cuenta en sí."""
        fila, columna = self.fila, self.columna

        # Ventana de celdas que percibe (recortada en los bordes del mapa)
        f0 = max(fila - radio, 0)
        f1 = min(fila + radio + 1, entorno.shape[0])
        c0 = max(columna - radio, 0)
        c1 = min(columna + radio + 1, entorno.shape[1])

        # Atractivo de cada celda: el pasto visible (lo que está por debajo del mínimo cuenta como nada)...
        pasto = entorno.pasto[f0:f1, c0:c1]
        puntaje = np.where(pasto < PASTO_MINIMO_VISIBLE, 0.0, pasto)   # es un array nuevo: se puede modificar
        # ...más los vecinos de su bloque 3x3: suman si es comunitario (> 0), restan si es solitario (< 0)
        peso_vecinos = self.comunitario * PESO_COMUNITARIO
        puntaje += peso_vecinos * entorno.vecinos_herbivoros[f0:f1, c0:c1]

        # No contarse a sí mismo como vecino: el conteo se hizo al inicio del tick,
        # así que se descuenta en el bloque 3x3 alrededor de donde empezó
        r0, r1 = max(fila_inicio - 1, f0), min(fila_inicio + 2, f1)
        k0, k1 = max(columna_inicio - 1, c0), min(columna_inicio + 2, c1)
        if r0 < r1 and k0 < k1:
            puntaje[r0 - f0:r1 - f0, k0 - c0:k1 - c0] -= peso_vecinos

        # Si su propia celda está entre las mejores, no hay a dónde ir que valga la pena
        mejor = puntaje.max()
        if puntaje[fila - f0, columna - c0] >= mejor:
            return None

        # Las mejores celdas, numeradas fila por fila dentro de la ventana
        ancho = c1 - c0
        mejores = np.flatnonzero(puntaje == mejor)
        if len(mejores) > 1:
            # Si hay empate se queda con las más cercanas (camina menos, y al huir de un grupo
            # no lo atraviesa). Las distancias solo se calculan acá, cuando hacen falta.
            distancias = np.abs(mejores // ancho + f0 - fila) + np.abs(mejores % ancho + c0 - columna)
            mejores = mejores[distancias == distancias.min()]

        # Una al azar entre las que quedan, y se pasa del número a (fila, columna)
        i = int(mejores[random.randrange(len(mejores))])
        return (f0 + i // ancho, c0 + i % ancho)

    def accion_especifica(self, entorno):
        # Esto reemplaza al viejo método comer() -- se llama automáticamente desde step() en SerVivo
        # Un metabolismo rápido gasta más energía, pero también puede procesar más pasto por tick.
        # Así un gasto bajo ya no es "gratis": aguanta mejor la escasez, pero con mucho pasto
        # come poco y se reproduce lento.
        capacidad = FACTOR_COMER * self.gasto_metabolico
        cantidad_comida = entorno.consumir(self.fila, self.columna, capacidad)
        self.energia += cantidad_comida * self.eficiencia_comer


def crear_poblacion_inicial(n, shape):
    poblacion = []
    for _ in range(n):
        fila = random.randint(0, shape[0] - 1)
        columna = random.randint(0, shape[1] - 1)
        h = Herbivoro(fila, columna)
        # Edad inicial al azar por debajo de su madurez: así no llegan todos a reproducirse en el mismo tick
        h.edad = random.randint(0, int(h.edad_madurez))
        poblacion.append(h)
    return poblacion


def simular_tick(entorno, poblacion):
    """Avanza la simulación un tick y devuelve la población actualizada.
    La usan tanto la corrida por consola como el visualizador, para que ambos
    sigan exactamente las mismas reglas."""
    entorno.step()
    # Registrar dónde está cada herbívoro (y qué machos pueden aparearse),
    # para que puedan percibirse entre ellos
    entorno.registrar_herbivoros(poblacion)

    nuevos = []
    for h in poblacion:
        hijo = h.step(entorno)   # step() devuelve la cría si nació en este tick
        if hijo is not None:
            nuevos.append(hijo)
    poblacion.extend(nuevos)

    # Se retiran los muertos
    return [h for h in poblacion if h.esta_vivo()]


if __name__ == "__main__":
    fijar_semilla(SEMILLA)
    entorno = Entorno(seed=1)
    poblacion = crear_poblacion_inicial(n, entorno.shape)

    for tick in range(t):
        poblacion = simular_tick(entorno, poblacion)

        if tick % 20 == 0:
            print(f"Tick {tick}: Poblacion viva: {len(poblacion)}")

    print(f"Final: Poblacion viva: {len(poblacion)}, de los {n} iniciales")
