"""
Script de benchmark exhaustif pour la génération des résultats numériques et tableaux LaTeX
du rapport d'optimisation SPOT-5.
"""

import json
import os
import time
import pandas as pd
from spot_solver import SpotInstance, solve_spot, compare_weather_scenarios, WEATHER_MODES


def run_all_benchmarks():
    print("=" * 80)
    print("BENCHMARK EXHAUSTIF DU PLANIFICATEUR SPOT-5")
    print("=" * 80)

    instances_files = [
        "spotProba1.py",
        "spotProba2.py",
        "spotProba3.py",
        "spotProba4.py",
        "spotProba5.py",
    ]

    # 1. Validation sur instances 1, 2, 3
    print("\n--- 1. VALIDATION SUR INSTANCES ÉLÉMENTAIRES (1, 2, 3) ---")
    val_records = []
    for f in ["spotProba1.py", "spotProba2.py", "spotProba3.py"]:
        inst = SpotInstance.from_file(f)
        for mode in ["Déterministe (Sans nuages)", "Pessimiste (ProbaSup)"]:
            res = solve_spot(inst, weather_mode=mode)
            val_records.append({
                "Instance": f,
                "Images": inst.nbImages,
                "PMmax": inst.PMmax,
                "DU": inst.DU,
                "Météo": mode.split(" ")[0],
                "Statut": res.status,
                "Gain Espéré": round(res.objective_value, 3),
                "Mémoire": f"{res.memory_used}/{res.memory_max}",
                "Sélection": f"{res.selected_count}/{res.total_images}",
                "Images Retenues": res.selected_indices,
                "Affectations": res.raw_assignments,
                "CPU (ms)": round(res.solve_duration_sec * 1000, 2),
            })
    df_val = pd.DataFrame(val_records)
    print(df_val[["Instance", "PMmax", "DU", "Météo", "Gain Espéré", "Mémoire", "Images Retenues", "CPU (ms)"]].to_string(index=False))

    # 2. Benchmark Multi-Scénarios sur spotProba4 et spotProba5
    print("\n--- 2. BENCHMARK COMPARATIF spotProba4 ET spotProba5 ---")
    scenarios_records = []
    for f in ["spotProba4.py", "spotProba5.py"]:
        inst = SpotInstance.from_file(f)
        for mode in WEATHER_MODES.keys():
            res = solve_spot(inst, weather_mode=mode)
            scenarios_records.append({
                "Instance": f.replace(".py", ""),
                "Scénario Météo": mode,
                "Statut": res.status,
                "Gain Espéré": round(res.objective_value, 2),
                "Sélection": f"{res.selected_count} ({res.mono_count}M / {res.stereo_count}S)",
                "Mémoire Consommée": f"{res.memory_used} / {res.memory_max}",
                "Taux Remplissage Mem (%)": round(res.memory_used / res.memory_max * 100, 1),
                "Temps SCIP (ms)": round(res.solve_duration_sec * 1000, 2),
                "Indices": res.selected_indices,
                "Affectations": res.raw_assignments,
            })
    df_scen = pd.DataFrame(scenarios_records)
    print(df_scen[["Instance", "Scénario Météo", "Gain Espéré", "Sélection", "Mémoire Consommée", "Temps SCIP (ms)"]].to_string(index=False))

    # 3. Détail précis de spotProba4 (Pessimiste et Déterministe)
    print("\n--- 3. DÉTAIL DES PLANS POUR spotProba4 ---")
    inst4 = SpotInstance.from_file("spotProba4.py")
    res4_pess = solve_spot(inst4, weather_mode="Pessimiste (ProbaSup)")
    print(f"spotProba4 Pessimiste : Gain = {res4_pess.objective_value:.2f}, Mémoire = {res4_pess.memory_used}/{res4_pess.memory_max}")
    print("Planning détaillé spotProba4 (Pessimiste) :")
    print(res4_pess.schedule_df[["ID", "Type", "Instrument", "Début (s)", "Fin (s)", "Gain facial", "P_Clear"]].to_string(index=False))

    # 4. Détail précis de spotProba5 (Pessimiste et Déterministe)
    print("\n--- 4. DÉTAIL DES PLANS POUR spotProba5 ---")
    inst5 = SpotInstance.from_file("spotProba5.py")
    res5_pess = solve_spot(inst5, weather_mode="Pessimiste (ProbaSup)")
    print(f"spotProba5 Pessimiste (Failure=[0.001, 0.001, 0.70]) : Gain = {res5_pess.objective_value:.2f}, Mémoire = {res5_pess.memory_used}/{res5_pess.memory_max}")
    print("Planning détaillé spotProba5 (Pessimiste avec panne Inst 3) :")
    print(res5_pess.schedule_df[["ID", "Type", "Instrument", "Début (s)", "Fin (s)", "Gain facial", "P_Clear"]].to_string(index=False))

    # 5. Étude de l'impact de la panne de l'instrument 3 sur spotProba5
    print("\n--- 5. IMPACT DE LA DÉFAILLANCE DE L'INSTRUMENT 3 SUR spotProba5 ---")
    res5_no_fail = solve_spot(inst5, weather_mode="Pessimiste (ProbaSup)", failure_override=[0.0, 0.0, 0.0])
    res5_fail_3 = solve_spot(inst5, weather_mode="Pessimiste (ProbaSup)", failure_override=[0.001, 0.001, 0.70])
    res5_down_3 = solve_spot(inst5, weather_mode="Pessimiste (ProbaSup)", failure_override=[0.001, 0.001, 1.0])

    print(f"Sans panne (Failure=[0,0,0]) : Gain = {res5_no_fail.objective_value:.2f}, Mono = {res5_no_fail.mono_count}, Stéréo = {res5_no_fail.stereo_count}, Mémoire = {res5_no_fail.memory_used}")
    print(f"Panne partielle Inst 3 (Failure=[0.001, 0.001, 0.7]) : Gain = {res5_fail_3.objective_value:.2f}, Mono = {res5_fail_3.mono_count}, Stéréo = {res5_fail_3.stereo_count}, Mémoire = {res5_fail_3.memory_used}")
    print(f"Panne totale Inst 3 (Failure=[0.001, 0.001, 1.0]) : Gain = {res5_down_3.objective_value:.2f}, Mono = {res5_down_3.mono_count}, Stéréo = {res5_down_3.stereo_count}, Mémoire = {res5_down_3.memory_used}")

    # Charge par instrument
    for label, res_obj in [("Sans Panne", res5_no_fail), ("Panne 70% Inst 3", res5_fail_3), ("Panne 100% Inst 3", res5_down_3)]:
        inst_counts = res_obj.schedule_df["Instrument"].value_counts().to_dict()
        print(f"  > {label} : Répartition prises de vue = {inst_counts}")

    # 6. Analyse de Robustesse des Sélections
    print("\n--- 6. ANALYSE DE ROBUSTESSE DES SÉLECTIONS ---")
    for name, inst in [("spotProba4", inst4), ("spotProba5", inst5)]:
        comp = compare_weather_scenarios(inst)
        sets = {k: set(v.selected_indices) for k, v in comp.items()}
        robust = set.intersection(*sets.values())
        union = set.union(*sets.values())
        conditional = union - robust
        print(f"\n{name} :")
        print(f"  • Images robustes (tous scénarios) ({len(robust)}) : {sorted(list(robust))}")
        print(f"  • Images conditionnelles (dépendantes météo) ({len(conditional)}) : {sorted(list(conditional))}")

    # 7. Sensibilité à la Vitesse Miroir (VI) et à la Mémoire (PMmax)
    print("\n--- 7. ANALYSE DE SENSIBILITÉ (VI et PMmax) SUR spotProba4 ---")
    vi_records = []
    for vi in [0.2, 0.5, 1.0, 2.0, 5.0]:
        r = solve_spot(inst4, vi_override=vi)
        conf = inst4.compute_conflicts(vi_override=vi)
        vi_records.append({
            "VI (°/s)": vi,
            "Conflits Cinématiques": len(conf),
            "Gain Espéré": round(r.objective_value, 2),
            "Images Retenues": r.selected_count,
            "Mémoire": r.memory_used,
        })
    print("Sensibilité à la vitesse miroir VI :")
    print(pd.DataFrame(vi_records).to_string(index=False))

    pm_records = []
    for pm in [50, 100, 150, 200, 300]:
        r = solve_spot(inst4, pm_max_override=pm)
        pm_records.append({
            "PMmax": pm,
            "Gain Espéré": round(r.objective_value, 2),
            "Images Retenues": r.selected_count,
            "Mémoire Utilisée": r.memory_used,
            "Taux Saturation": f"{round(r.memory_used/pm*100, 1)}%",
        })
    print("\nSensibilité à la capacité mémoire PMmax :")
    print(pd.DataFrame(pm_records).to_string(index=False))

    print("\n" + "=" * 80)
    print("BENCHMARK TERMINÉ AVEC SUCCÈS")
    print("=" * 80)


if __name__ == "__main__":
    run_all_benchmarks()
