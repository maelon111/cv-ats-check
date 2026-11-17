"""Stop words (FR, EN, NL, DE, ES, normalised without accents) and job-ad boilerplate ignored when picking keywords."""

_FR = """a au aux avec ce ces cet cette dans de des du elle en et eux il ils je la le les leur leurs lui ma mais me meme
mes moi mon ne nos notre nous on ou par pas pour qu que qui sa se ses son sur ta te tes toi ton tu un une vos votre vous
c d j l m n s t y ete etre avoir ai as avons avez ont est sont sera serez etes fait faire plus moins tres tout tous toute
toutes autre autres afin ainsi chez comme dont entre lors selon sans sous vers via deja aussi bien bon bonne etc car si
cela celui celle ceux leurs quel quelle quels quelles chaque peut peuvent doit doivent sein ici"""

_EN = """a an and are as at be been being but by can could did do does for from had has have he her his how i if in into is
it its may me more most must my no nor not of on or our ours she should so some such than that the their them then there
these they this those through to too under up us very was we were what when where which while who whom why will with
would you your yours also any all both each few other own same just over only able across within etc per"""

_NL = """de het een en van in op te dat die is voor met zijn er aan als bij ook om tot uit naar dan wat maar door over ze
zich niet nog wel kan kunnen moet hebben heeft wij we jij je u uw onze ons hun"""

_DE = """der die das und in zu den von mit sich des auf fur ist im dem nicht ein eine als auch es an wird aus er hat dass sie
nach bei um am sind noch wie einem uber einen so zum zur kann nur sein ihre ihr wir sie unser unsere oder"""

_ES = """el la los las un una y de del en con por para que se es son al lo como mas pero sus su nuestro nuestra nosotros
usted ustedes o"""

# Words that appear in almost every job ad and say nothing about the job itself
_JOB_AD = """poste postes offre offres emploi emplois candidat candidate candidats candidature profil profils mission missions
entreprise societe client clients equipe equipes recherche recherchons cherchons rejoindre rejoignez rejoins ans annee
annees experience experiences minimum souhaite souhaitee souhaitable requis requise idealement maitrise connaissance
connaissances capacite capacites qualites esprit sens environnement cadre type contrat cdi cdd temps plein partiel
salaire remuneration avantages lieu date debut h f hf postuler envoyer cv lettre motivation description vos nos votre notre
sein afin travail travailler job role team company candidate candidates position positions looking join we you your
years year experience required preferred plus strong good excellent ability skills knowledge work working environment
salary benefits apply location full time part opportunity responsibilities requirements profile offer offers
atout atouts asset bonus h/f f/h m/f f/m m/w/d m/f/d w/m/d h/f/x un deux trois quatre cinq six sept huit neuf dix one two three four
five six seven eight nine ten twee drie vier zwei drei
vacature functie bedrijf kandidaat stelle stellen unternehmen bewerbung erfahrung kenntnisse puesto empresa"""

STOPWORDS = frozenset(" ".join([_FR, _EN, _NL, _DE, _ES, _JOB_AD]).split())

# Short terms that are real keywords despite having fewer than three letters
SHORT_TERMS = frozenset("""it ui ux qa bi ia ai rh hr ml go c r js ts db erp crm sap seo sea sql php aws gcp api cad dao
b2b b2c pmo cfo cto hse vba etl""".split())
