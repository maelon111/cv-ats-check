# cv-ats-check — votre CV passe-t-il les logiciels de recrutement (ATS) ?

**TL;DR** — Un petit outil open source (Python, licence MIT) qui lit votre CV comme le ferait un logiciel de recrutement
(ATS) et vous dit ce qui bloque : texte illisible, rubriques introuvables, coordonnées absentes, dates manquantes,
mise en page en colonnes, et mots-clés de l'offre que votre CV ne contient pas. Tout tourne sur votre ordinateur :
pas d'IA, pas de réseau, rien n'est envoyé.

- Essayer en ligne, sans rien installer : [Hugging Face Space](https://huggingface.co/spaces/RaphMael/cv-ats-check)
- Analyse plus poussée par IA, gratuite, avec conseils par e-mail (français, anglais, arabe) :
  [jobspeeder.online/analyse-cv](https://jobspeeder.online/analyse-cv?utm_source=github&utm_medium=readme&utm_campaign=cv-ats-check)

*English summary below.*

## Pourquoi

La plupart des entreprises de taille moyenne et des cabinets de recrutement trient les candidatures avec un ATS
(Workday, Teamtailor, Recruitee, Greenhouse, SmartRecruiters, HRSpeeder…). Avant qu'un humain lise votre CV, le
logiciel en extrait le texte, repère les rubriques et cherche les mots-clés du poste. Un CV joli mais exporté en image,
ou monté en deux colonnes, peut arriver vide ou dans le désordre chez le recruteur.

## Installation et usage

```bash
pip install git+https://github.com/maelon111/cv-ats-check
cv-ats-check mon-cv.pdf
cv-ats-check mon-cv.pdf --offre offre.txt          # compare avec le texte d'une offre
cv-ats-check mon-cv.docx --lang en --json          # rapport en anglais, sortie JSON
```

Ou sans installation : `pip install pypdf` puis `python -m cv_ats_check mon-cv.pdf` depuis ce dossier.

Exemple (fichiers dans [`exemples/`](exemples)) :

```text
Analyse ATS du CV
=================
Score global : 92/100
  Lisibilité et structure : 95/100
  Mots-clés de l'offre présents : 88/100

[✔] Le texte est lisible par un logiciel (131 mots).
[✔] Adresse e-mail trouvée : sarah.martin@example.com
[✔] Rubrique « Expérience » trouvée.
[!] CV trop court (131 mots) : visez 300 à 900 mots.
...
Mots-clés de l'offre absents du CV : bob, avancé, rigueur
```

## Ce qui est vérifié

| Contrôle | Pourquoi c'est important pour un ATS |
|---|---|
| Texte extractible | Un PDF scanné ou exporté en image ne contient aucun texte : le CV arrive vide. |
| Caractères illisibles | Les polices d'icônes et certains modèles produisent des « (cid:12) » ou des carrés. |
| Mots collés | Signe qu'une mise en page en colonnes ou en tableau est lue dans le désordre. |
| E-mail, téléphone, LinkedIn | Sans coordonnées lisibles, le recruteur ne peut pas vous rappeler. |
| Rubriques Expérience, Formation, Compétences, Langues | L'ATS range votre parcours grâce aux titres standard (reconnus en français, anglais, néerlandais, allemand, espagnol et arabe). |
| Dates | Les périodes « 2021 – 2024 » servent à calculer vos années d'expérience. |
| Longueur, nombre de pages | 300 à 900 mots, deux pages maximum. |
| Format et nom du fichier | PDF ou DOCX ; « Prenom-Nom-CV.pdf » plutôt que « cv(3).pdf ». |
| Mots-clés de l'offre (option) | Les 25 termes les plus présents dans l'offre, hors mots vides, au féminin et au pluriel près. |

Score : lisibilité et structure seules, ou 60 % structure + 40 % mots-clés quand une offre est fournie.

## Utiliser la bibliothèque

```python
from cv_ats_check import analyse_file, render
rapport = analyse_file("mon-cv.pdf", offer=open("offre.txt").read())
print(rapport.score, rapport.keywords_missing)
print(render(rapport, "fr"))
```

Application web locale : `pip install gradio` puis `python app.py`.

## Limites honnêtes

- Chaque ATS a son propre analyseur : ce contrôle reproduit les erreurs les plus courantes, il ne garantit pas le
  résultat d'un logiciel précis.
- La comparaison de mots-clés est lexicale : elle ne comprend pas les synonymes (« comptabilité » ≠ « finance »).
  N'ajoutez que des mots qui décrivent vraiment votre expérience.
- Le format .doc (Word 97-2003) n'est pas lu : enregistrez-le en PDF ou DOCX.

## FAQ

**Un CV en deux colonnes est-il refusé par les ATS ?** Pas toujours, mais beaucoup d'analyseurs lisent la page ligne
par ligne et mélangent les deux colonnes. Une seule colonne est plus sûre.

**PDF ou Word ?** Les deux sont acceptés par les ATS récents, à condition que le PDF contienne du texte (exporté depuis
un traitement de texte, pas scanné).

**Les icônes et photos posent-elles problème ?** La photo est ignorée ; les icônes à la place des mots (téléphone,
e-mail) font disparaître l'information. Écrivez « +32 470 12 34 56 » en toutes lettres.

**Mes données sont-elles envoyées quelque part ?** Non : l'outil ne fait aucun appel réseau.

## À propos

Outil publié par Raphaël Sellami, fondateur de [JobSpeeder](https://jobspeeder.online/?utm_source=github&utm_medium=readme&utm_campaign=cv-ats-check),
un assistant en recherche d'emploi. Voir aussi la liste
[awesome-recherche-emploi-belgique-france](https://github.com/maelon111/awesome-recherche-emploi-belgique-france).
Contributions bienvenues (nouvelles langues de rubriques, cas d'ATS réels) : ouvrez une issue ou une pull request.

---

## English

**cv-ats-check** reads your CV the way an applicant tracking system (ATS) does and reports what breaks: image-only
PDFs, garbled characters, multi-column layouts, missing contact details, unrecognised section headings (EN, FR, NL,
DE, ES, AR), missing dates, length, file format and name — plus which keywords of a job offer your CV lacks.
Runs locally, no AI, no network.

```bash
pip install git+https://github.com/maelon111/cv-ats-check
cv-ats-check resume.pdf --offer job.txt --lang en
```

Online demo: [Hugging Face Space](https://huggingface.co/spaces/RaphMael/cv-ats-check). Free AI review with
tips by email: [jobspeeder.online/analyse-cv](https://jobspeeder.online/analyse-cv?utm_source=github&utm_medium=readme&utm_campaign=cv-ats-check).

Licence: MIT.
