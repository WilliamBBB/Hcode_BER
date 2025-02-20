Ce projet est une solution au problème du Hash Code 2019, qui consiste à optimiser l'ordre des photos dans un diaporama. L'algorithme transforme les photos en slides et optimise leur ordonnancement pour maximiser le score d'intérêt.

Le programme utilise Gurobi Optimizer pour trouver la meilleure solution possible en un minimum de temps.

⚙️ Installation

1️⃣ Cloner le projet depuis GitHub

git clone https://github.com/WilliamBBB/Hcode_BER.git
cd Projet_William

2️⃣ Installer les dépendances

Assurez-vous d'avoir Python 3.12 et installez les librairies requises :

pip install -r requirements.txt


Exécuter le programme :

python slideshow.py data/PetPics-20.txt

python check_solution.py data/PetPics-20.txt

