import pandas as pd

def print_results(title, results):
    print(f"\n--- {title} ---")
    print(f"NPV: {results['npv']:.2f}")
    pb = results.get('payback_year')
    if pb is not None:
        print(f"Payback (años): {pb:.1f}")
    print(f"Capex: {results['capex']:.2f}")

    years = sorted(results['fuel_by_year'].keys())

    data = {
        "Generación total": [results['generación'][y] for y in years],
        "Consumo desde PV": [results['consumo_desde_pv'][y] for y in years],
        "Consumo desde BESS": [results['consumo_desde_bess'][y] for y in years],
        "Consumo desde Genset": [results['fuel_by_year'][y] for y in years],
        "Pérdidas FV": [results['losses_by_year'][y] for y in years],
        #"SOC final": [results['soc_end_by_year'][y] for y in years],
        #"Opex PV+BESS+GEN": [results['assets_opex_by_year'][y] for y in years],
        "Horas generador ON": [results['horas_generador_on'][y] for y in years],
        "Gross Savings": [results['gross_savings'][y] for y in years],
        #"Fuel Savings": [results['fuel_savings_by_year'][y] for y in years],
    }

    df = pd.DataFrame(data, index=years)
    df.index.name = "Año"

    print("\nResultados por año:")
    print(df)

    # ✅ Guardar en Excel opcional
    # df.to_excel("resultados.xlsx")

    return df


def print_results_reducidos(title, best):
    if best is None:
        print(f"\n--- {title} ---")
        print("No se encontró una solución factible.")
        return None

    print(f"\n--- {title} ---")
    print(f"NPV: {best['npv']:.2f}")
    pb = best.get('Payback_yr') or best.get('payback_year')
    if pb is not None:
        print(f"Payback (años): {float(pb):.1f}")
    print(f"Capex: {best['CAPEX']:.2f}")
    print(f"PV: {best['PV_kWp']:.2f} kWp, BESS: {best['E_bess_kWh']:.2f} kWh")

    # Convertir a tabla anual con métricas solicitadas
    years = sorted(best['Fuel_by_year'].keys())

    # Claves esperadas que fueron añadidas en optimizer al 'best'
    consumo_pv = best.get('consumo_desde_pv') or {}
    consumo_bess = best.get('consumo_desde_bess') or {}
    generacion = best.get('generación') or {}
    gen_hours = best.get('horas_generador_on') or {}
    gross_savings = best.get('gross_savings') or {}

    data = {
        "Consumo desde Genset": [best['Fuel_by_year'].get(y, 0.0) for y in years],
        "Consumo desde FV": [consumo_pv.get(y, 0.0) for y in years],
        "Consumo desde BESS": [consumo_bess.get(y, 0.0) for y in years],
        "Pérdidas FV": [best['Losses_by_year'].get(y, 0.0) for y in years],
        "Horas generador ON": [gen_hours.get(y, 0) for y in years],
        "Gross Savings": [gross_savings.get(y, 0.0) for y in years],
        "Generación FV": [generacion.get(y, 0.0) for y in years],
        # Extras que ya existían
        # "SOC final": [best['SOC_end_by_year'][y] for y in years],
        # "Opex PV+BESS+GEN": [best['Assets_OPEX_by_year'][y] for y in years],
    }

    df = pd.DataFrame(data, index=years)
    df.index.name = "Año"

    print("\nResultados por año:")
    print(df)

    # Guardar a Excel
    # df.to_excel("resultados_optimizador.xlsx")

    return df
