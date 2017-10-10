# -*- coding: utf-8 -*-
import os 
import time 
from qgis.core import *
import parametres

##############################################################################################################################################################
#PARAMETRES NECESSAIRES A LA DETERMINTAION DES VARIABLES RELATIFS AUX FICHIERS A TRAITER
##############################################################################################################################################################
#fonction listant les valeurs des isophones selon le type de carte LDA (etc) pour les isophones route et fer
def ValeursBordsIsophones(nomdB,typeLigne,typeSource):
    """
    en entrée
        nomdB = type carte (LDA, LNA, LDC, LNC, D) ---> type str
        typeLigne = LGV ou CONV pour gestion des voies ferrées (en carte de type C) ---> type str
        typeSource = F ou R pour gestion des voies ferrées en carte de type C ---> type str 
    en sortie
        liste des bords en dB pour chaque couche ---> type list de list
    """
    valeursBordsIsophones=[]
    if nomdB=='LDA':
        valeursBordsIsophones=[[55,60],[60,65],[65,70],[70,75],[75,1000]]
    elif nomdB=='LNA':
        valeursBordsIsophones=[[50,55],[55,60],[60,65],[65,70],[70,1000]]
    elif nomdB =='LDC':
        if typeSource == 'F':
            if typeLigne=="LGV" : 
                valeursBordsIsophones=[[68,1000]]
            if typeLigne=="CONV" :
                valeursBordsIsophones=[[73,1000]]
        else :
            valeursBordsIsophones=[[68,1000]]
    elif nomdB =='LNC':
        if typeSource == 'F':
            if typeLigne=="LGV" : 
                valeursBordsIsophones=[[62,1000]]
            if typeLigne=="CONV" : 
                valeursBordsIsophones=[[65,1000]]
        else :
            valeursBordsIsophones=[[62,1000]]
    elif nomdB[-1] == 'D':
        valeursBordsIsophones=[[-1000,-8],[-8,-5],[-5,-2],[-2,2],[2,5],[5,8],[8,1000]]
    return valeursBordsIsophones

##############################################################################################################################################################
#PARAMETRES NECESSAIRES A LA DETERMINATION DE L'ARBORESCENCE DES DOSSIERS SELON LE GEOSTANDARD
##############################################################################################################################################################
URLDEPARTEMENT="%s"+os.sep+"%s"
"""
1er %s = urlMillesime
2ème %s= codeDept
"""
#Détermination des noms des dossiers pour créer l'arborescence - partie CBS
URLRESUMECBS="%s"+os.sep+"CBS"+os.sep+"%s"+os.sep+"Resume_CBS"
"""
1er %s = urlDepartement
2ème %s = "Route" ou "Fer"
"""
URLGEOSTANDARDCBS="%s"+os.sep+"CBS"+os.sep+"%s"+os.sep+"GeoStandard"+os.sep+"CBS"
"""
1er %s = urlDepartement
2ème %s = "Route" ou "Fer"
"""
URLGEOSTANDARDCBSMETA="%s"+os.sep+"CBS"+os.sep+"%s"+os.sep+"GeoStandard"+os.sep+"Metadonnees"
"""
1er %s = urlDepartement
2ème %s = "Route" ou "Fer"
"""
URLGESTIONNAIRE="%s"+os.sep+"%s_"+"%s"
"""
1er %s =urlGeostandardCbs
2ème %s =  "1_Etat_nonconcede", "2_Etat_concede", "3_Conseil_Departemental", "4_Commune" ou "1_ligne_ferroviaire", "2_ligne_tramway_metro", 
3ème %s = autComCbs
"""
URLCODINFRA="%s"+os.sep+"%s"
"""
1er %s = urlGestionnaire (c'est-à-dire URLGESTIONNAIRE%(urlGeostandard, "1_Etat_nonconcede") ou URLGESTIONNAIRE%(urlGeostandard, "2_Etat_concede")
2ème %s = codInfra
"""
#URLCODINFRA est le lieu de stockage des fichiers N_BRUIT_CBS_typeTerr_codeDept
URLTYPECARTE="%s"+os.sep+"%s"
"""
1er %s = urlCodInfra
2ème %s = "carte_A","carte_B", "carte_C", "carte_D"
"""
#URLTYPECARTE est le lieu de stockage des fichiers N_BRUIT_ZBR

#Détermination des noms des dossiers pour créer l'arborescence - partie PPBE
URLRESUMEPPBE="%s"+os.sep+"PPBE"+os.sep+"Rapport_PPBE"
"""
1er %s = urlDepartement
"""
URLGEOSTANDARDPPBE="%s"+os.sep+"PPBE"+os.sep+"GeoStandard"+os.sep+"PPBE"
"""
1er %s = urlDepartement
"""

URLGEOSTANDARDPPBEMETA="%s"+os.sep+"PPBE"+os.sep+"GeoStandard"+os.sep+"Metadonnees"
"""
1er %s = urlDepartement
"""

##############################################################################################################################################################
#fonction permettant de définir l'arborescence des dossiers imposés par le GéoStandard pour les fichiers N_BRUIT_CBS
def ArborescenceDossiersGeostandardCbs(uueid,urlSortie,codeDept, autComCbs,gestionnaire,codInfra,natureInfra) : #urlSortie reprend la variable issue de l'interface graphique suite au choix du dossier par l'utilisateur 
    """
    en entrée
    	uueid = code européen récupérer dans TableCorrespondanceNomSIG.csv ---> type str
        urlSortie = chemin du dossier contenant les fichiers créés par Mizogeo ---> type str
        codeDept = code du département issu de la récupération des données infra (fichier recuperationDonnees.py) ---> type str
        autComCbs = numéro Siren de l'autorité compétente pour les CBS (fonction RecuperationDonneesComplem du fichier recuperationDonnees.py) ---> type str
        gestionnaire = type du gestionnaire de la voie cartographiée (fonction RecuperationTableCorrespondance du fichier recuperationDonnees.py) ---> type str
        codInfra = code de l'infrastruture issu de la récupération des données infra (fichier recuperationDonnees.py) ---> type str
    en sortie 
        listeUrlCbs = liste des chemins propres aux fichiers N_BRUIT_CBS  ---> type list de str 
    """
    #initialisation de la liste de stockage des url pour la route
    listeUrlCbs=[]
    #détermination des url définis par le GéoStandard
    urlMillesime=os.path.join(urlSortie,"Grandes_infrastructures_Millesime_2017")
    urlDepartement=URLDEPARTEMENT%(urlMillesime,codeDept)
    if natureInfra=="R" :
        urlResumeCbs=URLRESUMECBS%(urlDepartement, "Route")
        urlGeostandardCbs=URLGEOSTANDARDCBS%(urlDepartement, "Route")
        urlGeostandardMeta=URLGEOSTANDARDCBSMETA%(urlDepartement, "Route")
    else :
        urlResumeCbs=URLRESUMECBS%(urlDepartement, "Fer")
        urlGeostandardCbs=URLGEOSTANDARDCBS%(urlDepartement, "Fer")
        urlGeostandardMeta=URLGEOSTANDARDCBSMETA%(urlDepartement, "Fer")
    #détermination du dossier à créer selon la nature du gestionnaire (donnée récupérée dans la tableCorrespondanceRoute.csv pour la route via la fonction RecuperationTableCorres)
    if gestionnaire =="Etat_nonconcede" and uueid <> '':
        urlGestionnaire=URLGESTIONNAIRE%(urlGeostandardCbs,"1_Etat_nonconcede",autComCbs)
    elif gestionnaire =="Etat_concede" and uueid <> '': 
        urlGestionnaire=URLGESTIONNAIRE%(urlGeostandardCbs,"2_Etat_concede",autComCbs)
    elif gestionnaire =="Conseil_Departemental" and uueid <> '':
        urlGestionnaire=URLGESTIONNAIRE%(urlGeostandardCbs,"3_Conseil_Departemental",autComCbs)
    elif gestionnaire =="SNCF-Reseau" and uueid <> '':
        urlGestionnaire = URLGESTIONNAIRE%(urlGeostandardCbs,"0_ligne_ferroviaire",autComCbs)   
    elif gestionnaire == "Metropole" and uueid <> '':
    	urlGestionnaire = URLGESTIONNAIRE%(urlGeostandardCbs,"5_Metropole",autComCbs)
    elif gestionnaire in ["Etat_nonconcede","Etat_concede","Conseil_Departemental","SNCF-Reseau", "Metropole"] and uueid <> '': 
        urlGestionnaire = URLGESTIONNAIRE%(urlGeostandardCbs,"4_Commune",autComCbs)         
    else :
        urlGestionnaire=URLGESTIONNAIRE%(urlGeostandardCbs,"Voies_nouvelles",autComCbs)
    #détermination du dossier à créer à partir du codInfra (donnée récupérée à partir du nom des fichiers isophones à traiter)
    urlCodInfra=URLCODINFRA%(urlGestionnaire,codInfra)
    #détermination des dossiers de stockage selon le type de carte 
    urlCarteA=URLTYPECARTE%(urlCodInfra,"carte_a")
    urlCarteB=URLTYPECARTE%(urlCodInfra,"carte_b")
    urlCarteC=URLTYPECARTE%(urlCodInfra,"carte_c")
    urlCarteD=URLTYPECARTE%(urlCodInfra,"carte_d")
    #liste de stockage des url 
    listeUrlCbs.append(urlMillesime)
    listeUrlCbs.append(urlDepartement)
    listeUrlCbs.append(urlResumeCbs)
    listeUrlCbs.append(urlGeostandardCbs)
    listeUrlCbs.append(urlGeostandardMeta)
    listeUrlCbs.append(urlGestionnaire)
    listeUrlCbs.append(urlCodInfra)
    listeUrlCbs.append(urlCarteA)
    listeUrlCbs.append(urlCarteB)
    listeUrlCbs.append(urlCarteC)
    listeUrlCbs.append(urlCarteD)
    return listeUrlCbs

#fonction permettant de définir l'arborescence des dossiers imposés par le GéoStandard pour les fichiers N_BRUIT_PPBE
def ArborescenceDossiersGeostandardPpbe(urlSortie,codeDept) : #urlSortie reprend la variable issue de l'interface graphique suite au choix du dossier par l'utilisateur 
    """
    en entrée 
        urlSortie = chemin du dossier contenant les fichiers créés par Mizogeo ---> type str
        codeDept = code du département issu de la récupération des données infra (fichier recuperationDonnees.py) ---> type str
    en sortie 
        listeUrlPpbe liste des chemins propres aux fichiers N_BRUIT_PPBE  ---> type list de str 
    """
    #initialisation de la liste de stockage des url pour la route
    listeUrlPpbe=[]
    #détermination des url définis par le GéoStandard
    urlMillesime=os.path.join(urlSortie,"Grandes_infrastructures_Millesime_2017")
    urlDepartement=URLDEPARTEMENT%(urlMillesime,codeDept)
    urlResumePpbe=URLRESUMEPPBE%(urlDepartement)
    urlGeostandardPpbe=URLGEOSTANDARDPPBE%(urlDepartement)
    urlGeostandardPpbeMeta=URLGEOSTANDARDPPBEMETA%(urlDepartement)
    #liste de stockage des url 
    listeUrlPpbe.append(urlMillesime)
    listeUrlPpbe.append(urlDepartement)
    listeUrlPpbe.append(urlResumePpbe)
    listeUrlPpbe.append(urlGeostandardPpbe)
    listeUrlPpbe.append(urlGeostandardPpbeMeta)
    return listeUrlPpbe

#fonction de création de l'arborescence complète imposée par le GéoStandard en regardant dossier par dossier s'il n'existe pas
def CreationArborescenceDossiersGeostandard(uueid,urlSortie,gestionnaire,natureInfra,typeCbs,codeDept,autComCbs,codInfra) :
    """
    en entrée
        urlSortie = chemin du dossier contenant les fichiers créés par Mizogeo ---> type str
        gestionnaire = type du gestionnaire de la voie cartographiée (fonction RecuperationTableCorrespondance du fichier recuperationDonnees.py) ---> type str
        natureInfra = route ou fer  ---> type str
        typeCbs = type de carte (A, B, C ou D) ---> type str
        codeDept = code du département issu de la récupération des données infra (fichier recuperationDonnees.py) ---> type str
        autComCbs = numéro Siren de l'autorité compétente CBS ---> type str
        codInfra = code de l'infrastruture issu de la récupération des données infra (fichier recuperationDonnees.py) ---> type str
    en sortie 
        dossierZbr = emplacement du fichier N_BRUIT_ZBR ---> type str
        dossierCbs = emplacement du fichier N_BRUIT_CBS ---> type str
    """
    listeUrlCbs=ArborescenceDossiersGeostandardCbs(uueid,urlSortie,codeDept, autComCbs,gestionnaire,codInfra,natureInfra)
    for url in listeUrlCbs :  
        if url==listeUrlCbs[7] or url==listeUrlCbs[8] or url==listeUrlCbs[9] or url==listeUrlCbs[10]:
            if typeCbs=="A" :
                dossierZbr=listeUrlCbs[7]
                if not os.path.exists(dossierZbr) :
                    os.makedirs(dossierZbr)
            if typeCbs=="B" :
                dossierZbr=listeUrlCbs[8]
                if not os.path.exists(dossierZbr) : 
                    os.makedirs(dossierZbr)
            if typeCbs=="C" :
                dossierZbr=listeUrlCbs[9]
                if not os.path.exists(dossierZbr) :
                    os.makedirs(dossierZbr)
            if typeCbs=="D" : 
                dossierZbr=listeUrlCbs[10]
                if not os.path.exists(dossierZbr) : 
                    os.makedirs(dossierZbr)
        else :
            if not os.path.exists(url) : 
                os.makedirs(url)
    dossierCbs=listeUrlCbs[6]
    if ('dossierZbr' in locals()) or ('dossierZbr' in globals()) :
        pass 
    else:
        dossierZbr="DossierZbrIntrouvable"
    return (dossierZbr,dossierCbs)

#################################################################################################################################################################################################
#DETERMINTAION DES VARIABLES RELATIFS AUX FICHIERS A CREER SELON LE GEOSTANDARD
#################################################################################################################################################################################################
#NOMS IMPOSES PAR LE GEOSTANDARD DES FICHIERS A CREER 
####fichier N_BRUIT_CBS
NOMGEOSTANDARDCBS="N_BRUIT_CBS_%s_%s_%s"#.dbf"
"""
1er %s = typeTerr
2ème %s = codInfra
3ème %s = codeDept 
"""
####fichier N_BRUIT_ZBR shp
NOMGEOSTANDARDZBR="N_BRUIT_ZBR_%s_%s_%s_%s_%s_S_%s.shp"
"""
1er %s = typeTerr
2ème %s = typeSource
3ème %s = codInfra
4ème %s = typeCbs
5ème %s = indiceType
6ème %s = codeDept
"""
####fichier N_BRUIT_ZBR fichier style format qml
NOMGEOSTANDARDQML="N_BRUIT_ZBR_%s_%s_%s_%s_%s_S_%s.qml"
"""
1er %s = typeTerr
2ème %s = typeSource
3ème %s = codInfra
4ème %s = typeCbs
5ème %s = indiceType
6ème %s = codeDept
"""
####fichier N_BRUIT_PPBE
NOMGEOSTANDARDPPBE="N_BRUIT_PPBE_%s_S_%s.shp"
"""
1er %s = typeTerr
2ème %s = codeDept
"""
#################################################################################################################################################################################################
#DETERMINTAION DES VARIABLES RELATIFS AUX FICHIERS A CRER LORS DE LA CONCATENATION ET L'AGREGATION
#################################################################################################################################################################################################
####fichier assemblage N_BRUIT_ZBR
NOMASSEMBLZBR="Assemblage_N_BRUIT_ZBR"
####fichier assemblage N_BRUIT_CBS
NOMASSEMBLCBS="Assemblage_N_BRUIT_CBS"
####fichier agrégation N_BRUIT_ZBR
NOMAGREGZBR="Agregation_N_BRUIT_ZBR_%s"
"""
%s = indice (LDA, LNA, etc)
"""
####fichier agrégation N_BRUIT_ZBR
NOMAGREGQML="Agregation_N_BRUIT_ZBR_%s.qml"
"""
%s = indice (LDA, LNA, etc)
"""
#fonction qui fixe les valeurs attributaires pour les fichiers N_BRUIT_CBS (format dbf) liste des valeurs attributaires selon le GeoStandard
def ValeursAttributairesCBS(anneeCbsZbr,autComCbs,codInfra,codeDept,uueid,typeTerr,producteur,nationalRoadName,autComPpbe) :
    """
    en entrée 
        anneeCbsZbr = issue de parametres.py ---> type str
        autComCbs = numéro Siren de l'autorité compétente des CBS ---> type str
        codInfra = code de l'infrastruture issu de la récupération des données infra (fichier recuperationDonnees.py) ---> type str
        codeDept = code du département issu de la récupération des données infra (fichier recuperationDonnees.py) ---> type str
        uueid --> type str
        typeTerr = issu de parametres.py ---> type str
        producteur = issu de parametres.py ---> type str
        nationalRoadName ---> type str
        autComPpbe = numéro Siren de l'autorité compétente des PPBE ---> type str
    en sortie
        valeursAttributairesCbsRoute = dictionnaire avec comme clés les nomdB (LDA,LNA,etc) et comme valeurs, les valeurs attributaires des fichiers N_BRUIT_CBS Route ---> type dict
        valeursAttributairesCbsFer = dictionnaire avec comme clés les nomdB (LDA,LNA,etc) et comme valeurs, les valeurs attributaires des fichiers N_BRUIT_CBS Fer ---> type dict
    """
    #déclaration des variables servant de valeurs attributaires
    typesSource=["R","F"]
    nomsCarte=["LDA","LNA","LNU","LDC","LNC","LDD","LND"]
    #initialisation des dictionnaires de sortie 
    valeursAttributairesCbsRoute={}
    valeursAttributairesCbsFer={}
    #initialisation des listes de stockage des valeurs attributiares CBS
    listeValeursAttributairesCbsRoute=[]
    listeValeursAttributairesCbsFer=[]
    #initialisation des listes contenant les valeurs attributaires pour chaque type de cartes et type de nature d'infra
    #pour route 
    valeursLDARoute=[]
    valeursLNARoute=[]
    valeursLNURoute=[]
    valeursLDCRoute=[]
    valeursLNCRoute=[]
    valeursLDDRoute=[]
    valeursLNDRoute=[]
    #pour fer
    valeursLDAFer=[]
    valeursLNAFer=[]
    valeursLNUFer=[]
    valeursLDCFer=[]
    valeursLNCFer=[]
    valeursLDDFer=[]
    valeursLNDFer=[]
    #on boucle sur le type de Source pour sortir la liste des valeurs attributaires correspondantes
    for typeSource in typesSource : 
        for nomCarte in nomsCarte:
            if nomCarte != "LNU" : 
                indiceType=nomCarte[0:2] #2 premières lettres de nomCarte (LD ou LN)
                typeCBS=nomCarte[-1] 
            else : 
                typeCBS="B"
                indiceType="00"
            listeValeursAttributairesCBS=[str("CBS"+anneeCbsZbr+codeDept+autComCbs+"."+typeSource+"-"+codInfra+"-"+typeCBS +"-" + indiceType), \
                uueid, \
                anneeCbsZbr, \
                codeDept, \
                typeTerr, \
                autComCbs, \
                producteur, \
                codInfra, \
                typeSource, \
                nationalRoadName, \
                str(""), \
                str("01"), \
                str(""), \
                typeCBS, \
                indiceType, \
                autComPpbe, \
                str(""), \
                time.strftime('%Y-%m-%d',time.localtime()) , \
                str("")]
            #pour route
            if nomCarte=="LDA" and typeSource=="R": 
                valeursLDARoute=listeValeursAttributairesCBS
            if nomCarte=="LNA" and typeSource=="R": 
                valeursLNARoute=listeValeursAttributairesCBS
            if nomCarte=="LNU" and typeSource=="R":
                valeursLNURoute=listeValeursAttributairesCBS
            if nomCarte=="LDC"  and typeSource=="R" : 
                valeursLDCRoute=listeValeursAttributairesCBS
            if nomCarte=="LNC"  and typeSource=="R" : 
                valeursLNCRoute=listeValeursAttributairesCBS
            if nomCarte=="LDD" and typeSource=="R":
                valeursLDDRoute=listeValeursAttributairesCBS
            if nomCarte=="LND" and typeSource=="R":
                valeursLNDRoute=listeValeursAttributairesCBS
            #pour fer 
            if nomCarte=="LDA" and typeSource=="F": 
                valeursLDAFer=listeValeursAttributairesCBS
            if nomCarte=="LNA" and typeSource=="F":
                valeursLNAFer=listeValeursAttributairesCBS
            if nomCarte=="LNU" and typeSource=="F":
                valeursLNUFer=listeValeursAttributairesCBS
            if nomCarte=="LDC"  and typeSource=="F" :
                valeursLDCFer=listeValeursAttributairesCBS
            if nomCarte=="LNC"  and typeSource=="F":
                valeursLNCFer=listeValeursAttributairesCBS
            if nomCarte=="LDD" and typeSource=="F":
                valeursLDDFer=listeValeursAttributairesCBS
            if nomCarte=="LND" and typeSource=="F":
                valeursLNDFer=listeValeursAttributairesCBS
    listeValeursAttributairesCbsRoute=(valeursLDARoute,valeursLNARoute,valeursLNURoute, valeursLDCRoute, valeursLNCRoute,valeursLDDRoute,valeursLNDRoute)
    listeValeursAttributairesCbsFer=(valeursLDAFer,valeursLNAFer,valeursLNUFer, valeursLDCFer, valeursLNCFer,valeursLDDFer,valeursLNDFer)
    valeursAttributairesCbsRoute=dict(zip(nomsCarte,listeValeursAttributairesCbsRoute))
    valeursAttributairesCbsFer=dict(zip(nomsCarte,listeValeursAttributairesCbsFer))
    return valeursAttributairesCbsRoute, valeursAttributairesCbsFer
    
#fonction qui fixe les valeurs attributaires pour ficihier N_BRUIT_ZBR listes des couples 
def ValeursAttributairesZBR(anneeCbsZbr,autComCbs,codInfra,codeDept,uueid,typeTerr,producteur,typeLigne) :
    """
    en entrée
        anneeCbsZbr = issue de parametres.py ---> type str
        autComCbs = numéro Siren de l'autorité compétente des CBS ---> type str
        codInfra = code de l'infrastruture issu de la récupération des données infra (fichier recuperationDonnees.py) ---> type str
        codeDept = code du département issu de la récupération des données infra (fichier recuperationDonnees.py) ---> type str
        uueid --> type str
        typeTerr = issu de parametres.py ---> type str
        producteur = issu de parametres.py ---> type str
        typeLigne ---> type str
    en sortie
        ValeursAttributairesZbrRoute = dictionnaire avec comme clés les nomdB (LDA,LNA,etc) et comme valeurs, les valeurs attributaires des fichiers N_BRUIT_ZBR Route ---> type dict
        ValeursAttributairesZbrFerLgv = dictionnaire avec comme clés les nomdB (LDA,LNA,etc) et comme valeurs, les valeurs attributaires des fichiers N_BRUIT_ZBR Fer TGV ---> type dict
        ValeursAttributairesZbrFerConv = dictionnaire avec comme clés les nomdB (LDA,LNA,etc) et comme valeurs, les valeurs attributaires des fichiers N_BRUIT_ZBR Fer ligne conventionnelle ---> type dict
    """
    typesSource=["R","F"]
    nomsCarte=["LDA","LNA","LNU","LDC","LNC","LDD","LND"]
    ValeursAttributairesZbrRoute={}
    ValeursAttributairesZbrFerConv={}
    ValeursAttributairesZbrFerLgv={}
    listeValeursAttributairesZbrRoute=[]
    listeValeursAttributairesZbrFerConv=[]
    listeValeursAttributairesZbrFerLgv=[]
    #initialisation des listes contenant les valeurs attributaires pour chaque type de cartes et type de nature d'infra
    #pour route 
    valeursLDARoute=[]
    valeursLNARoute=[]
    valeursLNURoute=[]
    valeursLDCRoute=[]
    valeursLNCRoute=[]
    valeursLDDRoute=[]
    valeursLNDRoute=[]
    #pour fer
    valeursLDAFer=[]
    valeursLNAFer=[]
    valeursLNUFer=[]
    valeursLDCFerLgv=[]
    valeursLDCFerConv=[]
    valeursLNCFerLgv=[]
    valeursLNCFerConv=[]
    valeursLDDFer=[]
    valeursLNDFer=[]
    for typeSource in typesSource :
        for nomCarte in nomsCarte:
            if nomCarte != "LNU" : 
                indiceType=nomCarte[0:2] #2 premières lettres de nomCarte (LD ou LN)
                typeCBS=nomCarte[-1] #dernière lettre de nomCarte (A, B, C, D)
            else : 
                typeCBS="B"
                indiceType="00"
            if nomCarte=="LDA" : 
                legendes=[55,60,65,70,75]
                zoneDef="01"
            if nomCarte=="LNA" : 
                legendes=[50,55,60,65,70]
                zoneDef="00"
            if nomCarte=="LNU" : 
                legendes=["00"]
                zoneDef="00"
            if nomCarte=="LDC"  and typeSource=="R" : 
                legendes=[68]
                zoneDef="03"
            if nomCarte=="LNC"  and typeSource=="R" : 
                legendes=[62]
                zoneDef="04"
            if nomCarte=="LDC"  and typeSource=="F" :
                if typeLigne=="LGV" : 
                    legendes=[68]
                if typeLigne=="CONV" : 
                    legendes=[73]
                zoneDef="03"
            if nomCarte=="LNC"  and typeSource=="F":
                if typeLigne=="LGV": 
                    legendes=[62]
                if typeLigne=="CONV":
                    legendes=[65]
                zoneDef="04"
            if nomCarte=="LDD":
                legendes=["+8","+5","+2","+0","-2","-5","-8"]
                zoneDef="05"
            if nomCarte=="LND":
                legendes=["+8","+5","+2","+0","-2","-5","-8"]
                zoneDef="06"
            for legende in legendes :
                listeValeursAttributairesZBR=[str("ZBR"+anneeCbsZbr+codeDept+autComCbs+"."+typeSource+"-"+codInfra+"-"+typeCBS+'-'+ indiceType+str(legende)), \
                    str("CBS"+anneeCbsZbr+codeDept+autComCbs+"."+typeSource+"-"+codInfra+"-"+typeCBS +"-" + indiceType), \
                    uueid, \
                    anneeCbsZbr, \
                    codeDept, \
                    typeTerr, \
                    producteur, \
                    codInfra, \
                    typeSource, \
                    typeCBS, \
                    zoneDef, \
                    legende, \
                    indiceType, \
                    time.strftime('%Y-%m-%d',time.localtime()) , \
                    str("")]
                #pour route
                if nomCarte=="LDA" and typeSource=="R": 
                    valeursLDARoute=listeValeursAttributairesZBR
                if nomCarte=="LNA" and typeSource=="R": 
                    valeursLNARoute=listeValeursAttributairesZBR
                if nomCarte=="LNU" and typeSource=="R":
                    valeursLNURoute=listeValeursAttributairesZBR
                if nomCarte=="LDC"  and typeSource=="R" : 
                    valeursLDCRoute=listeValeursAttributairesZBR
                if nomCarte=="LNC"  and typeSource=="R" : 
                    valeursLNCRoute=listeValeursAttributairesZBR
                if nomCarte=="LDD" and typeSource=="R":
                    valeursLDDRoute=listeValeursAttributairesZBR
                if nomCarte=="LND" and typeSource=="R":
                    valeursLNDRoute=listeValeursAttributairesZBR
                #pour fer 
                if nomCarte=="LDA" and typeSource=="F": 
                    valeursLDAFer=listeValeursAttributairesZBR
                if nomCarte=="LNA" and typeSource=="F":
                    valeursLNAFer=listeValeursAttributairesZBR
                if nomCarte=="LNU" and typeSource=="F":
                    valeursLNUFer=listeValeursAttributairesZBR
                if nomCarte=="LDC"  and typeSource=="F" :
                    if typeLigne=="LGV" : 
                        valeursLDCFerLgv=listeValeursAttributairesZBR
                    if typeLigne=="CONV" : 
                        valeursLDCFerConv=listeValeursAttributairesZBR
                if nomCarte=="LNC"  and typeSource=="F":
                    if typeLigne=="LGV": 
                        valeursLNCFerLgv=listeValeursAttributairesZBR
                    if typeLigne=="CONV":
                        valeursLNCFerConv=listeValeursAttributairesZBR
                if nomCarte=="LDD" and typeSource=="F":
                    valeursLDDFer=listeValeursAttributairesZBR
                if nomCarte=="LND" and typeSource=="F":
                    valeursLNDFer=listeValeursAttributairesZBR
    listeValeursAttributairesZbrRoute=(valeursLDARoute,valeursLNARoute,valeursLNURoute, valeursLDCRoute, valeursLNCRoute,valeursLDDRoute,valeursLNDRoute)
    listeValeursAttributairesZbrFerLgv=(valeursLDAFer,valeursLNAFer,valeursLNUFer, valeursLDCFerLgv, valeursLNCFerLgv,valeursLDDFer,valeursLNDFer)
    listeValeursAttributairesZbrFerConv=(valeursLDAFer,valeursLNAFer,valeursLNUFer, valeursLDCFerConv, valeursLNCFerConv,valeursLDDFer,valeursLNDFer)
    ValeursAttributairesZbrRoute=dict(zip(nomsCarte,listeValeursAttributairesZbrRoute))
    ValeursAttributairesZbrFerLgv=dict(zip(nomsCarte,listeValeursAttributairesZbrFerLgv))
    ValeursAttributairesZbrFerConv=dict(zip(nomsCarte,listeValeursAttributairesZbrFerConv))
    return ValeursAttributairesZbrRoute, ValeursAttributairesZbrFerLgv,ValeursAttributairesZbrFerConv


#valeurs attributaires pour ficihier N_BRUIT_PPBE listes des couples 
def ValeursAttributairesPPBE(anneePpbe,codeDept,autComPpbe,typeTerr,producteur) :
    """
    en entrée 
        anneePpbe = issue de parametres.py
        codeDept = code du département issu de la récupération des données infra (fichier recuperationDonnees.py) ---> type str
        autComPpbe = numéro Siren de l'autorité compétente des PPBE ---> type str
        typeTerr = issu de parametres.py ---> type str
        producteur = issu de parametres.py ---> type str
    en sortie
        valeursAttributairesPPBE = liste des valeurs attributaires pour les fichiers N_BRUIT_PPBE ---> type list
    """
    valeursAttributairesPPBE=[str("PPBE"+anneePpbe+codeDept+autComPpbe+"."+typeTerr+"_E_TT"), \
                    anneePpbe, \
                    codeDept, \
                    typeTerr, \
                    parametres.typePpbe, \
                    autComPpbe, \
                    producteur, \
                    str("PPBEETAT"+codeDept), \
                    str(""), \
                    str("01"), \
                    str(""), \
                    time.strftime('%Y-%m-%d',time.localtime()), \
                    str("")]
    return valeursAttributairesPPBE