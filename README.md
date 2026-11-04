# 🦈 JAWS

**J**ules **A**llemand, **W**orkspace **S**eaTech

Mono repo qui regroupe tous mes projets réalisés dans le cadre de ma formation d'ingénieur à **SeaTech**.

---

## 📦 Contenu du repo

Le repo contient des projets de natures très différentes, tous liés à l'école :

- Maths / simulation (MATLAB)
- Programmation (Python, C, C++, Java)
- Jeux vidéo (Unity)
- Traitement d'image
- Systèmes embarqués (microcontrôleurs)
- Projets de groupe, hackathons, événements

Chaque projet s'appelle une **app**. Une app est un sous-projet autonome : elle a son code, son README et ses dépendances.

---

## 📁 Structure

```
jaws/
├── apps/        # Toutes les apps (un dossier par app)
├── docs/        # Ressources transverses (fiches, cours, templates)
├── shared/      # Librairie ou code commun à plusieurs apps
├── LICENSE
└── README.md
```

**Règles simples :**

1. Toutes les apps vivent dans `apps/`, à la racine du repo. Pas de sous-dossier par techno ou par année.
2. Une app = un dossier = un projet autonome.
3. Chaque app contient au minimum un `README.md` (objectif, comment la lancer).
4. Une app ne dépend pas du code d'une autre app. Si du code est partagé, il est copié ou déplacé dans `shared/`.
5. Les fichiers générés (binaires, `Library/` Unity, `venv`, gros datasets) ne sont jamais commit.

---

## 🏷️ Nommage des apps

Chaque dossier d'app suit cette nomenclature :

```
SCOPE-name-YY-YY
```

| Partie | Description | Format |
|---|---|---|
| `SCOPE` | La matière (code de l'emploi du temps) ou l'événement / l'occasion | MAJUSCULES, sans tiret |
| `name` | Nom court décrivant le projet | minuscules, `kebab-case`, sans accent |
| `YY-YY` | Année scolaire | deux chiffres, ex. `26-27` |

### Exemples

```
apps/
├── SNSIGM-sobel-filter-26-27/        # TP de la matière SNSIGM
├── SNSIGM-matlab-fft-26-27/
├── HACKATHON-escape-game-26-27/      # Événement
├── PERSO-portfolio-26-27/            # Projet personnel
└── PROJ-robot-suiveur-27-28/         # Projet de groupe l'année suivante
```

### Règles

- Le `SCOPE` est en majuscules et ne contient **ni tiret ni espace** (ex. `SNSIGM`, `HACKATHON`).
- Le `name` est en minuscules, mots séparés par des tirets, sans accent ni caractère spécial.
- L'année scolaire est toujours à la fin, et la deuxième année = la première + 1 (`26-27`, pas `26-28`).
- Pas de `_`, pas d'espace, pas de majuscule dans le `name`.

### Vérification rapide (regex)

```
^[A-Z0-9]+(-[a-z0-9]+)+-[0-9]{2}-[0-9]{2}$
```

---

## 🔀 Git

- `main` : version stable, toujours propre.
- `feature/<app>-<sujet>` : travail en cours sur une app.
- Commits courts et clairs, avec l'app concernée en préfixe :

```
SNSIGM-sobel-filter-26-27: ajout du calcul du gradient
HACKATHON-escape-game-26-27: fix collision joueur
```

---

## 🤝 Projets de groupe

Si tu es collaborateur sur ce repo :

1. Ne modifie que l'app du projet commun.
2. Travaille sur une branche, puis ouvre une Pull Request vers `main`.
3. Respecte la nomenclature ci-dessus pour toute nouvelle app.

---

## 📄 Licence

Repo privé, **tous droits réservés** (voir [LICENSE](LICENSE)). Les supports de cours et ressources tierces restent la propriété de leurs auteurs.

---

## 👤 Auteur

**Jules Allemand**, élève ingénieur à SeaTech
