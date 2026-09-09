# Intento de Simulación

## Descripción

**Intento de Simulación** es un modelo de simulación basado en agentes que
representa un ecosistema elemental sobre una grilla bidimensional de 300 × 300
celdas. El sistema integra tres componentes:

1. **Un entorno físico** con un campo de fertilidad estático generado mediante
   ruido de Perlin y un recurso renovable (pasto) cuya tasa de crecimiento
   depende de la estación del año.
2. **Una población de herbívoros** modelada como agentes autónomos que se
   desplazan por la grilla, consumen el recurso, gastan energía metabólica y
   se reproducen de forma asexual cuando superan un umbral energético.
3. **Un mecanismo de herencia con mutación**, por el cual cada descendiente
   recibe los rasgos del progenitor perturbados con ruido gaussiano, lo que
   permite observar deriva y selección de caracteres a lo largo de las
   generaciones.

El proyecto tiene fines didácticos y exploratorios: su objetivo es visualizar
cómo emergen dinámicas poblacionales (crecimiento, colapso, oscilaciones
estacionales) a partir de reglas locales simples.

## Requisitos

- Python 3.10 o superior
- Dependencias listadas en `requirements.txt`:
  - `numpy` — cálculo vectorizado sobre la grilla
  - `noise` — ruido de Perlin para el campo de fertilidad
  - `matplotlib` — visualización estática y animada

## Instalación

```bash
git clone https://github.com/MichelNahuel/Intento_de_Simulacion.git
cd Intento_de_Simulacion

python -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate

pip install -r requirements.txt
```

## Uso

Todos los scripts deben ejecutarse **desde el directorio raíz del proyecto**,
ya que los módulos se importan por nombre plano (`from Intento_de_ambiente import ...`).

### 1. Visualización animada de la simulación completa

```bash
python Intento_de_visualizar.py
```

Abre una ventana con dos paneles:

- **Panel izquierdo**: mapa del pasto (en tonos de verde) con los herbívoros
  superpuestos como puntos; el color indica el sexo (azul = M, rosa = H). El
  título muestra el tick actual, la estación y el tamaño de la población.
- **Panel derecho**: curva del tamaño de la población en función del tiempo.

La animación corre 100 fotogramas. Para cambiar la duración, la población
inicial o la velocidad, editar en `Intento_de_visualizar.py`:

```python
poblacion = crear_poblacion_inicial(50, entorno.shape)   # población inicial
ani = animation.FuncAnimation(fig, actualizar, frames=100, interval=50, blit=False)
#                                                   ^frames        ^ms entre frames
```

### 2. Corrida por consola (sin gráficos)

```bash
python Intento_de_herbivoro.py
```

Ejecuta la simulación durante `t` ticks e imprime el tamaño de la población
cada 20 ticks, además de un resumen final. Parámetros al inicio del archivo:

```python
n = 100     # cantidad de herbívoros iniciales
t = 1500    # cantidad de ticks a simular
```

### 3. Inspección del entorno

```bash
python Intento_de_ambiente.py
```

Avanza el entorno 200 ticks (sin herbívoros) y muestra dos mapas: el campo de
fertilidad (fijo) y el estado del pasto al final. Útil para calibrar las tasas
de crecimiento estacionales.

## Parámetros del modelo

| Constante | Archivo | Significado |
|---|---|---|
| `SHAPE` | `Intento_de_ambiente.py` | Dimensiones de la grilla (por defecto 300×300). |
| `PASTO_MAX` | `Intento_de_ambiente.py` | Capacidad máxima de pasto por celda. |
| `Tasa_crecimiento` | `Intento_de_ambiente.py` | Tasa de crecimiento del pasto por estación (primavera, verano, otoño, invierno). |
| `ENERGIA_MAX` | `Intento_de_ser_vivo.py` | Energía máxima de un individuo. |
| `FUERZA_MUTACION` | `Intento_de_ser_vivo.py` | Desvío estándar del ruido gaussiano aplicado en las mutaciones. |
| `RANGO_PROB_MUT` | `Intento_de_ser_vivo.py` | Rango de la probabilidad de mutación por rasgo. |
| `RANGO_GASTO_METABOLICO` | `Intento_de_herbivoro.py` | Rango del gasto energético por tick. |
| `RANGO_EFICIENCIA_COMER` | `Intento_de_herbivoro.py` | Energía obtenida por unidad de pasto consumido. |
| `CANTIDAD_COMER` | `Intento_de_herbivoro.py` | Pasto que intenta consumir el herbívoro por tick. |
| `COSTO_REPRODUCCION` | `Intento_de_herbivoro.py` | Energía que cuesta engendrar un descendiente. |

## Reglas de la simulación

**Entorno (por tick):**

1. Se incrementa el contador de ticks y se actualiza la estación
   (100 ticks por estación, ciclo de 4).
2. El pasto crece según
   `pasto += tasa_estación · fertilidad · (1 − pasto / PASTO_MAX)`,
   con el resultado recortado al intervalo `[0, PASTO_MAX]`. En invierno la
   tasa es negativa, por lo que el pasto decrece.

**Herbívoro (por tick):**

1. Se mueve una celda en una dirección aleatoria (arriba, abajo, izquierda o derecha).
2. Consume hasta `CANTIDAD_COMER` de pasto de su celda y gana
   `pasto_consumido · eficiencia_comer` de energía.
3. Paga su `gasto_metabolico`; la energía se limita a `ENERGIA_MAX`.
4. Si su energía es ≥ 40 % de `ENERGIA_MAX`, se reproduce: paga
   `COSTO_REPRODUCCION` y genera un descendiente en su misma celda con
   `COSTO_REPRODUCCION` de energía inicial.
5. Cuando su energía llega a cero, el individuo muere y se retira de la población.

**Herencia con mutación:** cada rasgo del descendiente
(`gasto_metabolico`, `eficiencia_comer`, `prob_mut`) se copia del progenitor y,
con probabilidad `prob_mut`, se le suma ruido gaussiano de desvío
`FUERZA_MUTACION`, recortando el valor a su rango válido.

## Estructura del proyecto

```
Intento_de_Simulacion/
├── Intento_de_ser_vivo.py     # Clase base SerVivo: energía, movimiento, mutación, reproducción
├── Intento_de_ambiente.py     # Clase Entorno: fertilidad (Perlin), pasto estacional, consumo
├── Intento_de_herbivoro.py    # Clase Herbivoro(SerVivo): alimentación y reproducción asexual
├── Intento_de_visualizar.py   # Animación matplotlib de la simulación completa
├── requirements.txt
└── README.md
```
