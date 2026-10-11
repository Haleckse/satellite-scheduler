# SPOT-5 Satellite Acquisition Scheduler 🛰️

Projet de Recherche Opérationnelle & Programmation Linéaire en Nombres Entiers (PLNE) portant sur la planification et l'ordonnancement optimal des prises de vue du satellite d'observation de la Terre **SPOT-5**.

Le problème modélise la sélection d'acquisitions mono et stéréo, l'affectation aux 3 instruments optiques embarqués, le respect de la capacité mémoire, les contraintes cinématiques de rotation des miroirs de visée ($V_I$), et intègre les incertitudes météorologiques (présence de nuages) et de pannes matérielles.

---

## 🌐 Accès en ligne direct (Streamlit Cloud)

L'application interactive est déployée et accessible directement dans votre navigateur :

👉 [satellite-scheduler-m2-iafa.streamlit.app](https://satellite-scheduler-m2-iafa.streamlit.app/)


L'interface web permet de :
- Sélectionner les instances de test (`spotProba1` à `spotProba5`).
- Ajuster les scénarios de décision sous incertitude (Wald / pessimiste, Laplace / moyen, Maximax / optimiste, déterministe).
- Simuler des pannes matérielles sur chaque instrument.
- Visualiser le diagramme de Gantt interactif des acquisitions par instrument.
- Inspecter les conflits cinématiques et exporter les plannings optimaux en JSON/CSV.

---

## 💻 Exécution en local

Si vous souhaitez exécuter l'application sur votre machine :

### 1. Prérequis
- **Python 3.10+** (Python 3.11 ou 3.12 recommandé)
- Solveur **SCIP** et **PySCIPOpt**

### 2. Cloner le dépôt ou se placer dans le dossier
```bash
git clone https://github.com/Haleckse/satellite-scheduler.git
cd satellite-scheduler
```

### 3. Créer un environnement virtuel et installer les dépendances
```bash
# Création de l'environnement virtuel
python3 -m venv .venv

# Activation de l'environnement
source .venv/bin/activate       # Sous Linux / macOS
# ou : .venv\Scripts\activate   # Sous Windows

# Installation des dépendances
pip install -r requirements.txt
```

### 4. Lancer l'application Streamlit
```bash
streamlit run app.py
```
L'application s'ouvre automatiquement dans votre navigateur à l'adresse [http://localhost:8501](http://localhost:8501).

---

## 📊 Exécution des scripts en ligne de commande

### Résolution et benchmark complet
Pour lancer le solveur et générer la matrice comparative des scénarios et analyses de sensibilité :
```bash
python benchmark_report.py
```

### Résolution d'une instance spécifique en Python
```python
from spot_solver import SpotInstance, solve_spot
import spotProba5 as data

instance = SpotInstance.from_module(data)
sol = solve_spot(instance, weather_scenario="pessimistic")

print(f"Statut : {sol.status}")
print(f"Gain espéré : {sol.objective_value}")
print(f"Images sélectionnées : {sol.selected_images}")
```

---

## 📄 Rapport Académique

Le rapport est disponible dans le dossier `rapport_spot5/`.

Le document compilé est généré sous `rapport_spot5/main.pdf`.

---

## 📁 Structure du Projet

```text
sat-scheduler/
├── app.py                   # Interface interactive Streamlit avec graphiques Plotly
├── spot_solver.py           # Modélisation PLNE et résolution avec PySCIPOpt / SCIP
├── benchmark_report.py      # Script d'automatisation des benchmarks et analyses
├── requirements.txt         # Dépendances Python (streamlit, plotly, pandas, pyscipopt)
├── spotProba1.py à 5.py     # Instances de données SPOT-5
├── rapport_spot5/           # Sources LaTeX du rapport académique
│   ├── main.tex             # Document maître
│   ├── main.pdf             # Rapport PDF compilé
│   └── sections/            # Sections modulaires du rapport
└── README.md                # Documentation du projet
```
