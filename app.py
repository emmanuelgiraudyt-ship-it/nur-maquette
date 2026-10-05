"""NÛR (نور) — maquette interactive Streamlit.

Maquette de démonstration : contenus non validés par l'imam garant,
horaires de prière fictifs, aucune publicité, aucune représentation d'être vivant.
"""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import streamlit as st
from hijridate import Gregorian

st.set_page_config(page_title="NÛR — نور", page_icon="☾", layout="wide")

# ---------------------------------------------------------------- données
MOIS_HIJRI = [
    "Mouharram", "Safar", "Rabî' al-awwal", "Rabî' ath-thânî",
    "Joumâdâ al-oûlâ", "Joumâdâ ath-thâniya", "Rajab", "Cha'bân",
    "Ramadan", "Chawwâl", "Dhou al-qa'da", "Dhou al-hijja",
]

PRIERES_DEMO = [
    ("Fajr", "05:45"), ("Dhuhr", "13:10"), ("'Asr", "16:30"),
    ("Maghrib", "19:25"), ("'Ishâ'", "20:50"),
]

NIVEAUX = ["Initié", "Intermédiaire", "Disciple", "Cheikh Premium"]

# Sourate Al-Fâtiha — texte de démonstration, non validé.
VERSETS = [
    {
        "n": 1,
        "ar": "بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ",
        "tr": "Bismi llāhi r-raḥmāni r-raḥīm",
        "fr": "Au nom d'Allah, le Tout Miséricordieux, le Très Miséricordieux.",
        "tajwid": "Assimilation du lâm de « Allâh » et prolongation naturelle (madd) sur « ar-Raḥmân ».",
    },
    {
        "n": 2,
        "ar": "ٱلْحَمْدُ لِلَّهِ رَبِّ ٱلْعَـٰلَمِينَ",
        "tr": "Al-ḥamdu lillāhi rabbi l-ʿālamīn",
        "fr": "Louange à Allah, Seigneur des mondes.",
        "tajwid": "Lâm solaire dans « al-ḥamd » ; prolongation sur « al-ʿâlamîn ».",
    },
    {
        "n": 3,
        "ar": "ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ",
        "tr": "Ar-raḥmāni r-raḥīm",
        "fr": "Le Tout Miséricordieux, le Très Miséricordieux.",
        "tajwid": "Double lâm solaire : assimilation dans le râ'.",
    },
    {
        "n": 4,
        "ar": "مَـٰلِكِ يَوْمِ ٱلدِّينِ",
        "tr": "Māliki yawmi d-dīn",
        "fr": "Maître du Jour de la rétribution.",
        "tajwid": "Prolongation naturelle sur « mâliki » ; lâm solaire dans « ad-dîn ».",
    },
    {
        "n": 5,
        "ar": "إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ",
        "tr": "Iyyāka naʿbudu wa iyyāka nastaʿīn",
        "fr": "C'est Toi seul que nous adorons, et c'est Toi seul dont nous implorons le secours.",
        "tajwid": "Chadda sur le yâ' de « iyyâka » : insister sur le redoublement.",
    },
    {
        "n": 6,
        "ar": "ٱهْدِنَا ٱلصِّرَٰطَ ٱلْمُسْتَقِيمَ",
        "tr": "Ihdina ṣ-ṣirāṭa l-mustaqīm",
        "fr": "Guide-nous dans le droit chemin,",
        "tajwid": "Lettre emphatique ṣâd dans « aṣ-ṣirâṭ » : prononciation pleine.",
    },
    {
        "n": 7,
        "ar": "صِرَٰطَ ٱلَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ ٱلْمَغْضُوبِ عَلَيْهِمْ وَلَا ٱلضَّآلِّينَ",
        "tr": "Ṣirāṭa lladhīna anʿamta ʿalayhim ghayri l-maghḍūbi ʿalayhim wa lā ḍ-ḍāllīn",
        "fr": "le chemin de ceux que Tu as comblés de bienfaits, non pas de ceux qui encourent Ta colère, ni des égarés.",
        "tajwid": "Prolongation obligatoire (madd lâzim) sur « ad-dâllîn » ; emphase du ḍâd.",
    },
]

# ---------------------------------------------------------------- style
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&display=swap');
.arabe {font-family:'Amiri',serif; direction:rtl; text-align:right; font-size:2.2rem;
        line-height:2.4rem; color:#F3EBD3; margin:0.2rem 0;}
.arabe-grand {font-size:3rem; line-height:3.4rem;}
.translit {font-style:italic; color:#C9A24B; font-size:1.05rem;}
.fr {font-size:1.05rem;}
.carte {background:#143A2F; border:1px solid #2B5A4A; border-radius:14px;
        padding:1rem 1.3rem; margin-bottom:0.8rem;}
.bandeau {background:linear-gradient(90deg,#143A2F,#1B4B3C); border:1px solid #C9A24B55;
          border-radius:14px; padding:0.9rem 1.3rem; margin-bottom:1rem;}
.badge {display:inline-block; background:#C9A24B; color:#0E2A22; border-radius:999px;
        padding:0.05rem 0.7rem; font-size:0.8rem; font-weight:700;}
.demo {color:#E8B86D; font-size:0.85rem;}
.prayer-now {color:#C9A24B; font-weight:700;}
.enfant-titre {font-size:2.4rem; text-align:center; color:#C9A24B;}
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------- état
st.session_state.setdefault("niveau", "Initié")
st.session_state.setdefault("mode_enfant", False)
st.session_state.setdefault("gratitudes", [])
st.session_state.setdefault("reflexions", {})
st.session_state.setdefault("etoiles", 0)

# ---------------------------------------------------------------- en-tête
def prochaine_priere(maintenant: datetime):
    for nom, hhmm in PRIERES_DEMO:
        h, m = map(int, hhmm.split(":"))
        t = maintenant.replace(hour=h, minute=m, second=0, microsecond=0)
        if t > maintenant:
            return nom, hhmm, t - maintenant
    nom, hhmm = PRIERES_DEMO[0]
    h, m = map(int, hhmm.split(":"))
    t = (maintenant + timedelta(days=1)).replace(hour=h, minute=m, second=0, microsecond=0)
    return nom, hhmm, t - maintenant


def bandeau():
    now = datetime.now(ZoneInfo("Europe/Paris"))
    hij = Gregorian(now.year, now.month, now.day).to_hijri()
    nom, hhmm, reste = prochaine_priere(now)
    heures, rem = divmod(int(reste.total_seconds()), 3600)
    minutes = rem // 60
    st.markdown(
        f"""<div class="bandeau">
        <b>{hij.day} {MOIS_HIJRI[hij.month - 1]} {hij.year} H</b>
        &nbsp;·&nbsp; {now.strftime('%d/%m/%Y')}
        &nbsp;·&nbsp; Prochaine prière : <span class="prayer-now">{nom} à {hhmm}</span>
        (dans {heures} h {minutes:02d})
        <br><span class="demo">Horaires fictifs de démonstration. Le calcul réel par géolocalisation
        n'est pas inclus dans la maquette.</span></div>""",
        unsafe_allow_html=True,
    )
    cols = st.columns(5)
    for col, (p, h) in zip(cols, PRIERES_DEMO):
        with col:
            st.metric(p, h)


def verset(v, niveau, grand=False):
    cls = "arabe arabe-grand" if grand else "arabe"
    st.markdown(
        f"""<div class="carte"><span class="badge">{v['n']}</span>
        <div class="{cls}">{v['ar']}</div>
        <div class="translit">{v['tr']}</div>
        <div class="fr">{v['fr']}</div></div>""",
        unsafe_allow_html=True,
    )
    if niveau in NIVEAUX[1:]:
        with st.expander(f"Tajwid — verset {v['n']}"):
            st.write(v["tajwid"])
            st.caption("Note indicative de démonstration, non validée par l'imam garant.")


# ---------------------------------------------------------------- barre latérale
with st.sidebar:
    st.markdown("## NÛR  نور")
    st.caption("Maquette de démonstration")
    st.session_state["mode_enfant"] = st.toggle(
        "Interface enfant", value=st.session_state["mode_enfant"]
    )
    if not st.session_state["mode_enfant"]:
        st.session_state["niveau"] = st.selectbox(
            "Niveau d'abonnement (aperçu)",
            NIVEAUX,
            index=NIVEAUX.index(st.session_state["niveau"]),
        )
        page = st.radio(
            "Les quatre actes",
            ["Apprendre", "Réciter", "Méditer", "Aimer", "Offres"],
        )
    else:
        page = "Enfant"
    st.divider()
    st.caption(
        "Zéro publicité. Zéro représentation d'être vivant. "
        "Contenus non validés : démonstration uniquement."
    )

niveau = st.session_state["niveau"]

# ---------------------------------------------------------------- pages
if page == "Enfant":
    st.markdown('<div class="enfant-titre">NÛR — Apprends avec joie</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="carte" style="text-align:center">Écoute, répète, gagne des étoiles.</div>',
        unsafe_allow_html=True,
    )
    i = st.select_slider(
        "Choisis un verset", options=[v["n"] for v in VERSETS], value=1
    )
    v = VERSETS[i - 1]
    st.markdown(
        f"""<div class="carte" style="text-align:center">
        <div class="arabe arabe-grand" style="text-align:center">{v['ar']}</div>
        <div class="translit">{v['tr']}</div><div class="fr">{v['fr']}</div></div>""",
        unsafe_allow_html=True,
    )
    if st.button("J'ai répété ce verset", use_container_width=True):
        st.session_state["etoiles"] += 1
    st.markdown(f"### Étoiles gagnées : {'★' * st.session_state['etoiles'] or '—'}")
    st.caption("Contrôle parental et espace parent prévus dans l'offre famille.")
    bandeau()

elif page == "Apprendre":
    st.title("Apprendre")
    bandeau()
    st.subheader("Sourate Al-Fâtiha — démonstration")
    st.markdown(f"Niveau actif : **{niveau}**")
    for v in VERSETS:
        verset(v, niveau)
    if niveau in ("Disciple", "Cheikh Premium"):
        st.info(
            "Niveau Disciple : parcours approfondi (mot à mot, étude comparée des lectures) "
            "— à concevoir avec l'imam garant. L'arbitrage Warsh / Hafs reste ouvert."
        )
    if niveau == "Cheikh Premium":
        st.warning(
            "Niveau Cheikh Premium : espace de validation et d'annotation des contenus "
            "par l'imam garant (aperçu conceptuel)."
        )

elif page == "Réciter":
    st.title("Réciter")
    bandeau()
    st.subheader("Écoute et récitation")
    st.markdown(
        '<div class="carte">Lecteur audio : emplacement réservé. '
        'Les récitations des qurrâ\' seront intégrées après validation des droits et de l\'imam garant.'
        "</div>",
        unsafe_allow_html=True,
    )
    mode = st.radio(
        "Mode d'entraînement",
        ["Lecture continue", "Texte masqué (réciter de mémoire)"],
        horizontal=True,
    )
    if mode == "Lecture continue":
        for v in VERSETS:
            st.markdown(
                f"<div class='arabe arabe-grand'>{v['ar']} ﴿{v['n']}﴾</div>",
                unsafe_allow_html=True,
            )
    else:
        n = st.number_input("Verset à réciter", 1, len(VERSETS), 1)
        v = VERSETS[n - 1]
        st.write(f"Récitez de mémoire le verset {n}, puis vérifiez.")
        if st.button("Afficher la correction"):
            verset(v, niveau, grand=True)

elif page == "Méditer":
    st.title("Méditer")
    bandeau()
    jour = datetime.now(ZoneInfo("Europe/Paris")).timetuple().tm_yday
    v = VERSETS[jour % len(VERSETS)]
    st.subheader("Verset du jour")
    verset(v, niveau, grand=True)
    st.session_state["reflexions"][v["n"]] = st.text_area(
        "Votre méditation (conservée uniquement pendant cette session)",
        value=st.session_state["reflexions"].get(v["n"], ""),
        height=140,
    )
    st.caption("Aucune donnée n'est enregistrée sur un serveur dans cette maquette.")

elif page == "Aimer":
    st.title("Aimer")
    bandeau()
    st.subheader("Carnet de gratitude et d'intention")
    g = st.text_input("Une gratitude ou une invocation")
    if st.button("Ajouter") and g.strip():
        st.session_state["gratitudes"].append(g.strip())
    for i, x in enumerate(reversed(st.session_state["gratitudes"]), 1):
        st.markdown(f"<div class='carte'>{x}</div>", unsafe_allow_html=True)
    st.subheader("Partager et transmettre")
    st.markdown(
        "<div class='carte'>Partage d'un verset avec un proche, invitation à rejoindre "
        "la famille ou la mosquée : fonctionnalité prévue, non active dans la maquette.</div>",
        unsafe_allow_html=True,
    )

elif page == "Offres":
    st.title("Offres")
    st.caption("Structure seule : les montants ne sont pas fixés (option tarifaire à trancher).")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Individuel")
        for n in NIVEAUX:
            st.markdown(f"- **{n}**" + (" — gratuit" if n == "Initié" else ""))
        st.markdown("#### Famille")
        st.markdown("1 parent et jusqu'à 4 enfants, interface enfant dédiée.")
    with c2:
        st.markdown("#### Mosquée (forfait annuel)")
        st.markdown("- **S** : 50 fidèles\n- **M** : 200 fidèles\n- **L** : illimité")
        st.markdown("#### Principes")
        st.markdown("Zéro publicité. Zéro représentation d'être vivant. Imam garant.")
