from multiprocessing import Pool
import numpy as np
from simulator import simulate_operation
import pandas as pd



def evaluate_grid_point(args):
    PV, E, irr, load, cfg = args
    res = simulate_operation(PV, E, irr, load, cfg)
    return (PV, E, res['npv'], res['feasible'], res['capex'],
            res['assets_opex_by_year'],
            res['fuel_liters_hybrid_by_year'],
            res['fuel_liters_genonly_by_year'],
            res['fuel_cost_hybrid_by_year'],
            res['fuel_cost_genonly_by_year'],
            res['soc_end_by_year'],
            res['losses_by_year'],
            #res.get('hourly_capture'),
            #res.get('net_savings_by_year'),
            #res.get('horas_generador_on'),
            #res.get('generacion'),
            res.get('payback_year'))

def grid_search_optimize(irr_annual, load_annual, cfg, PV_range=(0,500), E_range=(0,500), nPV=21, nE=21, parallel=True, nprocs=4, refine_steps=2, refine_factor=0.25):
    PV_min, PV_max = PV_range
    E_min, E_max = E_range
    PV_grid = np.linspace(PV_min, PV_max, nPV)
    E_grid = np.linspace(E_min, E_max, nE)
    tasks = [(pv, eb, irr_annual, load_annual, cfg) for pv in PV_grid for eb in E_grid]

    results = []
    if parallel:
        with Pool(processes=nprocs) as pool:
            for r in pool.imap_unordered(evaluate_grid_point, tasks):
                results.append(r)
    else:
        for t in tasks:
            results.append(evaluate_grid_point(t))


    df = pd.DataFrame(results, columns=['PV_kWp', 'E_bess_kWh', 'npv', 'Feasible',
                                        'CAPEX', 'Assets_OPEX_by_year', 'Fuel_liters_hybrid_by_year', 'Fuel_liters_genonly_by_year',
                                        'Fuel_cost_hybrid_by_year', 'Fuel_cost_genonly_by_year',
                                        'SOC_end_by_year', 'Losses_by_year', 'Payback_yr', ])
    df_factible = df[df['Feasible'] == True]
    best = None
    if not df_factible.empty:
        idx = df_factible['npv'].idxmax()
        best_row = df_factible.loc[idx]
        best = dict(best_row)

    # Refinamiento
    for step in range(refine_steps):
        if best is None:
            break
        pv0 = best['PV_kWp']
        e0 = best['E_bess_kWh']
        pv_half_span = (PV_max - PV_min) * (refine_factor / (2 ** (step+1)))
        e_half_span = (E_max - E_min) * (refine_factor / (2 ** (step+1)))
        new_PV_min = max(PV_min, pv0 - pv_half_span)
        new_PV_max = min(PV_max, pv0 + pv_half_span)
        new_E_min = max(E_min, e0 - e_half_span)
        new_E_max = min(E_max, e0 + e_half_span)

        PV_grid = np.linspace(new_PV_min, new_PV_max, nPV)
        E_grid = np.linspace(new_E_min, new_E_max, nE)
        tasks = [(pv, eb, irr_annual, load_annual, cfg) for pv in PV_grid for eb in E_grid]

        new_results = []
        if parallel:
            with Pool(processes=nprocs) as pool:
                for r in pool.imap_unordered(evaluate_grid_point, tasks):
                    new_results.append(r)
        else:
            for t in tasks:
                new_results.append(evaluate_grid_point(t))

        new_df = pd.DataFrame(new_results, columns=['PV_kWp', 'E_bess_kWh', 'npv', 'Feasible',
                                                    'CAPEX', 'Assets_OPEX_by_year', 'Fuel_by_year',
                                                    'SOC_end_by_year', 'Losses_by_year', 'Payback_yr'])
        df = pd.concat([df, new_df], ignore_index=True)
        df_factible = df[df['Feasible'] == True]
        if df_factible.empty:
            best = None
        else:
            idx = df_factible['npv'].idxmax()
            best_row = df_factible.loc[idx]
            best = dict(best_row)

    # Enriquecer 'best' con métricas detalladas del simulador
    if best is not None:
        detailed = simulate_operation(best['PV_kWp'], best['E_bess_kWh'], irr_annual, load_annual, cfg)
        best['consumo_desde_pv'] = detailed.get('consumo_desde_pv', {})
        best['consumo_desde_bess'] = detailed.get('consumo_desde_bess', {})
        best['generación'] = detailed.get('generación', {})
        best['horas_generador_on'] = detailed.get('horas_generador_on', {})
        best['gross_savings'] = detailed.get('gross_savings', {})

    return best, df