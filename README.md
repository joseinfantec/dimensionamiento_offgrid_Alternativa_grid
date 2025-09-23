## dimensionamiento_offgrid

Herramienta en Python para dimensionar sistemas off-grid híbridos (FV + BESS + generador diésel) a partir de perfiles horarios de irradiación y consumo. Permite:

- Simular la operación anual durante múltiples años, considerando degradación FV y BESS, eficiencias y límites de carga/descarga.
- Calcular métricas económicas: CAPEX, OPEX estimados, ahorro de combustible, NPV descontado, horas de operación del generador, etc.
- Optimizar el tamaño de PV y BESS por:
  - Búsqueda en malla (grid search) con refinamiento.
  - Un modelo MILP simple que selecciona entre conjuntos discretos de opciones.

### Estructura del proyecto

- `main.py`: punto de entrada. Carga datos desde Excel, configura parámetros y ejecuta simulación/optimizaciones de ejemplo.
- `data_loader.py`: lectura de la planilla Excel y transformación de datos (matriz 24×12 a 8760 y carga horaria 8760).
- `simulator.py`: simulación multianual de operación y cálculo económico (`SimulationConfig`, `simulate_operation`).
- `optimizer.py`: optimización por grid search con refinamiento; soporta ejecución paralela.
- `milp.py`: optimización MILP (Pulp) sobre opciones discretas de PV/BESS.
- `funciones.py`: utilidades para imprimir resultados en tablas (`print_results`, `print_results_reducidos`).
- `Versión_Final_Clientes_OFFGRID.xlsm`: ejemplo de planilla de entrada (no se versiona normalmente).

### Requisitos

- Python 3.9 o superior (Windows soportado; el script incluye `multiprocessing.freeze_support()`).
- Paquetes:
  - `numpy`
  - `pandas`
  - `openpyxl` (necesario para leer `.xlsm` con pandas)
  - `pulp` (solo si usarás la optimización MILP)

Instalación rápida de dependencias:

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install --upgrade pip
pip install numpy pandas openpyxl pulp
```

### Datos de entrada (Excel)

El archivo Excel y la hoja se configuran en `main.py`:

- Ruta: variable `path` en `main.py` (actualiza a tu ubicación local).
- Hoja: `sheet_name = "Gen_Cons_Horario"`.

Expectativas de formato (según `data_loader.py`):

- Irradiación 24×12: rango `AS:BD`, 24 filas (horas 0–23) × 12 columnas (enero–diciembre). Se leen con `read_irradiation_from_excel(...)`.
- Carga horaria 8760: columna `B` a partir de la fila 35 (índice base 1). Se leen con `read_load_hourly_from_excel(...)` y se valida tamaño 8760.

Si tu planilla usa otros rangos/hojas, ajusta `usecols`, `skiprows`, `nrows` y `sheet_name` en `data_loader.py` y `main.py`.

### Uso rápido (simulación de ejemplo)

1) Revisa y actualiza la ruta del Excel en `main.py`:

```python
path = r"C:\\Users\\TU_USUARIO\\ruta\\Versión_Final_Clientes_OFFGRID.xlsm"
sheet_name = "Gen_Cons_Horario"
```

2) Ejecuta el script principal:

```bash
python main.py
```

El script ejecuta una simulación con un ejemplo de tamaño `PV_test` y `E_test` y muestra por consola:

- NPV y CAPEX totales
- Tablas anuales: generación, consumo desde FV/BESS, consumo desde generador, pérdidas FV, horas de generador ON, gross savings

Para guardar tablas a Excel, puedes descomentar las líneas señaladas en `funciones.py`.

### Optimización por Grid Search (opcional)

En `main.py` hay un bloque comentado que ejecuta `grid_search_optimize(...)` de `optimizer.py`. Para usarlo:

1) Ajusta los rangos y resoluciones:

```python
best_grid, df_grid = grid_search_optimize(
    irr_8760, load_8760, cfg,
    PV_range=(100, 250),
    E_range=(30, 300),
    nPV=21,
    nE=21,
    parallel=True,
    nprocs=4
)
```

2) Descomenta el bloque correspondiente en `main.py` y vuelve a ejecutar. El resultado `best_grid` resume la mejor combinación con su NPV y métricas; `df_grid` contiene todas las evaluaciones.

Notas:
- En Windows, si usas `parallel=True`, ejecuta el script desde `if __name__ == "__main__":` (ya está implementado en `main.py`).
- Puedes aumentar `nprocs` según tus núcleos.

### Optimización MILP (opcional)

`milp.py` incluye un ejemplo con `pulp`. Define listas discretas de opciones:

```python
PV_options = list(range(10, 301, 10))
E_options = list(range(0, 501, 50))
```

Descomenta el bloque MILP en `main.py` y ejecuta. Requisitos: `pip install pulp`.

### Resultados y métricas clave

`simulate_operation` devuelve, entre otros:

- `capex`: inversión inicial estimada
- `npv`: valor presente neto (descontado por año)
- `fuel_by_year`: energía cubierta por el generador
- `assets_opex_by_year`: OPEX estimado de PV+BESS y del generador
- `consumo_desde_pv` / `consumo_desde_bess`: energía servida por FV/BESS
- `losses_by_year`: excedentes FV no aprovechados
- `horas_generador_on`: horas con generador en operación

Los parámetros económicos y técnicos se controlan desde `SimulationConfig` en `simulator.py` (tasas, O&M, inflación, degradación, límites de carga/descarga, etc.).

### Problemas comunes

- Error por tamaño distinto de 8760: revisa que la columna de carga tenga exactamente 8760 valores no vacíos.
- Error al leer `.xlsm`: asegúrate de tener `openpyxl` instalado y que la ruta sea válida.
- Resultados inesperados: verifica unidades (kWp/kWh), tarifas y factores en `SimulationConfig`.

### Licencia

Uso interno/educativo. Adapta según tus necesidades.
