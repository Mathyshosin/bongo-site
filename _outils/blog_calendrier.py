# L'ordre de publication du blog : DEBUT reçoit les LANCEMENT premiers articles,
# puis un article par jour. Ajouter un stock = ajouter des slugs à la fin de la liste.
# Un article déjà publié ne doit plus changer de place.
from datetime import date, timedelta

DEBUT = date(2026, 11, 2)
LANCEMENT = 3

ORDRE = [
    "comment-grossir-quand-on-est-maigre",
    "gainer-maison-recette",
    "seance-20-minutes-maison",
    "aliments-pour-grossir",
    "faire-des-pompes-debutant",
    "porridge-prise-de-masse",
    "se-peser-prise-de-masse",
    "journee-3000-calories",
    "muscler-pectoraux-maison",
    "recette-micro-ondes-etudiant",
    "manger-plus-sans-appetit",
    "combien-de-seances-par-semaine",
    "meal-prep-prise-de-masse",
    "prise-de-gras-prise-de-masse",
    "petit-dejeuner-pour-grossir",
    "muscler-dos-sans-materiel",
    "pancakes-proteines-sans-whey",
    "creatine-debutant",
    "courbatures-musculation",
    "chili-prise-de-masse-pas-cher",
    "rester-motive-musculation",
    "compter-calories-sans-peser",
    "muscler-bras-sans-halteres",
    "bolognaise-lentilles-proteines",
    "prise-de-masse-sans-whey",
    "sommeil-et-muscle",
    "muscler-jambes-maison",
    "boules-energie-beurre-cacahuete",
    "prise-de-masse-vegetarienne",
    "alcool-et-musculation",
]


def date_de(slug):
    i = ORDRE.index(slug)
    return DEBUT if i < LANCEMENT else DEBUT + timedelta(days=i - LANCEMENT + 1)
