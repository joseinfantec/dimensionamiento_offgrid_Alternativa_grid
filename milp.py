from pulp import LpProblem, LpVariable, LpMaximize, lpSum
from simulator import simulate_operation, SimulationConfig

def milp_optimize(irr_annual, load_annual, cfg, PV_options, E_options):
    """
    Optimización lineal: selecciona exactamente una combinación (PV, E) que maximiza el NPV
    precomputado por simulate_operation sobre el horizonte de cfg.N_years.
    """
    # Precomputar NPV como constantes (parámetros del modelo)
    npv_map = {}
    for pv in PV_options:
        for eb in E_options:
            res = simulate_operation(pv, eb, irr_annual, load_annual, cfg)
            npv_map[(pv, eb)] = res['npv']

    # Modelo MILP
    prob = LpProblem("PV_BESS_Optimization", LpMaximize)

    # Variable binaria para cada par (pv, eb)
    y = LpVariable.dicts("y", [(pv, eb) for pv in PV_options for eb in E_options], cat="Binary")

    # Objetivo: maximizar NPV esperado
    prob += lpSum(npv_map[(pv, eb)] * y[(pv, eb)] for pv in PV_options for eb in E_options)

    # Restricción: elegir exactamente una combinación
    prob += lpSum(y[(pv, eb)] for pv in PV_options for eb in E_options) == 1

    # Resolver
    prob.solve()

    # Recuperar la mejor combinación
    best_pv = None
    best_e = None
    for pv in PV_options:
        for eb in E_options:
            var = y[(pv, eb)]
            if var.varValue is not None and var.varValue > 0.5:
                best_pv = pv
                best_e = eb
                break
        if best_pv is not None:
            break

    if best_pv is None or best_e is None:
        return None, None, None

    best_res = simulate_operation(best_pv, best_e, irr_annual, load_annual, cfg)
    return best_pv, best_e, best_res
