/* Simulateur BONGO : 4 questions, une timeline, aucun envoi de données (tout se calcule dans le navigateur).
   Mêmes repères que _outils/generer.py : 0,25 à 0,5 % du poids par semaine (Iraki et al., 2019). */
(function () {
  'use strict';

  // ---------- Calculs ----------
  var RYTHME_APPETIT = { petit: 0.35, normal: 0.45, gros: 0.5 };
  var BONUS_SEANCES = { '1': -0.05, '2': 0, '3': 0.05, '4': 0.05 };

  // Rythme en % du poids par semaine, toujours gardé dans la fourchette des repères
  function rythme(appetit, seances) {
    var r = RYTHME_APPETIT[appetit] + BONUS_SEANCES[seances];
    return Math.round(Math.min(0.5, Math.max(0.25, r)) * 100) / 100;
  }

  function semaines(poids, objectif, r) {
    return Math.ceil(Math.log(objectif / poids) / Math.log(1 + r / 100));
  }

  function poidsApres(poids, r, s) {
    return poids * Math.pow(1 + r / 100, s);
  }

  // Garde-fous : pas de date pour un objectif irréaliste, message doux en cas de sous-poids marqué
  function evaluer(poids, taille, objectif, appetit, seances) {
    var m2 = (taille / 100) * (taille / 100);
    var imc = poids / m2;
    var imcObjectif = objectif / m2;
    if (imcObjectif >= 27 || objectif - poids > 25) {
      var suggestion = Math.min(poids + 10, Math.floor(25 * m2));
      return { statut: 'objectif-haut', suggestion: suggestion - poids >= 1 ? suggestion : null };
    }
    var r = rythme(appetit, seances);
    var regulier = semaines(poids, objectif, r);
    return {
      statut: 'ok',
      sousPoids: imc < 17,
      rythme: r,
      regulier: regulier,
      irregulier: semaines(poids, objectif, r / 2)
    };
  }

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { rythme: rythme, semaines: semaines, poidsApres: poidsApres, evaluer: evaluer };
    return;
  }

  // ---------- Formats ----------
  var MOIS = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'];
  var MOIS_COURT = ['janv.', 'févr.', 'mars', 'avr.', 'mai', 'juin', 'juil.', 'août', 'sept.', 'oct.', 'nov.', 'déc.'];

  function dateDans(s) {
    var d = new Date();
    d.setDate(d.getDate() + Math.round(s * 7));
    return d;
  }
  function dateFloue(d) {
    var j = d.getDate();
    return (j <= 10 ? 'début ' : j <= 20 ? 'mi-' : 'fin ') + MOIS[d.getMonth()] + ' ' + d.getFullYear();
  }
  function duree(s) {
    var mois = Math.round(s / 4.345);
    if (mois < 2) return s + (s > 1 ? ' semaines' : ' semaine');
    if (mois >= 24) return 'environ ' + (Math.round(mois / 6) / 2).toString().replace('.', ',') + ' ans';
    return 'environ ' + mois + ' mois';
  }
  // Écart affiché : la différence des durées montrées juste en dessous, pour que le calcul tombe juste
  function ecart(regulier, irregulier) {
    var mois = Math.round(irregulier / 4.345) - Math.round(regulier / 4.345);
    if (Math.round(regulier / 4.345) < 2 || mois < 2) return duree(irregulier - regulier).replace('environ ', '');
    return mois >= 24 ? duree(irregulier - regulier).replace('environ ', '') : mois + ' mois';
  }
  function grammes(x) {
    return Math.round(x * 100) * 10 + ' g';
  }
  function kg(x) {
    return x.toFixed(1).replace('.', ',');
  }

  // ---------- Contenus ----------
  var QUESTIONS_CHOIX = {
    appetit: {
      titre: 'Et ton appétit, il ressemble à quoi ?',
      aide: "Sois honnête : ça change le rythme qu'on peut viser.",
      image: 'bongo-miam',
      choix: [
        { v: 'petit', icone: 'pousse', t: 'Petit', s: 'Je cale vite, je saute parfois des repas' },
        { v: 'normal', icone: 'assiette', t: 'Normal', s: 'Je mange à ma faim, sans plus' },
        { v: 'gros', icone: 'flamme', t: 'Gros', s: 'Je peux manger beaucoup sans problème' }
      ]
    },
    seances: {
      titre: 'Combien de séances par semaine ?',
      aide: 'Compte ce que tu peux vraiment tenir, même des séances courtes à la maison.',
      image: 'bongo-flex-b',
      choix: [
        { v: '1', icone: 'chrono', t: '0 ou 1', s: 'Pour le moment, pas plus' },
        { v: '2', icone: 'calendrier', t: '2', s: 'Un bon début' },
        { v: '3', icone: 'haltere', t: '3', s: 'Le rythme classique' },
        { v: '4', icone: 'trophee', t: '4 ou plus', s: "Je suis à fond" }
      ]
    }
  };

  var CONSEILS = {
    petit: { icone: 'assiette', t: 'Bois une partie de tes calories', s: 'Un gainer maison passe mieux quand on cale vite.', lien: 'blog/gainer-maison-recette/' },
    normal: { icone: 'cible', t: 'Trouve ton bon surplus', s: 'Combien manger en plus, sans te forcer.', lien: 'guides/combien-de-calories-pour-prendre-du-poids/' },
    gros: { icone: 'proteine', t: 'Fais le point sur tes protéines', s: 'Manger beaucoup ne suffit pas à construire du muscle.', lien: 'guides/combien-de-proteines-par-jour/' },
    peu: { icone: 'chrono', t: 'Commence par 20 minutes', s: 'Une séance sans matériel, facile à caser.', lien: 'blog/seance-20-minutes-maison/' },
    assez: { icone: 'haltere', t: 'Suis un programme simple', s: "Quoi faire à chaque séance quand on débute.", lien: 'guides/programme-prise-de-masse-debutant/' }
  };

  // ---------- Interface ----------
  function echapper(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');
  }

  function demarrer(racine) {
    var pre = racine.getAttribute('data-prefixe') || '';
    var store = racine.getAttribute('data-store');
    var methode = racine.getAttribute('data-methode');
    var etat = { poids: 62, taille: 175, objectif: 68, appetit: null, seances: null, etape: 0 };
    var nettoyer = null;

    function img(nom, cls, largeur) {
      return '<img src="' + pre + 'img/' + nom + '.webp" alt="" class="' + cls + '" width="' + largeur + '" height="' + largeur + '">';
    }

    function progression() {
      var html = '<div class="sim-progres" role="img" aria-label="Question ' + (etat.etape + 1) + ' sur 4">';
      for (var i = 0; i < 4; i++) html += '<i class="' + (i <= etat.etape ? 'fait' : '') + '"></i>';
      return html + '</div>';
    }

    function curseur(id, nom, min, max, valeur, unite) {
      return '<div class="sim-curseur"><label for="' + id + '">' + nom + '</label>' +
        '<output id="' + id + '-val" for="' + id + '"><b>' + valeur + '</b> ' + unite + '</output>' +
        '<input id="' + id + '" type="range" min="' + min + '" max="' + max + '" step="1" value="' + valeur + '"></div>';
    }

    function peindreCurseur(el) {
      el.style.setProperty('--sim-pct', ((el.value - el.min) / (el.max - el.min)) * 100 + '%');
    }

    function brancherCurseur(id, surChange) {
      var el = racine.querySelector('#' + id);
      peindreCurseur(el);
      el.addEventListener('input', function () {
        racine.querySelector('#' + id + '-val b').textContent = el.value;
        peindreCurseur(el);
        surChange(Number(el.value));
      });
    }

    function pied(suivant) {
      return '<div class="sim-actions">' +
        (etat.etape > 0 ? '<button type="button" class="sim-retour">Retour</button>' : '<span></span>') +
        (suivant ? '<button type="button" class="sim-suivant">' + suivant + '</button>' : '') + '</div>';
    }

    function brancherPied() {
      var r = racine.querySelector('.sim-retour');
      var s = racine.querySelector('.sim-suivant');
      if (r) r.addEventListener('click', function () { etat.etape--; rendre(true); });
      if (s) s.addEventListener('click', function () { etat.etape++; rendre(true); });
    }

    function etapeMesures() {
      racine.innerHTML = '<div class="sim-carte">' + progression() +
        '<div class="sim-tete">' + img('bongo-neutre', 'sim-bongo', 84) +
        '<div><h3 tabindex="-1">On part d\'où ?</h3><p>Ton poids et ta taille d\'aujourd\'hui.</p></div></div>' +
        curseur('sim-poids', 'Ton poids', 40, 130, etat.poids, 'kg') +
        curseur('sim-taille', 'Ta taille', 145, 205, etat.taille, 'cm') +
        pied('Continuer') + '</div>';
      brancherCurseur('sim-poids', function (v) {
        etat.objectif += v - etat.poids;
        etat.poids = v;
      });
      brancherCurseur('sim-taille', function (v) { etat.taille = v; });
      brancherPied();
    }

    function etapeObjectif() {
      var min = etat.poids + 1;
      var max = etat.poids + 30;
      etat.objectif = Math.min(max, Math.max(min, etat.objectif));
      racine.innerHTML = '<div class="sim-carte">' + progression() +
        '<div class="sim-tete">' + img('bongo-flex-a', 'sim-bongo', 84) +
        '<div><h3 tabindex="-1">Tu veux arriver à combien ?</h3><p>Tu pars de ' + etat.poids + ' kg.</p></div></div>' +
        curseur('sim-objectif', 'Ton objectif', min, max, etat.objectif, 'kg') +
        '<p class="sim-ecart">Soit <b>+' + (etat.objectif - etat.poids) + ' kg</b></p>' +
        pied('Continuer') + '</div>';
      brancherCurseur('sim-objectif', function (v) {
        etat.objectif = v;
        racine.querySelector('.sim-ecart b').textContent = '+' + (v - etat.poids) + ' kg';
      });
      brancherPied();
    }

    function etapeChoix(cle) {
      var q = QUESTIONS_CHOIX[cle];
      var boutons = q.choix.map(function (c) {
        return '<button type="button" class="sim-choix" data-v="' + c.v + '" aria-pressed="' + (etat[cle] === c.v) + '">' +
          img('ic-' + c.icone, '', 44) + '<span><b>' + c.t + '</b><small>' + c.s + '</small></span></button>';
      }).join('');
      racine.innerHTML = '<div class="sim-carte">' + progression() +
        '<div class="sim-tete">' + img(q.image, 'sim-bongo', 84) +
        '<div><h3 tabindex="-1">' + q.titre + '</h3><p>' + q.aide + '</p></div></div>' +
        '<div class="sim-choix-liste">' + boutons + '</div>' + pied() + '</div>';
      racine.querySelectorAll('.sim-choix').forEach(function (b) {
        b.addEventListener('click', function () {
          etat[cle] = b.getAttribute('data-v');
          etat.etape++;
          rendre(true);
        });
      });
      brancherPied();
    }

    function resultat() {
      var e = evaluer(etat.poids, etat.taille, etat.objectif, etat.appetit, etat.seances);
      if (e.statut === 'objectif-haut') return resultatRefuse(e);

      var dReg = dateDans(e.regulier);
      var dIrr = dateDans(e.irregulier);
      var nutrition = CONSEILS[etat.appetit];
      var sport = etat.seances === '1' ? CONSEILS.peu : CONSEILS.assez;
      var conseils = [nutrition, sport].map(function (c) {
        return '<a class="sim-conseil" href="' + pre + c.lien + '">' + img('ic-' + c.icone, '', 44) +
          '<span><b>' + c.t + '</b><small>' + c.s + '</small></span></a>';
      }).join('');

      racine.innerHTML = '<div class="sim-carte sim-resultat">' +
        '<p class="sim-sur">Ton résultat</p>' +
        '<h3 tabindex="-1">' + etat.objectif + ' kg : tu pourrais y être vers ' + dateFloue(dReg) + '.</h3>' +
        '<p class="sim-gain">Être régulier peut te faire gagner <b>' + ecart(e.regulier, e.irregulier) + '</b> sur cet objectif.</p>' +
        (e.sousPoids ? '<p class="sim-alerte">Ton poids est bas pour ta taille. Avant de te lancer, parles-en à un médecin, surtout si tu as perdu du poids sans le vouloir ou si manger est difficile en ce moment.</p>' : '') +
        '<div class="sim-duo">' +
          '<div class="sim-scenario sim-avec"><small>Avec un plan suivi presque chaque jour</small><b>' + dateFloue(dReg) + '</b><span>' + duree(e.regulier) + ' · ' + grammes(e.rythme * etat.poids / 100) + ' par semaine au début</span></div>' +
          '<div class="sim-scenario sim-sans"><small>Sans plan, un jour sur deux</small><b>' + dateFloue(dIrr) + '</b><span>' + duree(e.irregulier) + ' · ' + grammes(e.rythme / 2 * etat.poids / 100) + ' par semaine au début</span></div>' +
        '</div>' +
        '<div class="sim-graphe"></div>' +
        '<p class="sim-role"><b>Le rôle de BONGO :</b> t\'aider à tenir le scénario vert, avec tes repas notés en une phrase, des séances guidées et ta série du jour.</p>' +
        '<div class="sim-conseils">' + conseils + '</div>' +
        '<a class="sim-cta" href="' + echapper(store) + '">Télécharger BONGO gratuitement</a>' +
        '<p class="sim-note">Simulation basée sur des repères moyens (0,25 à 0,5 % du poids par semaine), pas une promesse. « Un jour sur deux » suppose que tu manges juste à ton équilibre les autres jours. Ces courbes ne sont pas des résultats mesurés sur des utilisateurs de BONGO. Repères pour adultes en bonne santé, pas un avis médical. <a href="' + echapper(methode) + '">Comment c\'est calculé</a></p>' +
        '<button type="button" class="sim-recommencer">Refaire la simulation</button>' +
        '</div>';
      racine.querySelector('.sim-recommencer').addEventListener('click', function () {
        etat.etape = 0;
        rendre(true);
      });
      nettoyer = dessinerGraphe(racine.querySelector('.sim-graphe'), e);
    }

    function resultatRefuse(e) {
      var message = e.suggestion
        ? "Cet objectif est très élevé pour ta taille, ou trop loin pour qu'une date ait du sens. Une prise de masse se fait par étapes : commence par une première marche, puis on verra la suite."
        : "À ton poids actuel, prendre encore du poids n'est pas forcément utile pour gagner du muscle. Un médecin ou un diététicien pourra t'aider à trouver le bon objectif pour toi.";
      racine.innerHTML = '<div class="sim-carte sim-refus">' + img('bongo-zen', 'sim-bongo', 96) +
        '<h3 tabindex="-1">On préfère ne pas te donner de date.</h3><p>' + message + '</p>' +
        (e.suggestion ? '<button type="button" class="sim-suivant sim-essai">Simuler avec ' + e.suggestion + ' kg</button>' : '') +
        '<button type="button" class="sim-recommencer">Refaire la simulation</button></div>';
      var essai = racine.querySelector('.sim-essai');
      if (essai) essai.addEventListener('click', function () {
        etat.objectif = e.suggestion;
        rendre(true);
      });
      racine.querySelector('.sim-recommencer').addEventListener('click', function () {
        etat.etape = 0;
        rendre(true);
      });
    }

    function rendre(focus) {
      if (nettoyer) { nettoyer(); nettoyer = null; }
      if (etat.etape === 0) etapeMesures();
      else if (etat.etape === 1) etapeObjectif();
      else if (etat.etape === 2) etapeChoix('appetit');
      else if (etat.etape === 3) etapeChoix('seances');
      else resultat();
      if (focus) {
        var h = racine.querySelector('h3');
        if (h) h.focus({ preventScroll: true });
        var haut = racine.getBoundingClientRect().top;
        if (haut < 70 || haut > window.innerHeight * 0.6) {
          racine.scrollIntoView({ behavior: mouvementReduit() ? 'auto' : 'smooth', block: 'start' });
        }
      }
    }

    // ---------- La courbe ----------
    function dessinerGraphe(zone, e) {
      var poids = etat.poids, objectif = etat.objectif, r = e.rythme;
      var total = e.irregulier;
      var legende = document.createElement('div');
      legende.className = 'sim-legende';
      legende.innerHTML = '<span class="sim-leg-v">Avec un plan</span><span class="sim-leg-l">Sans plan, un jour sur deux</span>';
      zone.appendChild(legende);
      var surface = document.createElement('div');
      surface.className = 'sim-surface';
      zone.appendChild(surface);
      var resume = document.createElement('p');
      resume.className = 'sim-bulle';
      zone.appendChild(resume);
      var bongos = ['bongo-neutre', 'bongo-flex-a', 'bongo-fete'].map(function (n) { var i = new Image(); i.src = pre + 'img/' + n + '.webp'; return i.src; });
      var dims, svg, tracés, bongo, fin = false, raf = 0, ech;

      function construire() {
        var L = Math.max(280, zone.clientWidth);
        var H = L < 480 ? 290 : 350;
        var m = { g: 42, d: 14, h: L < 480 ? 72 : 88, b: 34 };
        dims = { L: L, H: H, m: m };
        var yMin = poids - Math.max(1, (objectif - poids) * 0.08);
        ech = {
          x: function (s) { return m.g + (s / total) * (L - m.g - m.d); },
          y: function (k) { return m.h + (1 - (k - yMin) / (objectif - yMin)) * (H - m.h - m.b); }
        };
        var grille = '';
        var pas = objectif - poids <= 4 ? 1 : objectif - poids <= 12 ? 2 : 5;
        for (var k = Math.ceil(poids / pas) * pas; k < objectif - pas * 0.4; k += pas) {
          grille += '<line x1="' + m.g + '" x2="' + (L - m.d) + '" y1="' + ech.y(k) + '" y2="' + ech.y(k) + '" class="sim-g"/>' +
            '<text x="' + (m.g - 7) + '" y="' + (ech.y(k) + 4) + '" text-anchor="end" class="sim-t">' + k + '</text>';
        }
        // Repères de temps : le 1er de chaque mois, espacés selon la longueur de la timeline
        var repT = '';
        var moisTotal = total / 4.345;
        var ecart = Math.max(1, Math.ceil(moisTotal * 66 / (L - m.g - m.d)));
        var depart = new Date();
        var derniereAnnee = depart.getFullYear();
        for (var i = 1; i <= Math.ceil(moisTotal) + 1; i += ecart) {
          var c = new Date(depart.getFullYear(), depart.getMonth() + i, 1);
          var s = (c - depart) / (7 * 864e5);
          if (s >= total) break;
          if (ech.x(s) <= m.g + 42 || ech.x(s) > L - m.d - 24) continue;
          var libelle = MOIS_COURT[c.getMonth()];
          if (c.getFullYear() !== derniereAnnee) { libelle += ' ' + String(c.getFullYear()).slice(2); derniereAnnee = c.getFullYear(); }
          repT += '<text x="' + ech.x(s) + '" y="' + (H - 10) + '" text-anchor="middle" class="sim-t">' + libelle + '</text>';
        }
        repT += '<text x="' + m.g + '" y="' + (H - 10) + '" text-anchor="start" class="sim-t">Auj.</text>';
        surface.style.height = H + 'px';
        surface.innerHTML =
          '<svg width="' + L + '" height="' + H + '" role="img" aria-label="Courbe de poids de ' + poids + ' à ' + objectif + ' kg : ' + duree(e.regulier) + ' avec un plan suivi, ' + duree(e.irregulier) + ' un jour sur deux.">' +
          '<defs><linearGradient id="sim-aire" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#58C536" stop-opacity=".22"/><stop offset="1" stop-color="#58C536" stop-opacity="0"/></linearGradient></defs>' +
          grille + repT +
          '<line x1="' + m.g + '" x2="' + (L - m.d) + '" y1="' + ech.y(objectif) + '" y2="' + ech.y(objectif) + '" class="sim-but"/>' +
          '<text x="' + (m.g - 7) + '" y="' + (ech.y(objectif) + 4) + '" text-anchor="end" class="sim-t sim-t-but">' + objectif + '</text>' +
          '<path class="sim-aire" fill="url(#sim-aire)"/><path class="sim-lent"/><path class="sim-vite"/>' +
          '<line class="sim-guide" y1="' + m.h + '" y2="' + (H - m.b) + '" style="display:none"/>' +
          '<circle class="sim-pt-lent" r="5"/><circle class="sim-pt-vite" r="6" style="display:none"/>' +
          '</svg>';
        svg = surface.querySelector('svg');
        tracés = {
          vite: svg.querySelector('.sim-vite'), lent: svg.querySelector('.sim-lent'), aire: svg.querySelector('.sim-aire'),
          ptLent: svg.querySelector('.sim-pt-lent'), ptVite: svg.querySelector('.sim-pt-vite'), guide: svg.querySelector('.sim-guide')
        };
        bongo = document.createElement('img');
        bongo.className = 'sim-bongo-courbe';
        bongo.alt = '';
        surface.appendChild(bongo);
      }

      function chemin(rr, jusqua) {
        var pts = [], n = Math.max(2, Math.ceil(jusqua * 2));
        for (var i = 0; i <= n; i++) {
          var s = (jusqua * i) / n;
          pts.push(ech.x(s).toFixed(1) + ' ' + ech.y(Math.min(objectif, poidsApres(poids, rr, s))).toFixed(1));
        }
        return 'M' + pts.join('L');
      }

      function poser(t) {
        var sV = Math.min(t, e.regulier), sL = Math.min(t, e.irregulier);
        tracés.vite.setAttribute('d', chemin(r, sV));
        tracés.lent.setAttribute('d', chemin(r / 2, sL));
        tracés.aire.setAttribute('d', chemin(r, sV) + 'L' + ech.x(sV) + ' ' + (dims.H - dims.m.b) + 'L' + ech.x(0) + ' ' + (dims.H - dims.m.b) + 'Z');
        var yL = ech.y(Math.min(objectif, poidsApres(poids, r / 2, sL)));
        tracés.ptLent.setAttribute('cx', ech.x(sL));
        tracés.ptLent.setAttribute('cy', yL);
        var part = sV / e.regulier;
        var taille = (dims.L < 480 ? 36 : 44) + part * (dims.L < 480 ? 28 : 36);
        var src = part >= 1 ? bongos[2] : part > 0.35 ? bongos[1] : bongos[0];
        if (bongo.getAttribute('src') !== src) bongo.setAttribute('src', src);
        bongo.style.width = taille + 'px';
        var bx = Math.min(dims.L - taille, Math.max(0, ech.x(sV) - taille / 2));
        var by = ech.y(Math.min(objectif, poidsApres(poids, r, sV))) - taille + 3;
        bongo.style.transform = 'translate(' + bx + 'px,' + by + 'px)';
        bongo.classList.toggle('arrive', part >= 1);
      }

      function texteFinal() {
        resume.textContent = 'Glisse sur la courbe pour voir ton poids à chaque moment.';
      }

      function jouer() {
        if (mouvementReduit()) { poser(total); fin = true; texteFinal(); return; }
        var duree_ms = 3200, debut = null;
        function pas(t0) {
          if (debut === null) debut = t0;
          var p = Math.min(1, (t0 - debut) / duree_ms);
          poser(total * p);
          if (p < 1) raf = requestAnimationFrame(pas);
          else { fin = true; texteFinal(); }
        }
        resume.textContent = ' ';
        raf = requestAnimationFrame(pas);
      }

      function survol(ev) {
        if (!fin) return;
        var b = surface.getBoundingClientRect();
        var x = Math.min(dims.L - dims.m.d, Math.max(dims.m.g, ev.clientX - b.left));
        var s = ((x - dims.m.g) / (dims.L - dims.m.g - dims.m.d)) * total;
        var pV = Math.min(objectif, poidsApres(poids, r, s));
        var pL = Math.min(objectif, poidsApres(poids, r / 2, s));
        var d = dateDans(s);
        tracés.guide.style.display = '';
        tracés.guide.setAttribute('x1', x);
        tracés.guide.setAttribute('x2', x);
        tracés.ptVite.style.display = '';
        tracés.ptVite.setAttribute('cx', x);
        tracés.ptVite.setAttribute('cy', ech.y(pV));
        tracés.ptLent.setAttribute('cx', x);
        tracés.ptLent.setAttribute('cy', ech.y(pL));
        resume.innerHTML = '<b>' + MOIS[d.getMonth()] + ' ' + d.getFullYear() + '</b> : <span class="sim-v">' + kg(pV) + ' kg</span> avec un plan, <span class="sim-l">' + kg(pL) + ' kg</span> sans plan';
      }
      surface.addEventListener('pointermove', survol);
      surface.addEventListener('pointerdown', survol);

      construire();
      poser(0);

      var lance = false;
      var io = new IntersectionObserver(function (es) {
        if (es[0].isIntersecting && !lance) { lance = true; io.disconnect(); jouer(); }
      }, { threshold: 0.4 });
      io.observe(surface);

      var largeur = zone.clientWidth;
      var ro = new ResizeObserver(function () {
        if (zone.clientWidth === largeur) return;
        largeur = zone.clientWidth;
        cancelAnimationFrame(raf);
        construire();
        poser(total);
        fin = true;
        texteFinal();
      });
      ro.observe(zone);

      return function () { cancelAnimationFrame(raf); io.disconnect(); ro.disconnect(); };
    }

    rendre(false);
  }

  function mouvementReduit() {
    return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }

  document.querySelectorAll('[data-simulateur]').forEach(demarrer);
})();
