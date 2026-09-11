# Intento_de_ser_vivo.py
import random
import numpy as np

# --- Parámetros globales compartidos por cualquier ser vivo ---
ENERGIA_MAX = 100.0
FUERZA_MUTACION = 0.1        # desviación estándar de la mutación, como fracción del rango del gen (0.1 = 10%)
RANGO_PROB_MUT = (0.01, 0.08)
COSTO_VISION = 0.01          # energía por tick por cada unidad del gen visión (mantener ojos y cerebro)
COSTO_VELOCIDAD = 0.01       # energía por tick por cada unidad del gen velocidad (mantener músculos), se mueva o no
COSTO_PASO = 0.02            # energía por cada paso que da
COSTO_ATRACTIVO = 0.05       # energía por tick por cada unidad de atractivo que muestra un adulto (mantener el "ornamento")
PROB_CAMBIO_DIRECCION = 0.1  # probabilidad por tick de cambiar de rumbo mientras explora buscando pareja
DIRECCIONES = [(-1, 0), (1, 0), (0, -1), (0, 1)]


class SerVivo:
    # --- Genes ---
    # Diccionario {nombre del gen: (mínimo, máximo)}. Cada especie le suma los suyos (ver Herbivoro.GENES).
    # Todo gen listado acá se genera al azar, se hereda y muta automáticamente.
    GENES = {"prob_mut": RANGO_PROB_MUT}

    # --- Parámetros de la especie ---
    # Son atributos de clase: cada especie (subclase) los redefine con sus propios valores.
    APORTE_GESTACION = None        # energía por tick que la hembra le pasa a la cría mientras gesta
    ENERGIA_MIN_GESTACION = None   # si la hembra baja de esta energía mientras gesta, pierde la cría
    VEJEZ_POR_MADUREZ = None       # empieza a envejecer a esta cantidad de veces su edad de madurez
    FACTOR_VEJEZ_MINIMO = None     # fracción de visión y velocidad que conserva al final (ej: 0.2 = 20%)

    def __init__(self, fila, columna, energia=None, sexo=None, edad=0, **genes):
        # **genes junta en un diccionario todos los genes que se pasen por nombre,
        # ej: Herbivoro(3, 4, vision=2.5) -> genes = {"vision": 2.5}
        self.fila = fila
        self.columna = columna
        self.sexo = sexo if sexo is not None else random.choice(["M", "H"])
        self.energia = energia if energia is not None else ENERGIA_MAX / 2
        self.edad = edad
        self.direccion = None          # rumbo que sigue mientras explora buscando pareja

        # Genes: los que vienen dados (heredados o pasados a mano) se usan tal cual,
        # los que faltan se generan al azar dentro del rango de la especie.
        desconocidos = set(genes) - set(self.GENES)
        if desconocidos:
            raise TypeError(f"Genes desconocidos para {type(self).__name__}: {desconocidos}")
        for nombre, rango in self.GENES.items():
            valor = genes.get(nombre)
            if valor is None:
                valor = random.uniform(*rango)
            setattr(self, nombre, valor)   # ej: setattr(self, "vision", 2.5) es lo mismo que self.vision = 2.5

        # Estado de la reproducción
        self.gestando = False          # hembra: está preñada / macho: está en su gestación macho
        self.ticks_gestacion = 0       # cuántos ticks lleva gestando
        self.energia_invertida = 0.0   # (solo hembras) energía que ya le pasó a la cría
        self.genes_padre = None        # (solo hembras) genes del macho con el que se apareó

    def esta_vivo(self):
        return self.energia > 0

    def genes(self):
        """Devuelve un diccionario {nombre: valor} con todos sus genes."""
        return {nombre: getattr(self, nombre) for nombre in self.GENES}

    def mutar(self, valor, rango):
        if random.random() < self.prob_mut:
            # El tamaño de la mutación es proporcional al rango del gen, así todos los genes
            # mutan "lo mismo" en términos relativos, sea su rango de 0.07 o de 130
            valor += random.gauss(0, FUERZA_MUTACION * (rango[1] - rango[0]))
            valor = np.clip(valor, rango[0], rango[1])
        return valor

    # --- Vejez ---
    def factor_edad(self):
        """1.0 de joven; desde el inicio de la vejez baja linealmente hasta FACTOR_VEJEZ_MINIMO.
        La vejez empieza a VEJEZ_POR_MADUREZ veces la edad de madurez (madurar rápido es
        envejecer rápido) y tarda lo mismo en llegar al deterioro máximo."""
        inicio_vejez = self.edad_madurez * self.VEJEZ_POR_MADUREZ
        if self.edad <= inicio_vejez:
            return 1.0
        deterioro = (self.edad - inicio_vejez) / inicio_vejez
        return max(self.FACTOR_VEJEZ_MINIMO, 1.0 - deterioro)

    def radio_vision_actual(self):
        # Radio que realmente ve hoy: su gen de visión, reducido por la edad
        return int(round(self.vision * self.factor_edad()))

    def pasos_este_tick(self):
        # Pasos que puede dar hoy: su gen de velocidad, reducido por la edad.
        # La parte fraccionaria es una probabilidad: con 2.3 da 2 pasos y un 30% de chances de un tercero.
        velocidad = self.velocidad * self.factor_edad()
        pasos = int(velocidad)
        if random.random() < velocidad - pasos:
            pasos += 1
        return pasos

    # --- Movimiento ---
    # (En estos métodos se usan min/max y comparaciones de Python en vez de np.clip y np.sign:
    #  con números sueltos, en lugar de arrays, Python puro es mucho más rápido que numpy.)
    def paso_al_azar(self, entorno):
        df, dc = random.choice(DIRECCIONES)
        self.fila = min(max(self.fila + df, 0), entorno.shape[0] - 1)
        self.columna = min(max(self.columna + dc, 0), entorno.shape[1] - 1)

    def paso_hacia(self, fila_destino, columna_destino):
        # Da un solo paso hacia el destino, por el eje en el que está más lejos
        df = fila_destino - self.fila
        dc = columna_destino - self.columna
        if df == 0 and dc == 0:
            return   # ya está en el destino
        if abs(df) >= abs(dc):
            self.fila += 1 if df > 0 else -1
        else:
            self.columna += 1 if dc > 0 else -1

    def distancia_a(self, otro):
        # Distancia en celdas contando las diagonales como 1 (estar "al lado" es distancia 1)
        return max(abs(otro.fila - self.fila), abs(otro.columna - self.columna))

    def mover(self, entorno):
        # Movimiento cuando no está buscando pareja. Por defecto al azar; cada especie lo
        # sobreescribe con su propio movimiento "a voluntad" (ej: el herbívoro busca pasto).
        # Devuelve cuántos pasos dio (cada paso cuesta energía).
        pasos = self.pasos_este_tick()
        for _ in range(pasos):
            self.paso_al_azar(entorno)
        return pasos

    def acercarse_a(self, otro):
        """Camina hacia otro individuo hasta quedar al lado (o quedarse sin pasos). Devuelve los pasos dados."""
        pasos_dados = 0
        for _ in range(self.pasos_este_tick()):
            if self.distancia_a(otro) <= 1:
                break
            self.paso_hacia(otro.fila, otro.columna)
            pasos_dados += 1
        return pasos_dados

    def explorar(self, entorno):
        """Búsqueda activa de pareja cuando no ve ninguna: camina con un rumbo sostenido
        (así recorre mucho más terreno que yendo al azar) y cada tanto cambia de rumbo.
        Devuelve cuántos pasos dio."""
        if self.direccion is None or random.random() < PROB_CAMBIO_DIRECCION:
            self.direccion = random.choice(DIRECCIONES)
        pasos = self.pasos_este_tick()
        for _ in range(pasos):
            fila = self.fila + self.direccion[0]
            columna = self.columna + self.direccion[1]
            if not (0 <= fila < entorno.shape[0] and 0 <= columna < entorno.shape[1]):
                # Llegó al borde del mapa: elige al azar otro rumbo que sí se pueda seguir
                posibles = [d for d in DIRECCIONES
                            if 0 <= self.fila + d[0] < entorno.shape[0] and 0 <= self.columna + d[1] < entorno.shape[1]]
                self.direccion = random.choice(posibles)
                fila = self.fila + self.direccion[0]
                columna = self.columna + self.direccion[1]
            self.fila, self.columna = fila, columna
        return pasos

    def accion_especifica(self, entorno):
        # Cada subclase define qué hace acá: comer pasto, cazar, etc.
        raise NotImplementedError("Cada subclase debe implementar accion_especifica()")

    def registro_de_fertiles(self, entorno, sexo):
        # Cada subclase indica dónde están anotados los individuos fértiles de su especie de un sexo:
        # devuelve (grilla con cuántos hay por celda, diccionario {(fila, columna): [individuos]})
        raise NotImplementedError("Cada subclase debe implementar registro_de_fertiles()")

    def step(self, entorno):
        """Un tick de vida. Devuelve la cría si nació en este tick, o None."""
        self.edad += 1

        # Movimiento: si es fértil busca pareja activamente (va hacia la que elige, o explora si no ve
        # ninguna); si no, se mueve según su especie (ej: el herbívoro busca pasto)
        pareja = None
        if self.puede_reproducirse():
            pareja = self.elegir_pareja(entorno)
            pasos = self.acercarse_a(pareja) if pareja is not None else self.explorar(entorno)
        else:
            pasos = self.mover(entorno)

        self.accion_especifica(entorno)

        # Gasto del tick: metabolismo basal + visión + velocidad + pasos dados + atractivo que muestra
        self.energia -= (self.gasto_metabolico
                         + COSTO_VISION * self.vision
                         + COSTO_VELOCIDAD * self.velocidad
                         + COSTO_PASO * pasos
                         + COSTO_ATRACTIVO * self.atractivo_expresado())

        hijo = None
        if self.gestando:
            hijo = self.avanzar_gestacion()
        elif (pareja is not None and self.distancia_a(pareja) <= 1
              and self.puede_reproducirse() and pareja.puede_reproducirse()
              and self.hay_interes_mutuo(pareja)):
            # Llegó al lado de la pareja elegida y los dos siguen dispuestos: se aparean
            self.aparearse_con(pareja)

        self.energia = min(self.energia, ENERGIA_MAX)
        return hijo

    # --- Cortejo ---
    # Cada individuo lleva los genes de los dos sexos, pero solo expresa los del suyo
    # (y le pasa todos a sus crías).
    def atractivo(self):
        return self.atractivo_macho if self.sexo == "M" else self.atractivo_hembra

    def exigencia(self):
        return self.exigencia_macho if self.sexo == "M" else self.exigencia_hembra

    def atractivo_expresado(self):
        # Solo los adultos muestran (y pagan) su atractivo
        return self.atractivo() if self.edad >= self.edad_madurez else 0.0

    def atractivo_percibido(self):
        # Lo que ven los demás: su gen de atractivo, reducido si está mal alimentado.
        # Así el atractivo es una señal honesta de su estado.
        return self.atractivo() * self.energia / ENERGIA_MAX

    def le_atrae(self, otro):
        # Decide según lo que percibe: el otro le atrae si supera su exigencia
        return otro.atractivo_percibido() >= self.exigencia()

    def hay_interes_mutuo(self, otro):
        return self.le_atrae(otro) and otro.le_atrae(self)

    # --- Reproducción sexual ---
    def puede_reproducirse(self):
        # Vale igual para machos y hembras
        return (not self.gestando
                and self.edad >= self.edad_madurez
                and self.energia >= 0.4 * ENERGIA_MAX)

    def elegir_pareja(self, entorno):
        """Mira, dentro de su radio de visión, a los individuos fértiles del otro sexo con los que
        hay interés mutuo, y elige el más atractivo (si empatan, el más cercano). None si no hay."""
        radio = self.radio_vision_actual()
        sexo_opuesto = "M" if self.sexo == "H" else "H"
        conteo, por_celda = self.registro_de_fertiles(entorno, sexo_opuesto)

        f0 = max(self.fila - radio, 0)
        f1 = min(self.fila + radio + 1, entorno.shape[0])
        c0 = max(self.columna - radio, 0)
        c1 = min(self.columna + radio + 1, entorno.shape[1])
        if not conteo[f0:f1, c0:c1].any():
            return None   # no ve a nadie fértil del otro sexo (lo más común: se descarta rápido)

        elegida, mejor_clave = None, None
        for df, dc in np.argwhere(conteo[f0:f1, c0:c1] > 0):
            for candidato in por_celda[(f0 + int(df), c0 + int(dc))]:
                # El registro se hizo al inicio del tick: confirmar que siga disponible
                if not candidato.puede_reproducirse() or not self.hay_interes_mutuo(candidato):
                    continue
                # Prefiere al más atractivo; entre iguales, al más cercano
                clave = (-candidato.atractivo_percibido(), self.distancia_a(candidato))
                if elegida is None or clave < mejor_clave:
                    elegida, mejor_clave = candidato, clave
        return elegida

    def aparearse_con(self, pareja):
        hembra, macho = (self, pareja) if self.sexo == "H" else (pareja, self)
        # La hembra queda preñada y guarda los genes del padre para la cría
        hembra.gestando = True
        hembra.ticks_gestacion = 0
        hembra.genes_padre = macho.genes()
        # El macho empieza su gestación macho: hasta que termine no puede volver a aparearse
        macho.gestando = True
        macho.ticks_gestacion = 0

    def avanzar_gestacion(self):
        """Avanza un tick de gestación. Devuelve la cría si nace, o None."""
        self.ticks_gestacion += 1

        if self.sexo == "M":
            # Gestación macho: un tiempo de espera; al terminar puede volver a aparearse
            if self.ticks_gestacion >= self.tiempo_gestacion_macho:
                self.terminar_gestacion()
            return None

        # Gestación hembra: le pasa energía a la cría en cada tick,
        # así una gestación más larga da una cría con más energía
        self.energia -= self.APORTE_GESTACION
        self.energia_invertida += self.APORTE_GESTACION

        # Si se quedó sin reservas (ej: hay poco pasto), pierde la cría y la energía invertida
        if self.energia < self.ENERGIA_MIN_GESTACION:
            self.terminar_gestacion()
            return None

        if self.ticks_gestacion >= self.tiempo_gestacion_hembra:
            hijo = self.crear_hijo(self.energia_invertida)
            self.terminar_gestacion()
            return hijo

        return None

    def terminar_gestacion(self):
        self.gestando = False
        self.ticks_gestacion = 0
        self.energia_invertida = 0.0
        self.genes_padre = None

    def crear_hijo(self, energia):
        """La cría nace en la celda de la madre, con la energía que ella le fue pasando.
        Cada gen se hereda de la madre o del padre (50% cada uno) y después puede mutar
        (con la probabilidad de mutación de la madre)."""
        genes_hijo = {}
        for nombre, rango in self.GENES.items():
            valor = random.choice([getattr(self, nombre), self.genes_padre[nombre]])
            genes_hijo[nombre] = self.mutar(valor, rango)
        # type(self) es la clase de la madre (ej: Herbivoro), así la cría es de su misma especie
        return type(self)(self.fila, self.columna, energia=energia, **genes_hijo)
