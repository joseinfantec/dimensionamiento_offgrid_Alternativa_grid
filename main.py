from data_loader import read_irradiation_from_excel, expand_monthly_matrix_to_annual_hourly, read_load_hourly_from_excel
from simulator import SimulationConfig, simulate_operation
from optimizer import grid_search_optimize
from milp import milp_optimize
from funciones import *

# ===========================
# Carga de datos
# ===========================
path = r"C:\Users\josem\OneDrive\Escritorio\Versión_Final_Clientes_OFFGRID.xlsm"
sheet_name = "Gen_Cons_Horario"

# Cargar matriz mensual de irradiación (24h x 12 meses)
mat_24x12 = read_irradiation_from_excel(path, sheet_name=sheet_name)

# Expandir a perfil horario anual (8760 horas)
irr_8760 = expand_monthly_matrix_to_annual_hourly(mat_24x12)

# Cargar consumo horario desde columna B (índice 1)
load_8760 = read_load_hourly_from_excel(path, sheet_name=sheet_name)

# ===========================
# Configuración del sistema
# ===========================
cfg = SimulationConfig(
    N_years=15,
    r=0.07,
    ef_charge=0.99,
    ef_discharge=0.99,
    DOD=0.9,
    charge_rate=0.99,
    discharge_rate=0.99,
    pv_deg_rate=0.0045,
    C_pv_kWp=721155,
    C_bess_kWh=240385,
    C_gen_kWh=288.462,
    C_om_pv_kW_yr=100000,
    C_om_bess_kWh_yr=50000,
    cpi=0.02,
    diesel_inflation=0.04,
    bess_capacity_factors=[1,0.95,0.925,0.9,0.875,0.85,0.825,0.8,0.775,0.75,0.725,0.7,0.675,0.65,0.625,0.6]
)

# ===========================
# Simulación de operación (ejemplo)
# ===========================

if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()   

    PV_test = 156  # kWp
    E_test = 491  # kWh

    #sim_results = simulate_operation(PV_test, E_test, irr_8760, load_8760, cfg)
    #print("===== Para PV = ", PV_test, "kWp y BESS =", E_test, "kWh =====")
    #print_results("Resultados de simulación ejemplo", sim_results)


# ===========================
# Optimización Grid Search
# ===========================

    best_grid, df_grid = grid_search_optimize(
        irr_8760, load_8760, cfg,
        PV_range=(100, 180),
        E_range=(300, 500),
        nPV=21,
        nE=21,
        parallel=True,
        nprocs=4
    )
    # La dejé comentada, si no funciona el código tengo que borrar el #
    #print("Best grid:", best_grid)


    if best_grid is not None:
        print_results_reducidos("Mejor PV+BESS (Grid Search)", best_grid)
    else:
        print("No se encontró una solución factible en Grid Search.")

# ===========================
# Optimización MILP
# ===========================
'''''
PV_options = list(range(100, 201, 10))
E_options = list(range(300, 601, 50))

best_pv, best_e, best_res = milp_optimize(
    irr_annual=irr_8760,
    load_annual=load_8760,
    cfg=cfg,
    PV_options=PV_options,
    E_options=E_options
)

print("\n--- Mejor PV+BESS (MILP) ---")
print(f"PV: {best_pv} kWp, BESS: {best_e} kWh")
print(f"NPV: {best_res['npv']:.2f}")
'''''