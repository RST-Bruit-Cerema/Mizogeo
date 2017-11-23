# -*- coding:utf8 -*-
##############################################################################################
##fichier settings.py récapitule lles règles de nommage appliqués dans Mizogeo \
# le role et contenu de chaque fichier utilisé dans le fonctionnement de Miozgeo \
# le nom de chaque variable
##############################################################################################
#REGLE DE NOMMAGE
##############################################################################################
"""
REGLES DE NOMMAGE DES VARIABLES FIGEES
    écrites en minuscules
    en cas de variables composées de plusieurs mots, à chaque changement de mot majuscule
        ex : systCoord
		
REGLES DE NOMMAGE DES VARIABLES NON FIGEES
    écrites en majuscules
        ex : NOMGEOSTANDARDCBS="N_BRUIT_CBS_%s_%s"
			"""
				1er %s = typeTerr
				2ème %s = codeDept 
			"""

REGLES DE NOMMAGE DES FONCTIONS
    écrites avec la 1ère lettre en majuscule et le reste en minuscules 
    en cas de fonctions composées de plusieurs mots, à chaque changement de mot majuscule
        ex : RecuperationTableCorres(urlTableCorrespondance,codInfra)
    exception : les types de fichiers (ZBR, CBS, PPBE) contenus dans les fonctions sont en majuscule
        ex : CreationCBSdbf()
"""
##############################################################################################
#DECOMPOSITION DES FICHIERS UTILISES POUR LE FONCTIONNEMENT DE MIZOGEO
##############################################################################################
"""
   1- fichier "parametres.py" ---> toutes les variables fixes utiles au traitement
        ##Données ressources intégrées dans le plugin 
            noms des fichiers ressources (donneesComplementaires.csv + tableCorrespondance.csv)
            récupération des données complémentaires (autComcbs, autComPpbe)
            récupération de la table de correspondance codInfra/uueid
    
        ##Données sur les fichiers GéoStandard à produire
            noms de fichiers à produire
            champs attributaires imposés par GéoStandard
            valeurs attributaires imposés par GéoStandard
            système de coordonnées
            
        ##Données sur l'arborescence des dossier à produire selon le GéoStandard
            url dossiers à créer
        
    2- fichier "verificationDonnees.py" ---> toutes les fonctions nécessaires au travail de vérifications des données d'entrée à Mizogeo
        ##vérification sur les caractéristiques des fichiers à traiter
            noms des fichiers (ddd_Route_indice pour CBS2012, msig_ddd_Route_indice pour CBS2017)
                liste des codes de département à traiter 
                liste des noms des fichiers Route à traiter
                liste des noms des fichiers Fer à traiter
            table attributaire des fichiers (colonne ID pour CBS2012, colonne ValuesPolygon pour CBS2017)
        
        ##vérification de la validité géométrique des isophones à traiter
        
    3- fichier "recuperationDonnees.py" ---> toutes les fonctions nécessaires au récupération des données à mettre dans le fichier de sortie
        ##import des données depuis le fichier "parametres.py"
            récupération des données complémentaires
            récupération de la table de correspondance
            noms de fichiers à produire
            champs attributaires imposés par GéoStandard
            valeurs attributaires imposés par GéoStandard
            
        ##récupération des attributs des fichiers d'entrée
            attributs isophones CBS2012
            attributs isophones CBS2017
            attibuts limites administratives (codeDept)
                
        ##récupération de la géométrie des fichiers d'entrée
            isophones CBS2012
            isophones CBS2017
            limites adminitratives 
            
    4- fichier "creationFichiersGeostandard.py" ---> toutes les fonctions nécessaires à la création des fichiers imposés par le Géostandard
        ##création des fichiers N_BRUIT_CBS 
        
        ##création des fichiers N_BRUIT_ZBR
        
        ##création des fichiers N_BRUIT_PPBE
        
    5- fichier "traitementsFichiersGeostandard.py" ---> toutes les fonctions nécessaires à l'agrégation et concaténation des fichiers déjà mis au GéoStandard
        ##agrégation des fichiers N_BRUIT_CBS.shp
            union de la géométrie des isophones
            union de la table attributaire
           
        ##concaténation des fichiers 
            concaténation des tables attributaires des fichiers N_BRUIT_CBS.dbf
            concaténation des tables attributaires des fichiers N_BRUIT_ZBR.dbf
"""
##############################################################################################
#LISTE DES VARIABLES ET FONCTIONS : nom et type
##############################################################################################
"""
#fichier parametres.py
    urlTableCorrespondance - type str
    urlDonneesComplementaires - type str
    RecuperationTableCorres(urlTableCorrespondance,codInfra) - renvoie une liste (gestionnaire, uueid,nationalRoadName)
    RecuperationDonneesComplem(urlDonneesComplementaires,codeDept) - renvoie une liste (autComCbs, autComPpbe)
    systCoord - type class 'qgis._core.QgsCoordinateReferenceSystem'
    producteur - type str
    typeTerr - type str
    anneeCbsZbr - type str
    anneePpbe - type str
    champsAttributairesCBS - type class 'qgis._core.QgsFields' (sous forme de liste)
    uueid - type str (issu de RecuperationTableCorres)
    codeDept - type str (sous forme de 3 chiffres)
    typeTerr - type str 
    autComCbs - type str (issu de RecuperationDonneesComplem)
    producteur - type str (sous forme de 9 chiffres)
    codInfra - type str (issu de ...)
    typeSource - type str (issu de 
    nationalRoadName - type str (issu de RecuperationTableCorres)
    typeCBS - type str 
    indiceType
    autComPpbe - type str (issu de RecuperationDonneesComplem)
    
