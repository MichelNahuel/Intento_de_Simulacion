# Intento de Simulación

Simulación de un ecosistema basada en agentes, escrita en Python, para practicar
**algoritmos genéticos**. Una población de herbívoros vive sobre un mapa de pasto
que cambia con las estaciones: cada animal percibe lo que tiene alrededor, decide
hacia dónde moverse, come, gasta energía, envejece, busca pareja y se reproduce.
Sus crías heredan una mezcla de los genes de ambos padres, con mutaciones, así que
con el paso de las generaciones la población **evoluciona**: los genes que ayudan a
sobrevivir y reproducirse se vuelven más comunes.

El proyecto es didáctico y exploratorio: la idea es observar cómo, a partir de
reglas locales simples, aparecen dinámicas poblacionales (crecimiento, colapsos,
ciclos estacionales) y cambios evolutivos.

---

## Qué hace la simulación

### El mundo
- Un mapa de **300 × 300 celdas**. Cada celda tiene **pasto** (de 0 a 1) y una
  **fertilidad** fija, generada con ruido de Perlin para que haya zonas ricas y
  zonas pobres.
- El tiempo avanza en **ticks**. Cada **100 ticks cambia la estación**
  (primavera → verano → otoño → invierno, y vuelve a empezar).
- En primavera y verano el pasto **crece** (más rápido en las celdas fértiles);
  en otoño e invierno **se seca**. El invierno es la época de escasez.

### Los herbívoros
Cada herbívoro tiene energía, edad, sexo y un conjunto de **genes**. En cada tick:

1. **Se mueve.**
   - Si es **fértil**, **busca pareja**: mira a su alrededor y camina hacia el
     individuo del otro sexo que más le atrae (y al que él también atrae). Si no
     ve a nadie, explora el mapa con rumbo sostenido.
   - Si **no es fértil** (es joven, está gestando o tiene poca energía), **busca
     pasto**: se queda donde hay suficiente o camina hacia la celda más
     atractiva que ve, teniendo en cuenta si le gusta estar cerca de otros.
2. **Come** el pasto de su celda y gana energía.
3. **Gasta energía**: metabolismo, mantener la visión y la velocidad, cada paso
   que da y (si es adulto) mostrar su atractivo.
4. **Se reproduce**: si llegó al lado de la pareja que eligió y los dos siguen
   interesados, se aparean. La hembra gesta y le va pasando energía a la cría
   hasta dar a luz; el macho espera un tiempo antes de poder volver a aparearse.
5. **Envejece**: después de cierta edad ve y se mueve cada vez menos.
6. **Muere** si se queda sin energía.

### La evolución
- Cada gen de una cría viene **de la madre o del padre** (50 % cada uno) y puede
  **mutar** un poco.
- Casi todos los genes tienen **ventajas y costos**, así que no hay un "valor
  perfecto": por ejemplo, ver más lejos ayuda a encontrar comida y pareja, pero
  cuesta energía en cada tick; una gestación larga da crías más fuertes, pero
  menos crías.
- Hay **selección sexual**: los individuos eligen pareja según su atractivo, y
  cada uno tiene su propio nivel de exigencia.

---

## Instalación

Requiere **Python 3.10 o superior**.

```bash
git clone https://github.com/MichelNahuel/Intento_de_Simulacion.git
cd Intento_de_Simulacion

python -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate

pip install -r requirements.txt
```

Dependencias (`requirements.txt`):
- `numpy` — cálculos sobre la grilla
- `noise` — ruido de Perlin para la fertilidad
- `matplotlib` — gráficos y animación

---

## Cómo usarla

> **Importante:** todos los comandos se ejecutan **desde la carpeta del proyecto**,
> porque los módulos se importan por nombre (`from Intento_de_ambiente import ...`).

### 1. Ver la simulación animada

```bash
python Intento_de_visualizar.py
```

Se abre una ventana con dos paneles:

- **Izquierda**: el mapa de pasto (verde más oscuro = más pasto) con los
  herbívoros encima (azul = macho, rosa = hembra). El título muestra el tick,
  la estación y la población.
- **Derecha**: la cantidad de herbívoros a lo largo del tiempo.

La simulación **sigue corriendo hasta que cerrás la ventana**. Con la barra de
herramientas de matplotlib podés hacer zoom sobre el mapa.

Para cambiar la población inicial o la velocidad de la animación, editá en
`Intento_de_visualizar.py`:

```python
poblacion = crear_poblacion_inicial(50, entorno.shape)   # cantidad de herbívoros al inicio
ani = animation.FuncAnimation(fig, actualizar, frames=100, interval=50, blit=False)
#                                                          ^ milisegundos entre cuadros
```

### 2. Correrla por consola (sin gráficos, más rápido)

```bash
python Intento_de_herbivoro.py
```

Imprime la población cada 20 ticks y un resumen al final. Los parámetros están
al inicio del archivo:

```python
n = 100     # cantidad de herbívoros al inicio
t = 1500    # cantidad de ticks a simular (400 ticks = 1 año)
```

### 3. Ver solo el entorno

```bash
python Intento_de_ambiente.py
```

Avanza el entorno 200 ticks sin animales y muestra el mapa de fertilidad y el
estado del pasto. Sirve para ajustar las tasas de crecimiento del pasto.

### 4. Repetir exactamente la misma corrida

Por defecto cada corrida sale distinta. Para comparar el efecto de un cambio en
el código conviene repetir la misma corrida: poné un número en `SEMILLA`, en
`Intento_de_ambiente.py`:

```python
SEMILLA = 42     # None = cada corrida sale distinta
```

El mapa de fertilidad es siempre el mismo (usa su propia semilla fija).

### 5. Ver cómo evolucionaron los genes

La animación y la consola muestran la población, pero no los genes. Para verlos,
guardá esto como `ver_genes.py` en la carpeta del proyecto y corré
`python ver_genes.py`:

```python
import numpy as np
from Intento_de_ambiente import Entorno, fijar_semilla
from Intento_de_herbivoro import Herbivoro, crear_poblacion_inicial, simular_tick

fijar_semilla(42)
entorno = Entorno(seed=1)
poblacion = crear_poblacion_inicial(1000, entorno.shape)

for tick in range(400):          # 400 ticks = 1 año
    poblacion = simular_tick(entorno, poblacion)

print("Población:", len(poblacion))
if poblacion:
    for gen in Herbivoro.GENES:
        valores = [getattr(h, gen) for h in poblacion]
        print(f"{gen:25s} promedio {np.mean(valores):.2f}")
```

### Consejos

- **Empezá con una población grande (por ejemplo 1000).** Como la reproducción
  es sexual y los individuos eligen pareja, con pocos animales en un mapa tan
  grande casi no se encuentran y la población tiende a extinguirse (ver
  [Estado actual](#estado-actual-y-comportamiento-conocido)).
- **Cuanto más grande la población, más lenta la simulación.** Para corridas
  largas usá la consola en vez de la animación.
- Para probar un cambio, fijá `SEMILLA` y compará varias corridas: una sola
  corrida puede engañar.

---

## Genes

Cada especie declara sus genes en el diccionario `GENES = {nombre: (mínimo, máximo)}`
(ver `Herbivoro.GENES`). Todo gen listado ahí se genera al azar en la población
inicial, se hereda y muta automáticamente: **agregar un gen nuevo es agregar una
línea**. Machos y hembras llevan todos los genes (aunque algunos solo se expresen
en un sexo) y los pasan a sus crías.

| Gen | Rango | Qué hace | Ventaja / costo |
|---|---|---|---|
| `prob_mut` | 0.01 – 0.08 | Probabilidad de que cada gen mute al pasar a la cría. | La población "descubre" su tasa de mutación. |
| `gasto_metabolico` | 0.1 – 1.5 | Energía basal por tick; también cuánto pasto puede comer por tick. | Come más, pero gasta más. |
| `eficiencia_comer` | 1.1 – 2.0 | Energía obtenida por unidad de pasto. | — |
| `vision` | 1 – 6 | Radio de visión (en celdas). | Encuentra comida y pareja; cuesta energía cada tick. |
| `velocidad` | 0.5 – 4 | Pasos por tick. | Llega antes; cuesta energía cada tick y por paso. |
| `comunitario` | -1 – 1 | Tendencia a acercarse (> 0) o alejarse (< 0) de otros al buscar pasto. | Compañía vs. competencia por el pasto. |
| `edad_madurez` | 20 – 150 | Edad a partir de la cual puede reproducirse. | Madurar rápido es envejecer rápido. |
| `tiempo_gestacion_hembra` | 10 – 40 | Ticks de gestación (= energía con la que nace la cría). | Más crías vs. crías más fuertes. |
| `tiempo_gestacion_macho` | 5 – 50 | Ticks que un macho espera para volver a aparearse. | — |
| `atractivo_macho` | 0 – 1 | Cuán atractivo es un macho (solo se expresa en machos). | Consigue pareja; mostrarlo cuesta energía. |
| `atractivo_hembra` | 0 – 1 | Cuán atractiva es una hembra (solo se expresa en hembras). | Consigue pareja; mostrarlo cuesta energía. |
| `exigencia_macho` | 0 – 1 | Atractivo mínimo que un macho acepta en una hembra. | Parejas más atractivas vs. menos oportunidades. |
| `exigencia_hembra` | 0 – 1 | Atractivo mínimo que una hembra acepta en un macho. | Parejas más atractivas vs. menos oportunidades. |

---

## Reglas detalladas

### Entorno (en cada tick)
1. Avanza el contador de ticks y se actualiza la estación (100 ticks por estación).
2. **Pasto:**
   - tasa positiva (crece): `pasto += tasa · fertilidad · (1 − pasto / PASTO_MAX)`
   - tasa negativa (se seca): `pasto += tasa · pasto` (pierde un porcentaje de lo que tiene)
   - el resultado se recorta a `[0, PASTO_MAX]`.
3. Se registra dónde está cada herbívoro: cuántos hay por celda, cuántos en el
   bloque 3×3 de cada celda, y qué machos y hembras son fértiles. Así los
   animales pueden percibirse entre sí.

### Vejez
La vejez empieza a `VEJEZ_POR_MADUREZ · edad_madurez` ticks. Desde ahí la visión
y la velocidad bajan linealmente hasta `FACTOR_VEJEZ_MINIMO` (20 %), que se
alcanza al cabo de otro período igual.

### Fertilidad y cortejo
- **Fértil:** no está gestando, tiene al menos `edad_madurez` ticks y energía ≥ 40 % de `ENERGIA_MAX`.
- **Atractivo percibido** por los demás: `atractivo · energía / ENERGIA_MAX`
  (mal alimentado se ve menos atractivo).
- **Le atrae** otro individuo si su atractivo percibido es ≥ su propia exigencia.
  Hay **interés mutuo** si a cada uno le atrae el otro.

### Herbívoro (en cada tick)
1. Aumenta su edad en 1.
2. **Movimiento.** Puede dar hasta `velocidad · factor_edad` pasos (la parte
   fraccionaria es la probabilidad de un paso extra).
   - **Fértil → busca pareja:** entre los fértiles del otro sexo que ve (radio
     `round(vision · factor_edad)`) con interés mutuo, elige al más atractivo
     (el más cercano si empatan) y camina hacia él hasta quedar al lado. Si no
     ve a nadie, **explora** con un rumbo que cambia con probabilidad
     `PROB_CAMBIO_DIRECCION` por tick o al llegar al borde del mapa.
   - **No fértil → busca pasto.** En cada paso:
     - si en su celda hay pasto suficiente para comer ese tick, se queda;
     - si no tiene destino (o ya llegó), puntúa cada celda visible con
       `pasto + comunitario · PESO_COMUNITARIO · vecinos` y elige la mejor
       (la más cercana si empatan) como destino;
     - da un paso hacia el destino;
     - si su propia celda es la mejor, se queda si tiene algo de pasto o se
       mueve al azar si está vacía.
3. **Come** hasta `FACTOR_COMER · gasto_metabolico` de pasto y gana `pasto_comido · eficiencia_comer`.
4. **Gasta:** `gasto_metabolico + COSTO_VISION · vision + COSTO_VELOCIDAD · velocidad + COSTO_PASO · pasos + COSTO_ATRACTIVO · atractivo` (el último término, solo adultos).
5. **Reproducción:**
   - Si quedó a distancia ≤ 1 (contando diagonales) de la pareja elegida, y los
     dos siguen fértiles y con interés mutuo, se aparean.
   - **Gestación hembra:** durante `tiempo_gestacion_hembra` ticks le pasa
     `APORTE_GESTACION` de energía por tick a la cría. Si su energía baja de
     `ENERGIA_MIN_GESTACION`, pierde la cría. Al terminar, la cría nace en su
     celda con la energía acumulada y sexo al azar.
   - **Gestación macho:** no puede volver a aparearse hasta que pasen
     `tiempo_gestacion_macho` ticks.
6. La energía se limita a `ENERGIA_MAX`; con energía ≤ 0 muere.

La población inicial recibe genes al azar y edades al azar por debajo de su
`edad_madurez`, para que no todos lleguen a reproducirse en el mismo tick.

### Herencia
Cada gen de la cría se copia de la madre o del padre (50 % cada uno) y, con
probabilidad `prob_mut` (de la madre), se le suma ruido gaussiano de desvío
`FUERZA_MUTACION · (ancho del rango del gen)`, recortando al rango válido.

---

## Parámetros del modelo

| Constante | Archivo | Significado |
|---|---|---|
| `SHAPE` | `Intento_de_ambiente.py` | Tamaño de la grilla (300×300). |
| `PASTO_MAX` | `Intento_de_ambiente.py` | Pasto máximo por celda. |
| `SEMILLA` | `Intento_de_ambiente.py` | Semilla de `random` y `numpy`; `None` = corridas distintas. |
| `Tasa_crecimiento` | `Intento_de_ambiente.py` | Tasa del pasto por estación (positiva crece, negativa se seca). |
| `ENERGIA_MAX` | `Intento_de_ser_vivo.py` | Energía máxima de un individuo. |
| `FUERZA_MUTACION` | `Intento_de_ser_vivo.py` | Tamaño de una mutación, como fracción del rango del gen. |
| `RANGO_PROB_MUT` | `Intento_de_ser_vivo.py` | Rango del gen `prob_mut`. |
| `COSTO_VISION` | `Intento_de_ser_vivo.py` | Energía por tick por unidad de `vision`. |
| `COSTO_VELOCIDAD` | `Intento_de_ser_vivo.py` | Energía por tick por unidad de `velocidad`, se mueva o no. |
| `COSTO_PASO` | `Intento_de_ser_vivo.py` | Energía por cada paso. |
| `COSTO_ATRACTIVO` | `Intento_de_ser_vivo.py` | Energía por tick por unidad de atractivo que muestra un adulto (0 = sin costo). |
| `PROB_CAMBIO_DIRECCION` | `Intento_de_ser_vivo.py` | Probabilidad por tick de cambiar de rumbo al explorar. |
| `RANGO_*` | `Intento_de_herbivoro.py` | Rangos de los genes del herbívoro. |
| `FACTOR_COMER` | `Intento_de_herbivoro.py` | Pasto que puede comer por tick = `FACTOR_COMER · gasto_metabolico`. |
| `PESO_COMUNITARIO` | `Intento_de_herbivoro.py` | Peso de cada vecino frente al pasto al elegir destino. |
| `PASTO_MINIMO_VISIBLE` | `Intento_de_herbivoro.py` | Pasto por debajo del cual una celda se considera vacía. |
| `Herbivoro.APORTE_GESTACION` | `Intento_de_herbivoro.py` | Energía por tick que la hembra pasa a la cría. |
| `Herbivoro.ENERGIA_MIN_GESTACION` | `Intento_de_herbivoro.py` | Por debajo de esta energía, la hembra pierde la cría. |
| `Herbivoro.VEJEZ_POR_MADUREZ` | `Intento_de_herbivoro.py` | La vejez empieza a esta cantidad de veces la `edad_madurez`. |
| `Herbivoro.FACTOR_VEJEZ_MINIMO` | `Intento_de_herbivoro.py` | Fracción de visión y velocidad que conserva un individuo muy anciano. |

---

## Estado actual y comportamiento conocido

Observaciones de corridas de prueba (3 semillas, 2000–4000 ticks):

- **Con 100 herbívoros iniciales la población tiende a extinguirse.** En un mapa
  de 90.000 celdas la pareja más cercana suele estar a unas 30 celdas y la visión
  alcanza 2–4, así que casi no se encuentran; y cuando se encuentran, el interés
  mutuo es poco frecuente mientras las exigencias no evolucionan hacia abajo
  (*efecto Allee*).
- **Con 1000 herbívoros iniciales la población sobrevive**: el primer invierno la
  reduce a ~250, y después los apareamientos aumentan año a año y la exigencia
  promedio baja.
- **El invierno es el principal cuello de botella**: el pasto casi desaparece y
  mueren sobre todo los individuos con pocas reservas.
- Sin depredadores, algunos genes derivan hacia valores extremos (por ejemplo, el
  gasto metabólico tiende a bajar); se espera que agregar carnívoros cambie esas
  presiones.

## Próximos pasos posibles
- Carnívoros (`Carnivoro(SerVivo)`) que cacen herbívoros.
- Exigencia que baje mientras un individuo pasa tiempo fértil sin pareja.
- Fertilidad del suelo dinámica (degradación por sobrepastoreo).

---

## Estructura del proyecto

```
Intento_de_Simulacion/
├── Intento_de_ser_vivo.py     # Clase base SerVivo: genes, energía, vejez, movimiento, cortejo, búsqueda de pareja, reproducción
├── Intento_de_ambiente.py     # Clase Entorno: fertilidad (Perlin), pasto estacional, consumo, registro de herbívoros, SEMILLA
├── Intento_de_herbivoro.py    # Clase Herbivoro(SerVivo): genes de la especie, búsqueda de pasto, alimentación, simular_tick()
├── Intento_de_visualizar.py   # Animación con matplotlib (mapa + curva de población)
├── requirements.txt
└── README.md
```
