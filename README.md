# French language tools
Serie d'outils exploitant un dictionnaire français au format .csv.
Le fichier contient +900.000 mots avec leurs variations orthographiques, leurs pluriels, leurs conjugaisons etc.. ainsi que leurs définitions, également en français. Il a été généré en Python sur la base d'un fichier XML contenant la database de fr.wiktionary et selon des méthodes explicitées en détail dans le dossier "en amont", le XML ne se trouvant pas dans le git final en raison de son poids important.

Le dataset .csv a également été publié sur Kaggle : https://www.kaggle.com/datasets/kartmaan/dictionnaire-francais

## Dictionnaire francais
Permet de parcouir le dictionnaire, d'y rechercher un mot et d'en récupérer sa ou ses définitions 

## Lexique français
Outils permettant d'enregistrer des mots provenant du dictionnaire ou personnalisés, dans un fichier Excel .xlsx. L'outils permet entre autres de :
- Ajouter des mots provenant du dictionnaire au lexique
- Ajouter des mots personnalisés au lexique
- Rechercher si un mot est présent dans le lexique
- Supprimer un mot du lexique
