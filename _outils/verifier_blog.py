# Contrôle qualité du blog : bloque la publication si un article ne respecte pas les règles SEO/GEO.
# Usage (depuis la racine du site) :  python3 _outils/verifier_blog.py
import os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blog_aliments import ALIMENTS, totaux
from blog_calendrier import ORDRE
from blog_sources import SOURCES_BLOG
from generer import CATEGORIES, GUIDES, RACINE, texte_brut, tous_les_articles

CHAMPS = ["slug", "categorie", "mot_cle", "titre", "titre_seo", "titre_court", "description", "resume", "reponse", "en_bref", "corps", "faq", "sources", "guide", "icone"]
INTERDITS = ["garanti", "miracle", "sans effort", "—", "révolutionnaire", "plongeons", "dans le monde de", "il est important de noter", "en conclusion"]
ICONES = {f[3:-5] for f in os.listdir(os.path.join(RACINE, "img")) if f.startswith("ic-")}
GUIDES_SLUGS = {g["slug"] for g in GUIDES}


def controler(a, slugs):
    pb = []
    for c in CHAMPS:
        if not a.get(c):
            pb.append(f"champ manquant : {c}")
    if pb:
        return pb
    mc = a["mot_cle"].lower()
    corps = texte_brut(re.sub(r"\[\[[^|\]]+\|([^\]]+)\]\]", r"\1", a["corps"]))
    tout = " ".join([a["titre"], a["description"], a["reponse"], corps, " ".join(a["en_bref"]), " ".join(q + " " + r for q, r in a["faq"])])
    if not 30 <= len(a["titre_seo"]) <= 62: pb.append(f"titre_seo fait {len(a['titre_seo'])} caractères (30 à 62)")
    if not 120 <= len(a["description"]) <= 158: pb.append(f"description fait {len(a['description'])} caractères (120 à 158)")
    if len(a["titre_court"]) > 42: pb.append(f"titre_court fait {len(a['titre_court'])} caractères (42 max)")
    if len(a["resume"]) > 90: pb.append(f"resume fait {len(a['resume'])} caractères (90 max)")
    mots_rep = len(a["reponse"].split())
    if not 35 <= mots_rep <= 75: pb.append(f"réponse courte de {mots_rep} mots (35 à 75)")
    mots = len(corps.split())
    if mots < (450 if a.get("recette") else 700): pb.append(f"corps trop court : {mots} mots")
    if a["categorie"] not in CATEGORIES: pb.append("rubrique inconnue")
    if a["guide"] not in GUIDES_SLUGS: pb.append(f"guide inconnu : {a['guide']}")
    if a["icone"] not in ICONES: pb.append(f"icône inconnue : {a['icone']}")
    if a["slug"] in CATEGORIES: pb.append("slug réservé à une rubrique")
    if not re.fullmatch(r"[a-z0-9-]+", a["slug"]): pb.append("slug mal formé")
    for ou, texte in [("titre", a["titre"]), ("titre_seo", a["titre_seo"]), ("description", a["description"]), ("réponse", a["reponse"])]:
        if not set(mc.split()) <= set(re.findall(r"[\w'-]+", texte.lower())) and mc not in texte.lower():
            pb.append(f"mot-clé « {mc} » absent de : {ou}")
    if mc not in corps.lower(): pb.append(f"mot-clé « {mc} » absent du corps")
    if not 3 <= len(a["en_bref"]) <= 5: pb.append("en_bref : 3 à 5 points")
    if not 3 <= len(a["faq"]) <= 6: pb.append("faq : 3 à 6 questions")
    if len(a["sources"]) < 2: pb.append("au moins 2 sources")
    for s in a["sources"]:
        if s not in SOURCES_BLOG: pb.append(f"source inconnue : {s}")
    h2 = re.findall(r"<h2>(.*?)</h2>", a["corps"])
    if len(h2) < 3 and not a.get("recette"): pb.append("au moins 3 titres h2")
    if not re.search(r"<table|<ul>|<ol>", a["corps"]): pb.append("au moins un tableau ou une liste")
    if "<h1" in a["corps"]: pb.append("pas de h1 dans le corps")
    if a["corps"].count("<p>") != a["corps"].count("</p>"): pb.append("balises <p> déséquilibrées")
    if a["corps"].count("<table") != a["corps"].count("</table>"): pb.append("tableau mal fermé")
    if "<table" in a["corps"] and a["corps"].count('<div class="tableau"><table') != a["corps"].count("<table"): pb.append('tableau hors de <div class="tableau">')
    liens = re.findall(r"\[\[([^|\]]+)\|", a["corps"])
    if not any(l.startswith("guide:") for l in liens): pb.append("au moins un lien vers un guide")
    if sum(not l.startswith("guide:") for l in liens) < 2: pb.append("au moins 2 liens vers d'autres articles")
    for l in liens:
        if l.startswith("guide:"):
            if l[6:] not in GUIDES_SLUGS: pb.append(f"lien vers un guide inconnu : {l}")
        elif l not in slugs or l == a["slug"]: pb.append(f"lien vers un article inconnu : {l}")
    if re.search(r'href="(?!https?://|mailto:)', a["corps"]): pb.append("lien interne écrit en dur : utiliser [[slug|texte]]")
    if "BONGO" not in a["corps"]: pb.append("BONGO n'apparaît pas dans le corps")
    for s in a.get("lire_aussi", []):
        if s not in slugs: pb.append(f"lire_aussi inconnu : {s}")
    for mot in INTERDITS:
        if mot in tout.lower(): pb.append(f"expression à éviter : « {mot} »")
    if re.search(r"\b(vous|votre|vos)\b", tout.lower()): pb.append("tutoiement obligatoire (vous/votre/vos trouvé)")
    r = a.get("recette")
    if a["categorie"] == "recettes" and not r: pb.append("une recette doit avoir son bloc recette")
    if r:
        for cle, g, _ in r["ingredients"]:
            if cle not in ALIMENTS: pb.append(f"aliment inconnu : {cle}")
        if len(r["etapes"]) < 2: pb.append("recette : au moins 2 étapes")
        if not r.get("categorie") or not r.get("portions") or "preparation" not in r: pb.append("recette : catégorie, portions, preparation requis")
        if not pb:
            t = totaux(r["ingredients"], r["portions"])
            if r.get("attendu_kcal") and abs(t["kcal"] - r["attendu_kcal"]) > 60: pb.append(f"le texte annonce {r['attendu_kcal']} kcal, le calcul donne {t['kcal']}")
            if r.get("attendu_prot") and abs(t["prot"] - r["attendu_prot"]) > 4: pb.append(f"le texte annonce {r['attendu_prot']} g de protéines, le calcul donne {t['prot']}")
    return pb


def main():
    articles = tous_les_articles()
    slugs = {a["slug"] for a in articles}
    erreurs = 0
    vus = {}
    for a in articles:
        pb = controler(a, slugs)
        for c in ("titre", "titre_seo", "description", "mot_cle"):
            if (c, a.get(c)) in vus:
                pb.append(f"{c} en double avec {vus[(c, a[c])]}")
            vus[(c, a.get(c))] = a["slug"]
        if a.get("titre_seo") in {g["titre"] for g in GUIDES}:
            pb.append("même titre qu'un guide")
        if not os.path.exists(os.path.join(RACINE, "img", "og", f"blog-{a['slug']}.png")):
            pb.append("image de partage manquante (lancer generer.py sur le Mac)")
        if pb:
            erreurs += len(pb)
            print(f"✗ {a['slug']}")
            for p in pb:
                print("   -", p)
    print(f"{len(articles)} articles, {erreurs} problème(s)")
    sys.exit(1 if erreurs else 0)


if __name__ == "__main__":
    main()
