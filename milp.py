from pulp import LpProblem, LpVariable, LpMaximize, lpSum, LpStatus
from simulator import simulate_operation, SimulationConfig

def milp_optimize(irr_annual, load_annual, cfg, PV_options, E_options):
    """
    Optimización MILP simplificada usando NPV como objetivo.
    PV_options y E_options son listas de posibles capacidades.
    """
    prob = LpProblem("PV_BESS_Optimization", LpMaximize)

    # Variables binarias para selección de PV y BESS
    x_pv = LpVariable.dicts("x_pv", PV_options, cat="Binary")
    x_e = LpVariable.dicts("x_e", E_options, cat="Binary")

    # Variables auxiliares para NPV de cada combinación
    npv_vars = {}
    for pv in PV_options:
        for eb in E_options:
            res = simulate_operation(pv, eb, irr_annual, load_annual, cfg)
            npv_vars[(pv, eb)] = res['npv']

    # Función objetivo: maximizar NPV
    prob += lpSum([npv_vars[(pv, eb)] * x_pv[pv] * x_e[eb] for pv in PV_options for eb in E_options])

    # Restricción: solo se puede elegir un PV y un BESS
    prob += lpSum([x_pv[pv] for pv in PV_options]) == 1
    prob += lpSum([x_e[eb] for eb in E_options]) == 1

    # Resolver
    prob.solve()

    # Obtener resultados
    best_pv = None
    best_e = None
    for pv in PV_options:
        if x_pv[pv].varValue > 0.5:
            best_pv = pv
            break
    for eb in E_options:
        if x_e[eb].varValue > 0.5:
            best_e = eb
            break

    best_res = simulate_operation(best_pv, best_e, irr_annual, load_annual, cfg)
    return best_pv, best_e, best_res
