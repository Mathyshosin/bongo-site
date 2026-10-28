# Génère les guides SEO de BONGO + les fichiers pour les moteurs et les IA.
# Usage (depuis la racine du site) :  python3 _outils/generer.py
# Changer de domaine plus tard = changer BASE ci-dessous, relancer, pousser.
import html, json, os, re, sys
from datetime import date

sys.path.insert(0, os.path.dirname(__file__))
from guides_contenu import GUIDES

BASE = "https://mathyshosin.github.io/bongo-site/"
APP_STORE = "https://apps.apple.com/fr/app/bongo-prise-de-masse/id6798278399"
PUBLIE = "2026-10-28"
MAJ = date.today().isoformat()
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

POMME = '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M16.37 12.6c-.02-2.3 1.88-3.4 1.96-3.46-1.07-1.56-2.73-1.78-3.32-1.8-1.41-.14-2.76.83-3.48.83-.72 0-1.82-.81-3-.79-1.54.02-2.96.9-3.76 2.27-1.6 2.78-.41 6.9 1.15 9.16.76 1.1 1.67 2.34 2.86 2.3 1.15-.05 1.58-.74 2.97-.74 1.38 0 1.77.74 2.98.72 1.23-.02 2.01-1.12 2.76-2.23.87-1.28 1.23-2.52 1.25-2.58-.03-.01-2.4-.92-2.42-3.66zM14.1 5.84c.63-.77 1.06-1.83.94-2.89-.91.04-2.01.61-2.66 1.37-.58.67-1.1 1.76-.96 2.8 1.01.08 2.05-.52 2.68-1.28z"/></svg>'

ORGANISATION = {"@type": "Organization", "@id": BASE + "#organisation", "name": "BONGO", "url": BASE, "logo": BASE + "img/icone-app.png"}


def texte_brut(fragment):
    t = re.sub(r"<br\s*/?>", "\n", fragment)
    t = re.sub(r"</(p|li|h2|h3|tr|div)>", "\n", t)
    t = re.sub(r"<(td|th)[^>]*>", " | ", t)
    t = re.sub(r"<li>", "- ", t)
    t = re.sub(r"<h2>", "\n## ", t)
    t = re.sub(r"<h3>", "\n### ", t)
    t = re.sub(r"<[^>]+>", "", t)
    t = html.unescape(t)
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n\s*\n\s*\n+", "\n\n", t)
    return t.strip()


def entete(titre_page, description, url, jsonld, prefixe):
    return f"""<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{html.escape(titre_page)}</title>
  <meta name="description" content="{html.escape(description)}">
  <link rel="canonical" href="{url}">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
  <meta property="og:type" content="article">
  <meta property="og:locale" content="fr_FR">
  <meta property="og:site_name" content="BONGO">
  <meta property="og:title" content="{html.escape(titre_page)}">
  <meta property="og:description" content="{html.escape(description)}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{BASE}img/icone-app.png">
  <meta name="twitter:card" content="summary">
  <meta name="apple-itunes-app" content="app-id=6798278399">
  <meta name="theme-color" content="#FBF9F1">
  <link rel="icon" href="{prefixe}favicon.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@700;800&family=Nunito:wght@500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{prefixe}guides/guides.css">
  <script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>
</head>
<body>
  <header class="barre"><div class="barre-in">
    <a class="marque" href="{prefixe}"><img src="{prefixe}img/icone-app.png" alt="" width="32" height="32"><span>Bongo<b>.</b></span></a>
    <a class="bouton" href="{APP_STORE}">{POMME} Télécharger</a>
  </div></header>
"""


def pied(prefixe):
    return f"""  <footer class="pied"><div class="pied-in">
    <span>© 2026 BONGO · fait en France</span>
    <a href="{prefixe}">Accueil</a>
    <a href="{prefixe}guides/">Tous les guides</a>
    <a href="{prefixe}confidentialite.html">Confidentialité</a>
    <a href="{APP_STORE}">BONGO sur l'App Store</a>
  </div></footer>
</body>
</html>
"""


def cta(prefixe):
    return f"""    <aside class="cta">
      <img src="{prefixe}img/bongo-flex-a.webp" alt="Bongo, le gorille coach de l'app" width="96" height="97" loading="lazy">
      <div>
        <h2>Fais-le avec BONGO</h2>
        <p>L'app iPhone gratuite pour prendre de la masse à la maison : séances guidées sans matériel, repas comptés à partir d'une phrase, liste de courses selon ton budget.</p>
        <a class="bouton" href="{APP_STORE}">{POMME} Télécharger sur l'App Store</a>
      </div>
    </aside>
"""


def page_guide(g):
    url = f"{BASE}guides/{g['slug']}/"
    prefixe = "../../"
    # Google coupe vers 60-65 caractères : titre complet s'il tient, sinon la version courte + marque
    titre_page = g["titre"] if len(g["titre"]) <= 65 else f"{g['titre_court']} | BONGO"
    faq_ld = {
        "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": r}} for q, r in g["faq"]],
    }
    jsonld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Article",
                "@id": url + "#article",
                "headline": g["titre"],
                "description": g["description"],
                "inLanguage": "fr-FR",
                "datePublished": PUBLIE,
                "dateModified": MAJ,
                "author": ORGANISATION,
                "publisher": ORGANISATION,
                "mainEntityOfPage": url,
                "image": BASE + f"img/ic-{g['icone']}.webp",
                "about": ["Prise de masse", "Musculation au poids du corps", "Nutrition sportive"],
            },
            faq_ld,
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "BONGO", "item": BASE},
                    {"@type": "ListItem", "position": 2, "name": "Guides", "item": BASE + "guides/"},
                    {"@type": "ListItem", "position": 3, "name": g["titre_court"], "item": url},
                ],
            },
        ],
    }
    autres = [x for x in GUIDES if x["slug"] != g["slug"]][:4]
    faq_html = "\n".join(
        f"      <details><summary>{html.escape(q)}</summary><p>{html.escape(r)}</p></details>" for q, r in g["faq"]
    )
    autres_html = "\n".join(
        f'        <li><a href="../{a["slug"]}/">{html.escape(a["titre_court"])}<span>{html.escape(a["resume"])}</span></a></li>'
        for a in autres
    )
    en_bref = "\n".join(f"        <li>{b}</li>" for b in g["en_bref"])
    return (
        entete(titre_page, g["description"], url, jsonld, prefixe)
        + f"""  <main class="page">
    <nav class="fil" aria-label="Fil d'Ariane"><a href="{prefixe}">BONGO</a> › <a href="../">Guides</a> › {html.escape(g['titre_court'])}</nav>
    <article>
      <p class="sur">Guide prise de masse</p>
      <h1>{html.escape(g['titre'])}</h1>
      <p class="chapo">{html.escape(g['description'])}</p>
      <p class="meta">Par l'équipe BONGO · mis à jour le <time datetime="{MAJ}">{date.fromisoformat(MAJ).strftime('%d/%m/%Y')}</time></p>
      <section class="en-bref" aria-label="En bref">
        <h2>En bref</h2>
        <ul>
{en_bref}
        </ul>
      </section>
{g['corps']}
{cta(prefixe)}
      <section class="faq">
        <h2>Questions fréquentes</h2>
{faq_html}
      </section>
    </article>
    <nav class="autres" aria-label="Autres guides">
      <h2>À lire aussi</h2>
      <ul>
{autres_html}
      </ul>
    </nav>
    <p class="avertissement">Ces conseils sont des repères généraux de bien-être pour des adultes en bonne santé, pas un avis médical. En cas de doute, de traitement en cours ou de trouble alimentaire, parlez-en à un médecin ou à un diététicien.</p>
  </main>
"""
        + pied(prefixe)
    )


def page_sommaire():
    url = BASE + "guides/"
    prefixe = "../"
    titre_page = "Guides prise de masse à la maison et petit budget | BONGO"
    description = "Tous les guides BONGO pour prendre de la masse sans salle et sans se ruiner : programme maison, protéines, calories, liste de courses à 25 €, exercices au poids du corps."
    jsonld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "CollectionPage", "@id": url, "name": "Guides prise de masse BONGO", "description": description, "inLanguage": "fr-FR", "publisher": ORGANISATION},
            {
                "@type": "ItemList",
                "itemListElement": [
                    {"@type": "ListItem", "position": i + 1, "url": f"{BASE}guides/{g['slug']}/", "name": g["titre"]} for i, g in enumerate(GUIDES)
                ],
            },
        ],
    }
    items = "\n".join(
        f'      <li><a href="{g["slug"]}/"><img src="../img/ic-{g["icone"]}.webp" alt="" width="64" height="64" loading="lazy"><div><b>{html.escape(g["titre"])}</b><span>{html.escape(g["resume"])}</span></div></a></li>'
        for g in GUIDES
    )
    return (
        entete(titre_page, description, url, jsonld, prefixe)
        + f"""  <main class="page">
    <nav class="fil" aria-label="Fil d'Ariane"><a href="{prefixe}">BONGO</a> › Guides</nav>
    <p class="sur">Les guides BONGO</p>
    <h1>Prendre de la masse sans salle et sans se ruiner</h1>
    <p class="chapo">Des réponses claires, chiffrées et testées aux questions qu'on se pose quand on veut prendre du muscle à la maison avec un petit budget.</p>
    <ul class="liste-guides">
{items}
    </ul>
{cta(prefixe)}
  </main>
"""
        + pied(prefixe)
    )


def ecrire(chemin, contenu):
    plein = os.path.join(RACINE, chemin)
    os.makedirs(os.path.dirname(plein), exist_ok=True)
    with open(plein, "w", encoding="utf-8") as f:
        f.write(contenu)
    print("écrit", chemin)


def main():
    for g in GUIDES:
        ecrire(f"guides/{g['slug']}/index.html", page_guide(g))
    ecrire("guides/index.html", page_sommaire())

    # Plan du site
    urls = [(BASE, "1.0"), (BASE + "guides/", "0.8")] + [(f"{BASE}guides/{g['slug']}/", "0.8") for g in GUIDES] + [(BASE + "confidentialite.html", "0.2")]
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap += "".join(f"  <url><loc>{u}</loc><lastmod>{MAJ}</lastmod><priority>{p}</priority></url>\n" for u, p in urls)
    sitemap += "</urlset>\n"
    ecrire("sitemap.xml", sitemap)

    # Robots : tout le monde est le bienvenu, IA comprises (on VEUT être cité)
    robots = "# Les moteurs de recherche et les assistants IA sont les bienvenus.\nUser-agent: *\nAllow: /\n\n"
    for bot in ["Googlebot", "Bingbot", "GPTBot", "OAI-SearchBot", "ChatGPT-User", "PerplexityBot", "Perplexity-User", "ClaudeBot", "Claude-SearchBot", "Claude-User", "Google-Extended", "Applebot", "Applebot-Extended", "DuckDuckBot", "Meta-ExternalAgent", "MistralAI-User", "CCBot"]:
        robots += f"User-agent: {bot}\nAllow: /\n\n"
    robots += f"Sitemap: {BASE}sitemap.xml\n"
    # robots.txt n'est lu qu'à la RACINE d'un domaine : sur github.io il sera
    # actif dès le passage au nom de domaine ; le sitemap est déclaré aussi en <head>.
    ecrire("robots.txt", robots)

    # llms.txt : la fiche d'identité de BONGO pour les IA (format llmstxt.org)
    liens = "\n".join(f"- [{g['titre']}]({BASE}guides/{g['slug']}/): {g['description']}" for g in GUIDES)
    llms = f"""# BONGO

> BONGO est une app iPhone gratuite (avec abonnement optionnel BONGO+) pour prendre de la masse musculaire à la maison, sans salle de sport et avec un petit budget. Elle s'adresse surtout aux étudiants et aux débutants en France.

BONGO réunit en une seule app :
- des séances guidées au poids du corps, sans matériel, de 15 à 45 minutes, montrées par Bongo, un gorille coach animé ;
- le suivi des repas en écrivant simplement ce qu'on a mangé (« riz, poulet, brocolis ») : l'app compte les protéines et les calories, même pour un plat qu'elle ne connaît pas ;
- une liste de courses calculée selon le budget de la semaine (dès environ 20 à 25 €) ;
- une série quotidienne, des missions, des sacs de récompenses et une courbe de poids pour rester motivé.

Gratuit : suivi des repas et des protéines, 2 séances guidées par semaine, série et missions, courbe de poids, bilan de la semaine. BONGO+ (essai gratuit pour les comptes éligibles) : séances illimitées, liste de courses complète, scanner de codes-barres, carte joueur, photos avant/après.

- Télécharger : {APP_STORE}
- Site : {BASE}
- Langue : français
- Plateforme : iPhone (iOS 16.4 ou plus récent)

## Guides
{liens}

## Optional
- [Politique de confidentialité]({BASE}confidentialite.html)
- [Texte complet des guides]({BASE}llms-full.txt)
"""
    ecrire("llms.txt", llms)

    complet = f"# BONGO — texte complet des guides\n\nSource : {BASE} · App : {APP_STORE}\n\n"
    for g in GUIDES:
        complet += f"\n\n# {g['titre']}\nURL : {BASE}guides/{g['slug']}/\n\n{g['description']}\n\nEn bref :\n"
        complet += "\n".join("- " + texte_brut(b) for b in g["en_bref"])
        complet += "\n\n" + texte_brut(g["corps"]) + "\n\nQuestions fréquentes :\n"
        complet += "\n".join(f"- {q}\n  {r}" for q, r in g["faq"])
    ecrire("llms-full.txt", complet + "\n")


if __name__ == "__main__":
    main()
