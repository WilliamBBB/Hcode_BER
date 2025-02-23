import sys
import os
from gurobipy import Model, GRB, quicksum
from itertools import combinations

def charger_donnees(nom_fichier):
    with open(nom_fichier, "r") as fichier:
        lignes = fichier.readlines()
    
    nb_photos = int(lignes[0].strip())  # Nombre total de photos
    images = {}
    verticales = []

    for i in range(1, nb_photos + 1):
        elements = lignes[i].strip().split()
        type_orientation = elements[0]
        etiquettes = set(elements[2:])
        images[i - 1] = {"orientation": type_orientation, "tags": etiquettes}
        if type_orientation == "V":
            verticales.append(i - 1)

    return images, verticales


def generer_diapositives(images, verticales):
    diapos = []
    
    for identifiant, image in images.items():
        if image["orientation"] == "H":
            diapos.append((identifiant,))
    
    paires_verticales = list(combinations(verticales, 2))
    diapos.extend(paires_verticales)
    
    return diapos


def calculer_interet(tags_un, tags_deux):
    return min(len(tags_un & tags_deux), len(tags_un - tags_deux), len(tags_deux - tags_un))


def optimiser_diaporama(images, diapos):
    modele = Model("Optimisation Diaporama")
    
    print("\nDémarrage de l'optimisation Gurobi...")
    
    diapos_horizontales = [s for s in diapos if len(s) == 1]
    diapos_verticales = [s for s in diapos if len(s) == 2]
    
    variables_selection = modele.addVars(diapos, vtype=GRB.BINARY, name="selection")
    
    etiquettes_diapos = {s: set().union(*[images[p]["tags"] for p in s]) for s in diapos}
    paires_diapos = [(s1, s2) for s1 in diapos for s2 in diapos if s1 != s2]
    scores_transitions = {(s1, s2): calculer_interet(etiquettes_diapos[s1], etiquettes_diapos[s2]) for s1, s2 in paires_diapos}
    variables_transitions = modele.addVars(paires_diapos, vtype=GRB.BINARY, name="transition")
    
    for identifiant in images:
        modele.addConstr(quicksum(variables_selection[s] for s in diapos if identifiant in s) <= 1)
    
    for s1, s2 in paires_diapos:
        modele.addConstr(variables_transitions[s1, s2] <= variables_selection[s1])
        modele.addConstr(variables_transitions[s1, s2] <= variables_selection[s2])
    
    nb_horizontales = quicksum(variables_selection[s] for s in diapos_horizontales)
    nb_verticales = quicksum(variables_selection[s] for s in diapos_verticales)
    
    if len(diapos_horizontales) > 0:
        modele.addConstr(nb_horizontales >= 1, "Au moins une diapositive horizontale")
    if len(diapos_verticales) > 0:
        modele.addConstr(nb_verticales >= 1, "Au moins une diapositive verticale")
    
    modele.setObjective(quicksum(scores_transitions[s1, s2] * variables_transitions[s1, s2] for s1, s2 in paires_diapos), GRB.MAXIMIZE)
    
    modele.optimize()
    
    diapos_selectionnees = [s for s in diapos if variables_selection[s].x > 0.5]
    
    ordre_optimise = ordonner_diapositives(diapos_selectionnees, scores_transitions)
    
    return ordre_optimise


def ordonner_diapositives(diapos, scores_transitions):
    ordre_final = []
    diapos_restantes = set(diapos)
    
    diapo_actuelle = diapos_restantes.pop()
    ordre_final.append(diapo_actuelle)
    
    while diapos_restantes:
        prochaine_diapo = max(diapos_restantes, key=lambda s: scores_transitions.get((diapo_actuelle, s), 0))
        ordre_final.append(prochaine_diapo)
        diapos_restantes.remove(prochaine_diapo)
        diapo_actuelle = prochaine_diapo
    
    return ordre_final


def evaluer_score_total(diaporama, images):
    score = 0
    for i in range(len(diaporama) - 1):
        tags_premier = set().union(*[images[p]["tags"] for p in diaporama[i]])
        tags_second = set().union(*[images[p]["tags"] for p in diaporama[i + 1]])
        score += calculer_interet(tags_premier, tags_second)
    return score


def sauvegarder_solution(diaporama):
    with open("slideshow.sol", "w") as fichier:
        fichier.write(f"{len(diaporama)}\n")
        for diapo in diaporama:
            fichier.write(" ".join(map(str, diapo)) + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python slideshow.py [fichier_donnees]")
        sys.exit(1)
    
    fichier_donnees = sys.argv[1]
    if not os.path.exists(fichier_donnees):
        print(f"Erreur : fichier '{fichier_donnees}' introuvable.")
        sys.exit(1)
    
    print(f"\nTraitement du fichier : {fichier_donnees}")
    
    images, verticales = charger_donnees(fichier_donnees)
    diapos = generer_diapositives(images, verticales)
    solution = optimiser_diaporama(images, diapos)
    score_final = evaluer_score_total(solution, images)
    
    sauvegarder_solution(solution)
    
    print(f"Solution optimisée enregistrée dans 'slideshow.sol'")
    print(f"Score final : {score_final}\n")