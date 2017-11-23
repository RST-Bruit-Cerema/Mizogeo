# Mizogeo
Répertoire dédié au plugin Mizogeo

Mizogeo v2 - modifs apportées

- fichier "creationFichiersGeostandard.py"
	ligne 104 - suppression de l'accent dans le print

- fichier "fenetre_menu_ZBR_CBS_Ui.py"
	ligne 311  - suppression de ""Dialog_ZbrCbs"" qui apparaissait dans l'info-bulle

- fichier "outilFonctions.py"
	ligne 321 - ajout des conditions pour multi-polygones Z (1003, 1006)

- fichier "parametres.py"
	ligne 60 - ajout de "val" et "valmin" dans la liste des champs attributaires imposés dans les fichiers à mettre au GéoStandard

- fichier "parametresFonctions.py"
	ligne 141 - ajout du "elif not gestionnaire" (erreur pour création des dossiers pour les cas de changement de domanialité sur l'ensemble de l'itinéraire)

- fichier "traitementsFichiers.py"
	ligne 76 - suppression de l'accent dans le print

Dossier "ressources"
- fichier "aideMizogeo.pdf"
	page 33 - ajout de la méthode "geom_to_wkt($geometry)" pour déterminer la nature de la géométrie

- suppression du fichier "donneesComplementaires_03102017.csv"
