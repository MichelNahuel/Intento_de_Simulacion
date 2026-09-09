# Intento de Simulación

Simulación sencilla de un ecosistema en una grilla de 300×300, con estaciones,
crecimiento de pasto y una población de herbívoros que se mueven, comen, gastan
energía, se reproducen de forma asexual y mutan sus rasgos.

## Estructura

| Archivo | Rol |
|---|---|
| `Intento_de_ser_vivo.py` | Clase base `SerVivo`: energía, movimiento, mutación gaussiana, reproducción. |
| `Intento_de_ambiente.py` | Clase `Entorno`: fertilidad con ruido Perlin, crecimiento de pasto por estación, consumo. |
| `Intento_de_herbivoro.py` | Clase `Herbivoro(SerVivo)`: come pasto, eficiencia alimentaria, reproducción con mutación. |
| `Intento_de_visualizar.py` | Animación con matplotlib: mapa de pasto + herbívoros y curva de población en el tiempo. |

## Uso

```bash
pip install -r requirements.txt

# Animación interactiva
python Intento_de_visualizar.py

# Corrida sin gráficos (solo conteo de población por consola)
python Intento_de_herbivoro.py

# Ver el entorno (fertilidad y pasto tras 200 ticks)
python Intento_de_ambiente.py
```

Los módulos se importan por nombre plano (`from Intento_de_ambiente import ...`),
así que hay que ejecutarlos desde esta carpeta.

## Modelo, en breve

- **Estaciones**: primavera / verano / otoño / invierno, 100 ticks cada una. La tasa de
  crecimiento del pasto cambia por estación (negativa en invierno).
- **Pasto**: `pasto += tasa · fertilidad · (1 − pasto/PASTO_MAX)`, recortado a `[0, 1]`.
- **Herbívoro**: cada tick se mueve al azar, come hasta `CANTIDAD_COMER` de pasto,
  gana `pasto · eficiencia_comer` de energía y paga su `gasto_metabolico`.
- **Reproducción**: si la energía supera el 40 % del máximo, crea un hijo por
  `COSTO_REPRODUCCION` de energía; los rasgos del hijo pueden mutar con ruido gaussiano.
