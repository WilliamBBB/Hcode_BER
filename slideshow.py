import sys
import gurobipy as gp
from gurobipy import GRB

def read_input(file_path):
    with open(file_path, "r") as f:
        lines = f.readlines()
    
    N = int(lines[0].strip())
    photos = []
    vertical_photos = []
    horizontal_photos = []
    
    for i in range(1, N + 1):
        parts = lines[i].strip().split()
        orientation = parts[0]
        tags = set(parts[2:])
        photos.append((i - 1, orientation, tags))
        
        if orientation == "H":
            horizontal_photos.append((i - 1, tags))
        else:
            vertical_photos.append((i - 1, tags))
    
    return photos, horizontal_photos, vertical_photos

def merge_vertical_photos(vertical_photos):
    merged_slides = []
    used = set()
    
    for i in range(len(vertical_photos)):
        if i in used:
            continue
        best_match = None
        max_tags = 0
        for j in range(i + 1, len(vertical_photos)):
            if j in used:
                continue
            merged_tags = vertical_photos[i][1] | vertical_photos[j][1]
            if len(merged_tags) > max_tags:
                max_tags = len(merged_tags)
                best_match = j
        
        if best_match is not None:
            merged_slides.append(((vertical_photos[i][0], vertical_photos[best_match][0]), merged_tags))
            used.add(i)
            used.add(best_match)
    
    return merged_slides

def compute_interest(tags1, tags2):
    common = len(tags1 & tags2)
    unique1 = len(tags1 - tags2)
    unique2 = len(tags2 - tags1)
    return min(common, unique1, unique2)

def solve_slideshow(file_path):
    photos, horizontal_photos, vertical_photos = read_input(file_path)
    vertical_slides = merge_vertical_photos(vertical_photos)
    slides = [(h[0], h[1]) for h in horizontal_photos] + vertical_slides
    
    # Gurobi model
    model = gp.Model("slideshow")
    
    # Variables : x[i, j] = 1 si la diapositive i est placée avant la diapositive j
    slide_indices = list(range(len(slides)))
    x = model.addVars(slide_indices, slide_indices, vtype=GRB.BINARY, name="x")
    
    # Contrainte : chaque diapositive doit être suivie par exactement une autre
    for i in slide_indices:
        model.addConstr(sum(x[i, j] for j in slide_indices if i != j) == 1)
    
    # Contrainte : chaque diapositive doit avoir exactement une prédécesseur
    for j in slide_indices:
        model.addConstr(sum(x[i, j] for i in slide_indices if i != j) == 1)
    
    # Fonction objectif : maximiser la somme des scores des transitions
    model.setObjective(
        gp.quicksum(compute_interest(slides[i][1], slides[j][1]) * x[i, j] 
                    for i in slide_indices for j in slide_indices if i != j), 
        GRB.MAXIMIZE)
    
    model.optimize()
    
    # Extraire l'ordre des diapositives
    order = []
    used = set()
    
    for i in slide_indices:
        for j in slide_indices:
            if i != j and x[i, j].X > 0.5:
                order.append((i, j))
                used.add(i)
                used.add(j)
    
    sorted_slides = []
    
    for idx in order:
        if isinstance(slides[idx[0]][0], tuple):
            sorted_slides.append(f"{slides[idx[0]][0][0]} {slides[idx[0]][0][1]}")
        else:
            sorted_slides.append(f"{slides[idx[0]][0]}")
    
    # Écriture du fichier de sortie
    with open("slideshow.sol", "w") as f:
        f.write(f"{len(sorted_slides)}\n")
        f.write("\n".join(sorted_slides) + "\n")
    
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python slideshow.py <dataset_path>")
        sys.exit(1)
    
    dataset_path = sys.argv[1]
    solve_slideshow(dataset_path)
