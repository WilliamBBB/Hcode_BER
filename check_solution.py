import sys

def read_input(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    num_photos = int(lines[0].strip())
    photos = []
    
    for i in range(1, num_photos + 1):
        parts = lines[i].strip().split()
        orientation = parts[0]
        tags = set(parts[2:])
        photos.append((i - 1, orientation, tags))
    
    return photos

def read_solution(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    num_slides = int(lines[0].strip())
    slides = []
    
    for i in range(1, num_slides + 1):
        photo_indices = list(map(int, lines[i].strip().split()))
        slides.append(photo_indices)
    
    return slides

def validate_solution(photos, slides):
    used_photos = set()
    
    for slide in slides:
        if len(slide) == 1:
            photo_idx = slide[0]
            if photos[photo_idx][1] != 'H':
                print(f"Erreur : La photo {photo_idx} n'est pas horizontale.")
                return False
            if photo_idx in used_photos:
                print(f"Erreur : La photo {photo_idx} est utilisée plus d'une fois.")
                return False
            used_photos.add(photo_idx)
        elif len(slide) == 2:
            photo_idx1, photo_idx2 = slide
            if photos[photo_idx1][1] != 'V' or photos[photo_idx2][1] != 'V':
                print(f"Erreur : Les photos {photo_idx1} et {photo_idx2} ne sont pas toutes les deux verticales.")
                return False
            if photo_idx1 in used_photos or photo_idx2 in used_photos:
                print(f"Erreur : Les photos {photo_idx1} ou {photo_idx2} sont utilisées plus d'une fois.")
                return False
            used_photos.add(photo_idx1)
            used_photos.add(photo_idx2)
        else:
            print(f"Erreur : La diapositive {slide} contient un nombre invalide de photos.")
            return False
    
    if len(used_photos) != len(photos):
        print("Erreur : Toutes les photos ne sont pas utilisées exactement une fois.")
        return False
    
    return True

def compute_interest(tags1, tags2):
    common_tags = len(tags1 & tags2)
    unique_to_1 = len(tags1 - tags2)
    unique_to_2 = len(tags2 - tags1)
    return min(common_tags, unique_to_1, unique_to_2)

def calculate_score(photos, slides):
    total_score = 0
    previous_tags = None
    
    for slide in slides:
        current_tags = set()
        for photo_idx in slide:
            current_tags.update(photos[photo_idx][2])
        
        if previous_tags is not None:
            total_score += compute_interest(previous_tags, current_tags)
        
        previous_tags = current_tags
    
    return total_score

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Utilisation : python check_solution.py <chemin_vers_le_fichier_données>")
        sys.exit(1)
    
    data_file = sys.argv[1]
    solution_file = "slideshow.sol"
    
    photos = read_input(data_file)
    slides = read_solution(solution_file)
    
    if validate_solution(photos, slides):
        score = calculate_score(photos, slides)
        print(f"La solution est valide, score total du diaporama : {score}")
    else:
        print("La solution est invalide.")
