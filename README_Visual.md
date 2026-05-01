# Hill Climbing & Simulated Annealing

Optimización de la posición de hospitales mediante **Hill Climbing** y **Simulated Annealing**.
El repositorio incluye tanto la lógica del algoritmo como un visualizador gráfico paso a paso.

---

## Archivos

| Archivo             | Descripción                                                              |
|---------------------|--------------------------------------------------------------------------|
| `utils.py`          | Funciones de utilidad: mapa, costos, movimientos, distancia Manhattan    |
| `hc.py`             | Algoritmos HC y SA (versión normal + generadores paso a paso)            |
| `main.py`           | Ejecución rápida en consola con un mapa de ejemplo                       |
| `visualizer_hc.py`  | **Visualizador gráfico pygame** (nuevo en Semana 6)                      |

---

## Funciones

### utils.py

- `is_free_to_move(map, move)` — Verifica si una posición está vacía
- `is_valid_move(map, move)` — Verifica si una posición está dentro del mapa
- `find_objects(map, target_object_symbol)` — Retorna coordenadas de todos los objetos del tipo dado
- `result(map, hospital_coordinates, target_move)` — Retorna un nuevo mapa después de mover un hospital
- `manhattan(pos, pos_2)` — Calcula distancia Manhattan entre dos coordenadas
- `cost(map)` — Retorna el costo total del mapa (suma de distancias hospital→casa)
- `move(pos, pos_2)` — Suma dos tuplas de coordenadas
- `actions(map, hospital_position)` — Retorna movimientos adyacentes válidos para un hospital

### hc.py

- `hill_climbing(grid)` — Optimiza posiciones con Hill Climbing hasta no encontrar mejora
- `hill_climbing_steps(grid)` — **Generador** que hace `yield` de cada estado intermedio evaluado
- `simulated_annealing(grid, T_min, T_initial, cooling_rate)` — Optimiza con Simulated Annealing
- `simulated_annealing_steps(grid, T_min, T_initial, cooling_rate)` — **Generador** paso a paso para SA

Cada `yield` del generador produce un diccionario con:

```python
{
    "grid":           current_map,      # mapa actual
    "current_cost":   current_cost,     # costo actual
    "hospital":       hospital,         # hospital evaluado
    "candidate_move": candidate_move,   # movimiento candidato
    "candidate_map":  candidate_map,    # mapa resultante del candidato
    "candidate_cost": candidate_cost,   # costo del candidato
    "best_map":       best_map,         # mejor mapa encontrado hasta ahora
    "best_cost":      best_cost,        # mejor costo encontrado hasta ahora
    "accepted":       True/False,       # ¿fue aceptado el movimiento?
    "done":           True/False,       # ¿terminó el algoritmo?
    "message":        "...",            # descripción legible del paso
}
```

---

## Instalación

```bash
pip install -r requirements.txt
```

---

## Ejecución

### Visualizador gráfico (recomendado)

**Windows:**
```bash
python visualizer_hc.py
```

**Linux/macOS:**
```bash
python3 visualizer_hc.py
```

### Controles del visualizador

| Tecla       | Acción                              |
|-------------|-------------------------------------|
| `ESPACIO`   | Play / Pause                        |
| `N`         | Avanzar un paso                     |
| `R`         | Reiniciar                           |
| `1`         | Cambiar a Hill Climbing             |
| `2`         | Cambiar a Simulated Annealing       |
| `↑ / ↓`    | Aumentar / reducir velocidad        |
| `ESC`       | Salir                               |

También puedes hacer clic en los botones del panel lateral.

### Ejecución rápida en consola

**Windows:**
```bash
python main.py
```

**Linux/macOS:**
```bash
python3 main.py
```

Imprime:
1. El mapa original.
2. El mapa optimizado después de aplicar Hill Climbing.

### Uso con mapa personalizado

```python
import hc
import utils
from tabulate import tabulate

custom_map = [
    [None, None, utils.OBJECT_HOSPITAL, None],
    [utils.OBJECT_HOUSE, None, None, None],
    [None, None, None, utils.OBJECT_HOUSE],
]

solved_map = hc.hill_climbing(custom_map)
print(tabulate(solved_map, tablefmt="grid", floatfmt=".2f"))
```

---

## Pruebas

### Windows

```bash
python -m pytest
```

### Linux/macOS

```bash
pytest
```

Comandos útiles:

```bash
# Archivo específico
python -m pytest tests/test_utils.py
python -m pytest tests/test_hill_climbing.py

# Función específica
python -m pytest tests/test_utils.py::test_function_name

# Por patrón
python -m pytest -k "test_name"

# Sin cobertura (más rápido)
python -m pytest --no-cov
```

---

## Contribuciones

1. Haz un fork del repositorio.
2. Crea una rama para tu cambio.
3. Haz tu actualización y mantenla enfocada.
4. Ejecuta las pruebas antes de enviar.
5. Abre un Pull Request con una descripción clara.

Por favor mantén los PRs pequeños, legibles y relacionados a una sola mejora.
