# Affiche le nombre d'articles écrits mais pas encore publiés.
from blog_calendrier import ORDRE, date_de
from generer import AUJOURDHUI

print(sum(1 for s in ORDRE if date_de(s) > AUJOURDHUI))
