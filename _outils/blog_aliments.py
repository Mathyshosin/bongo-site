# Repères par 100 g pour calculer les recettes du blog : valeurs arrondies d'après
# Ciqual (ANSES) et prix indicatifs en supermarché discount en France (fin 2026),
# alignés sur le guide « prix des protéines ». Les totaux affichés sont calculés ici.
# clé: (kcal, protéines g, glucides g, lipides g, prix € au kg)
ALIMENTS = {
  "flocons": (375, 13, 60, 7, 1.5),
  "lait": (46, 3.3, 4.8, 1.6, 1.0),
  "banane": (90, 1.1, 20, 0.2, 2.0),
  "beurre_cacahuete": (610, 25, 15, 50, 8.0),
  "oeuf": (140, 12.5, 0.5, 10, 5.3),  # sans coquille : 1 œuf moyen ≈ 50 g
  "fromage_blanc": (75, 8, 4, 3, 2.5),
  "yaourt": (60, 4, 5, 2, 2.0),
  "riz": (355, 7.5, 78, 0.6, 1.8),  # cru
  "pates": (355, 12, 71, 1.5, 1.2),  # crues
  "semoule": (360, 12, 72, 1.5, 1.6),  # crue
  "lentilles": (335, 24, 48, 1.5, 3.2),  # sèches
  "pois_chiches": (140, 7.5, 20, 3, 3.0),  # conserve égouttés
  "haricots_rouges": (105, 7.5, 14, 0.5, 3.0),  # conserve égouttés
  "mais": (90, 3, 15, 1, 3.0),  # conserve égoutté
  "thon": (110, 25, 0, 1, 11.0),  # au naturel égoutté
  "sardines": (220, 23, 0, 14, 12.0),  # à l'huile égouttées
  "poulet": (110, 23, 0, 2, 11.0),  # blanc cru
  "steak_hache": (125, 20, 0, 5, 8.75),  # 5 % cru
  "jambon": (110, 20, 1, 3, 10.0),
  "tofu": (140, 13, 2, 8, 6.0),
  "huile_olive": (900, 0, 0, 100, 9.0),
  "huile_colza": (900, 0, 0, 100, 3.0),
  "beurre": (745, 0.7, 0.7, 82, 9.0),
  "miel": (325, 0.4, 80, 0, 10.0),
  "sucre": (400, 0, 100, 0, 1.2),
  "pain": (270, 9, 55, 1, 3.0),
  "pain_mie": (260, 9, 45, 4, 3.0),
  "farine": (340, 10, 72, 1, 0.9),
  "patate": (80, 2, 17, 0.1, 1.2),  # crue
  "legumes": (40, 2.5, 5, 0.5, 2.5),  # surgelés
  "tomates": (25, 1.2, 4, 0.2, 2.0),  # concassées en conserve
  "oignon": (40, 1.2, 8, 0.2, 1.5),
  "lait_coco": (190, 2, 3, 19, 5.0),
  "emmental": (390, 27, 0.5, 31, 9.0),
  "cacao": (350, 20, 15, 22, 10.0),  # poudre non sucrée
  "chocolat": (530, 6, 55, 31, 10.0),  # noir
  "amandes": (620, 21, 8, 52, 12.0),
  "raisins_secs": (310, 3, 70, 0.5, 6.0),
  "pomme": (53, 0.3, 12, 0.2, 2.0),
  "whey": (400, 75, 8, 7, 25.0),
}


def totaux(ingredients, portions):
    """Totaux PAR PORTION d'une liste (clé, grammes, texte) : kcal, protéines, glucides, lipides, prix."""
    k = p = g = l = e = 0.0
    for cle, grammes, _ in ingredients:
        a = ALIMENTS[cle]
        k += a[0] * grammes / 100
        p += a[1] * grammes / 100
        g += a[2] * grammes / 100
        l += a[3] * grammes / 100
        e += a[4] * grammes / 1000
    return {"kcal": round(k / portions / 10) * 10, "prot": round(p / portions), "gluc": round(g / portions), "lip": round(l / portions), "prix": round(e / portions, 2)}
