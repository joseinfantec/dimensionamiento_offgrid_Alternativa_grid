import pandas as pd
import numpy as np


def read_irradiation_from_excel(path, sheet_name=None, usecols="AS:BD", skiprows=4, nrows=24, header=None):
    df = pd.read_excel(path, sheet_name=sheet_name, usecols=usecols, skiprows=skiprows, nrows=nrows, header=header)
    arr = df.to_numpy(dtype=float)
    if arr.shape != (24, 12):
        raise ValueError(f"Se esperaba matriz 24x12 desde Excel, se obtuvo shape={arr.shape}")
    return arr



def expand_monthly_matrix_to_annual_hourly(mat_24x12, days_in_month=None):
    if days_in_month is None:
        days_in_month = [31,28,31,30,31,30,31,31,30,31,30,31]
    if len(days_in_month) != 12:
        raise ValueError("days_in_month debe tener 12 elementos")

    hourly = []
    for j in range(12):
        perfil = mat_24x12[:, j]
        for _ in range(days_in_month[j]):
            hourly.extend(perfil.tolist())


    arr = np.array(hourly, dtype=float)
    return arr



def read_load_hourly_from_excel(path, sheet_name=None, expect_8760=True):
    # Forzamos a leer solo columna B y desde la fila 35 (skiprows=34)
    df = pd.read_excel(path, sheet_name=sheet_name, usecols="B", skiprows=34, header=None)

    vec = df.iloc[:, 0].dropna().to_numpy(dtype=float)

    if expect_8760 and vec.size != 8760:
        raise ValueError(f"Se esperaba 8760 valores en load, se encontraron {vec.size}")

    return vec


#if __name__ == "__main__":
#    path = r"C:\Users\josem\OneDrive\Escritorio\Versión_Final_Clientes_OFFGRID.xlsm"
#    sheet_name = "Gen_Cons_Horario"
#
#    load_8760 = read_load_hourly_from_excel(path, sheet_name=sheet_name)
#
#    print("Número de valores cargados:", len(load_8760))
#    print("\nPrimeras 10 horas de consumo:")
#    print(load_8760[:10])
#
#    print("\nÚltimas 10 horas de consumo:")
#    print(load_8760[-10:])
#
    # Verificar que no haya valores NaN
#    print("\n¿Hay valores NaN en los consumos?:", np.isnan(load_8760).any())