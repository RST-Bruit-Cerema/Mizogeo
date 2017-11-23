# -*- coding: utf-8 -*-
import csv
from parametres import *#from parametres import urlTableCorrespondanceFer,urlDonneesComplementaires,gestionnaire, uueid, nationalRoadName,ListeChampsImpose
import interfaceUtilisateur
from outilsFonctions import OutilRechercherValeursdBIsophones,OutilDetectionNomChampsAttributaires,OutilRechercheNomDansListe
from qgis.core import *
from PyQt4.QtGui import QMessageBox
from PyQt4.QtCore import QCoreApplication
import os

#################################################################################################################################################################################################
#RECUPERATION DES DONNEES PROPRES AUX FICHIERS A TRAITER
#################################################################################################################################################################################################  
#Ouverture de fichier csv
def OuvreCSV(urlFichier):
    """
    en entrée
        URLFichier ---> type str
    en sortie
        table csv ---> matrice de type tab[Numéro ligne][Numéro colonne]
    """
    # modifie le fichier en csv et fixer le delimiteur
    bonDelimiteur=''
    Nb=0
    for separateur in [';',',','\t']:
        fichierCsv =open(urlFichier, "r")
        try :
            lectureCsv=csv.reader(fichierCsv,delimiter=separateur)
            tableCsv=list(lectureCsv)
            if Nb<len(tableCsv[0]):
                bonDelimiteur=separateur
                Nb=len(tableCsv[0])
        except:
            1
        fichierCsv.close()
    fichierCsv =open(urlFichier, "r")
    lectureCsv=csv.reader(fichierCsv,delimiter=bonDelimiteur)
    tableCsv=list(lectureCsv)
    # crée  une matrice
    return tableCsv# renvoie une valeur de la matrice : tab[Numéro ligne][Numéro colonne]


#Récupération du format des cartes (2012 ou sortis de MithraSIG) pour le fichier mémorisé dans la liste des fichiers à traiter 
def RecuperationNatureFichier(nomFichierSansExt,partieNomAVerifier,txtCherche):
    """
    en entrée
        nomFichierSansExt (nom du fichier sans extension) ---> type str
        partieNomAVerifier (début du fichier spécifique permettant d'identifier le fichier)
        txtCherche (début nom du fichier recherché) ---> type str
    en sortie
        listeFichiers (liste des fichiers triés selon le début du nom du fichier) ---> type list
    """
    #initialisation des listes de stockage des couches format 2012 et couches au format Msig
    listeFichiers=[]
    if partieNomAVerifier==txtCherche : 
        listeFichiers.append(nomFichierSansExt)
        return listeFichiers
    else :                                        
        return False  
    
#Récupération du type de carte en se basant sur le dernier caractère du nom du fichier isophones
def RecuperationTypeCBS(nomFichierIsophone) : 
    """
    en entrée
        nom fichier isophone sans extension ---> type str
    en sortie
        type de la carte A, B, C ou D (typeCbs) ---> type str
    """
    typeCbs=nomFichierIsophone[-1] #dernière lettre du nom du fichier
    if typeCbs=="U" : 
        typeCbs="B"
    return typeCbs


#Récupération du niveau de bruit indiqué dans la valeur attributaire de la couche Isophone
def RecuperationValeurdB(urlDossierIsophone,nomFichierIsophoneExt,nomFichierIsophone,format2012,formatMsig) : 
    """
    en entrée
        nom du fichier isophone avec extension  ---> type str
    en sortie
        liste des valeurs dB indiquées dans les valeurs attributaires id ou Valmin ---> type list
    """
    #initialisation de la liste dans laquelle seront stockées les valeurs en dB des isophones
    listeValeursdB=[]
    #détermination du fichierIsophone comme couche SIG 
    coucheIsophone= QgsVectorLayer(urlDossierIsophone+os.sep+nomFichierIsophoneExt, "couche Isophone", "ogr") #j ouvre le fichier
    #si le fichierIsophone est au format 2012
    if nomFichierIsophone in format2012 : 
        #récupération de la valeur dB
        for objetIsophone in coucheIsophone.getFeatures() :
            Iso=int(objetIsophone['id'][-2:]) #prend le dB (2 dernières lettres de la valeur attributaire indiquée dans la colonne id ou Id ou ID)
    if nomFichierIsophone in formatMsig : 
        for objetIsophone in coucheIsophone.getFeatures() :
            Iso=objetIsophone['Valmin'] #prend le dB
    listeValeursdB.append(Iso)
    return listeValeursdB


#Passage du codInfraFormat2012 au codInfra (imposé par le Géostandard) pour les fichiers Route et Fer (même si pas de différence pour le Fer)
#par exemple, passer de N0007 à N7
def RecuperationCodInfra(codInfraFormat2012):
    """
    en entrée
        codInfraFormat2012 (résultat de la fonction OutilDecoupageNomFichier) ---> type str
            du type route : on supprime les zéros inutiles
            du type fer ou voie communale : on change rien
    en sortie
        codInfra format Géostandard ---> type str
    """
    #initialisation du texte 
    typeVoie=codInfraFormat2012[0]
    #pour les infras routières
    if not(typeVoie in ["0","1","2","3","4","5","6","7","8","9","C","V"]):
        if not(codInfraFormat2012[-1] in ["0","1","2","3","4","5","6","7","8","9"]):
            numRoute=str(int(codInfraFormat2012[1:-1]))+codInfraFormat2012[-1]
        else :
            numRoute=str(int(codInfraFormat2012[1:]))
        codInfra=typeVoie+numRoute
    #pour les voies ferrées et voies communales
    else :
        codInfra=codInfraFormat2012
    return codInfra


#Récupération de typeSource - valeur nécessaire pour le nom du fichier N_BRUIT_CBS
def RecuperationTypeSource(codInfra):
    """
	en entrée
        nom fichier isophone sans extension ---> type str
	en sortie
        typeSource comme indiqué dans le Géostandard ---> type str
    """
    natureRoute=codInfra[0]
    if natureRoute in ["0","1","2","3","4","5","6","7","8","9"] :
        typeSource="F"
    else: 
		typeSource="R"        
    return typeSource
	

#Récupération de indiceType au format GéoStandard 
def RecuperationIndiceType(nomdB,typeCbs):
	"""
	en entrée 
		nomdB ---> type str
		typeCbs ---> type str
	en sortie 
		indiceType ---> type str
	"""
	if typeCbs != "B" : 
		indiceType=nomdB[0:2]
	else :
		indiceType="00"
	return indiceType

#fonction qui récupère la géométrie des fichiers Isophones 
def RecuperationGeometrie(urlDossierIsophone,valeursBordsIsophones,nomFichierIsophoneExt):
    """
    en entrée
        nom du fichier Isophone avec extension ---> type str
    en sortie
        liste des géométries ---> type ????
    """
    #considerer le fichierIsophone en tant que couche SIG
    coucheIsophone= QgsVectorLayer(urlDossierIsophone+os.sep+nomFichierIsophoneExt, "couche Isophone", "ogr") #j ouvre le fichier
    #initialisation des listes de stockage pour les attributs et la géomérie 
    listeAttributs=[]
    listeGeometries=[]
    #création liste avec le bon nb d'isophones
    for i in range(len(valeursBordsIsophones)): 
        listeAttributs.append([])
        listeGeometries.append([])
    #Detection de la colonne 
    numChamps=OutilDetectionNomChampsAttributaires(coucheIsophone,ListeChampsImpose)[1]
    #ouverture de la barre de progression 
    progression=interfaceUtilisateur.ProgressBar()
    compteurTotal=coucheIsophone.featureCount()
    progression.InitialiserBarreProgressionLocale(compteurTotal, u'Récupération des géométries' + '\n' + u'étape 2 / 5 du traitement')
    compteur=0
    # pour chaque entite de la couche
    for objetIsophone in coucheIsophone.getFeatures() : 
    
        #vérification si l'utilisateur n'as pas demandé l'arret du traitement
        if interfaceUtilisateur.ProgressBar.drapeauArretFonctionEnCours==True:
            return 1
                    
        #Recherche la colonne des valeurs pour les CBS2012         
        if isinstance(objetIsophone[numChamps], basestring):
            Iso=int(objetIsophone[numChamps][-2:]) #prend le dB
        else:
            Iso=objetIsophone[numChamps]
        Nb=OutilRechercherValeursdBIsophones(Iso,valeursBordsIsophones) #identifie dans quelle case on met l'objet        
        if Nb>=0: # 
            listeAttributs[Nb].append(objetIsophone) # ajoute le numéro de l'objet dans la bonne case isophone
        else:
            print "Probleme de correspondance entre l'objet isophone et l'attribut : " + str(objetIsophone[numChamps])
        interfaceUtilisateur.ProgressBar.progressBarLocale.setValue(compteur)
        QCoreApplication.processEvents()
        compteur=compteur+1
    progression.close()
    # transforme en liste de polygones
    try :
        for i in range(len(listeAttributs)): 
            for j in range(len(listeAttributs[i])): 
                if listeAttributs[i][j].geometry().isMultipart():
                    multiGeometries = listeAttributs[i][j].geometry().buffer(0,0).asMultiPolygon()
                    for k in range(len(multiGeometries)):
                        listeGeometries[i].append(QgsGeometry().fromPolygon(multiGeometries[k]))
                else:
                    listeGeometries[i].append(listeAttributs[i][j].geometry().buffer(0,0))
    except:
       print 'pb geom'
    return listeGeometries

#Récupération du type de la ligne ferrovoiaire (LGV ou CONV) par une recherche dans le fichier "tableCorrespondanceFer.csv" à partir du codInfra et du codeDept
def RecuperationIdentifiants(codInfra,codeDept,urlCorrespondanceSIG):
    """
    en entrée
        codInfra au format Géostandard ---> type str
        codDept au format Géostandard ---> type str
    en sortie
        gestionnaire ---> type str
        uueid ---> type str
        nationalRoadName ---> type str
        typeLigne (LGV ou CONV) ---> type str
    """
    gestionnaire,uueid,nationalRoadName,typeLigne='','','',''     
    if codInfra[0] in ["0","1","2","3","4","5","6","7","8","9"]:
        urlfichier=urlTableCorrespondanceFer      
    else :
        urlfichier=urlCorrespondanceSIG
        #type de la ligne de fer si typeSource = F (LGV ou CONV)         
        typeLigne='NonConcerneMaisNecessaireCarUneSeuleFonctionTraitementGeometrie'
    #creer une matrice
    tableCorrespondance=OuvreCSV(urlfichier)#list(lectureCsv) # renvoie une valeur de la matrice : tableCorrespondance[Numéro ligne][Numéro colonne]    
    #recuperation colonne
    nbCodInfra2017=OutilRechercheNomDansListe('codinfra',tableCorrespondance[0])
    nbCodDept=OutilRechercheNomDansListe ('departement',tableCorrespondance[0])
    nbColoneNomSIG=tableCorrespondance[0].index('Nom fichier SIG sans _LDA')   
    nbUueid=OutilRechercheNomDansListe('uueid',tableCorrespondance[0])
    nbNationalRoadName=OutilRechercheNomDansListe('nationalRoadName',tableCorrespondance[0])
    nbGestionnaire=OutilRechercheNomDansListe('gestionnaire',tableCorrespondance[0])
    #balayage du fichier
    for ligne in range(len(tableCorrespondance)):
        if (tableCorrespondance[ligne][nbCodDept]==codeDept and tableCorrespondance[ligne][nbCodInfra2017] in [codInfra,RecuperationCodInfra(codInfra)] ) or tableCorrespondance[ligne][nbColoneNomSIG]==codeDept+'_'+codInfra or tableCorrespondance[ligne][nbColoneNomSIG]==codeDept+'_'+RecuperationCodInfra(codInfra) :
            codInfra=tableCorrespondance[ligne][nbCodInfra2017]
            uueid=tableCorrespondance[ligne][nbUueid]
            nationalRoadName=tableCorrespondance[ligne][nbNationalRoadName]
            gestionnaire=tableCorrespondance[ligne][nbGestionnaire]
            if codInfra[0] in ["0","1","2","3","4","5","6","7","8","9"]:
                #type de la ligne de fer si typeSource = F (LGV ou CONV)
                typeLigne=tableCorrespondance[ligne][tableCorrespondance[0].index('typeLigneFer')]
            return codInfra,gestionnaire,uueid,nationalRoadName,typeLigne
    return codInfra,gestionnaire,uueid,nationalRoadName,typeLigne

#Récupération du code infra 2017 en allant chercher dans le fichier "TableCorrespondanceNomSIG.csv"
def RecuperationCodeInfra2017(codInfra,codeDept,urlCorrespondance) : 
    """
    en entrée
        codInfra ---> type str
        codeDept ---> type str
        urlCorrespondance (fichier tableCorrespondanceNomSIG.csv dans dossier "ressources") ---> type str
    en sortie 
        codInfra version 2017 ---> type str
    """
    if len(urlCorrespondance)>0:
        # creer une matrice               
        tableCorrespondance=OuvreCSV(urlCorrespondance)#list(lectureCsv) # renvoie une valeur de la matrice : tableCorrespondance[Numéro ligne][Numéro colonne]
        nbColoneNomSIG=OutilRechercheNomDansListe('Nom fichier SIG sans _LDA',tableCorrespondance[0])
        for ligne in range(1,len(tableCorrespondance)):
            if tableCorrespondance[ligne][nbColoneNomSIG]==codeDept+'_'+codInfra:
                nbColone2017=OutilRechercheNomDansListe('Nom fichier SIG 2017',tableCorrespondance[0])
                return tableCorrespondance[ligne][nbColone2017]
    return codInfra

#Recuperation de tous les identifiants pour les voies nouvelles (recherche dans le fichier "TableVoiesNouvelles.csv" indiqué par l'utilisateur)
def RecuperationVoieNouvelle(codeDept,codInfra,urlVoiesNouvelles):
    """
    en entrée
        codInfra ---> type str
        codeDept ---> type str
        urlVoiesNouvelles  (fichier tablesVoiesNouvelles.csv indiqué par l'utilisateur)---> type str
    en sortie 
        codInfra ---> type str
        gestionnaire ---> type str
        uueid ---> type str
        nationalRoadName ---> type str
        typeLigne ---> type str
        autComCbs ---> type str
        autComPpbe ---> type str
    """
    #Si l'infra est une voie nouvelle non rapporté
    tableCorrespondance=OuvreCSV(urlVoiesNouvelles)
    #recuperation colonne
    nbColoneNomSIG=OutilRechercheNomDansListe('Nom fichier SIG sans _LDA',tableCorrespondance[0])
    #balayage du fichier
    for ligne in range(len(tableCorrespondance)):
        if tableCorrespondance[ligne][nbColoneNomSIG] in [codeDept+'_'+codInfra, codeDept+'_'+RecuperationCodInfra(codInfra)]:
            #recuperation colonne
            nbCodInfra=OutilRechercheNomDansListe('Code infrastructure',tableCorrespondance[0])
            nbGestionnaire=OutilRechercheNomDansListe('gestionnaire',tableCorrespondance[0])
            nbTypeLigne=OutilRechercheNomDansListe('Type ligne si Fer',tableCorrespondance[0])
            nbSIRENCBS=OutilRechercheNomDansListe('Num SIREN CBS',tableCorrespondance[0])
            nbSIRENPPBE=OutilRechercheNomDansListe('Num SIREN PPBE',tableCorrespondance[0])
            gestionnaire=tableCorrespondance[ligne][nbGestionnaire]
            codInfra= tableCorrespondance[ligne][nbCodInfra]
            uueid=''
            nationalRoadName= codeDept +'_' +codInfra
            typeLigne=tableCorrespondance[ligne][nbTypeLigne]
            autComCbs=tableCorrespondance[ligne][nbSIRENCBS]
            autComPpbe=tableCorrespondance[ligne][nbSIRENPPBE]
            return codInfra,gestionnaire,uueid,nationalRoadName,typeLigne, autComCbs,autComPpbe
    return codInfra,gestionnaire,uueid,nationalRoadName,typeLigne, autComCbs,autComPpbe

#Récupération 
def RecuperationListeNomFichierCorrespondance(urlCorrespondanceSIG,urlVoiesNouvelles):
    """
    en entrée
        urlCorrespondanceSIG = = par défaut fichier "TableCorrepondanceNomSIG.csv" dans dossier "ressources" sinon celui indiqué par l'utilisateur dans l'interface ---> type str
        urlVoiesNouvelles = par défaut vide sinon celui indiqué par l'utilisateur dans l'interface ---> type str
    en sortie
        listeNomFichierCorrespondance ---> type Liste de str avec DDD_codeInfra
        listeGestionnaire ---> type Liste de str avec le gestionnaire
    """
    listeNomFichierCorrespondance = []
    listeGestionnaire = []
    for urlfichier in [urlTableCorrespondanceFer,urlCorrespondanceSIG]:
        if len(urlfichier)>0:
            try:
                tableCorrespondance=OuvreCSV(urlfichier)
                nbColoneNomSIG=tableCorrespondance[0].index('Nom fichier SIG sans _LDA')
                nbColoneDep=tableCorrespondance[0].index('departement')
                nbColoneInfra=tableCorrespondance[0].index('codinfra')
                nbColoneGestionnaire=tableCorrespondance[0].index('gestionnaire')
                for ligne in range(1,len(tableCorrespondance)):
                    if tableCorrespondance[ligne][nbColoneNomSIG]==str(tableCorrespondance[ligne][nbColoneDep])+'_'+str(tableCorrespondance[ligne][nbColoneInfra]):
                        listeNomFichierCorrespondance.append(tableCorrespondance[ligne][nbColoneNomSIG])
                        listeGestionnaire.append(tableCorrespondance[ligne][nbColoneGestionnaire])
                    else:                        
                        if len(tableCorrespondance[ligne][nbColoneNomSIG])>0:
                            listeNomFichierCorrespondance.append(tableCorrespondance[ligne][nbColoneNomSIG])
                            listeGestionnaire.append(tableCorrespondance[ligne][nbColoneGestionnaire])
                        listeNomFichierCorrespondance.append(tableCorrespondance[ligne][nbColoneDep]+'_'+tableCorrespondance[ligne][nbColoneInfra])
                        listeGestionnaire.append(tableCorrespondance[ligne][nbColoneGestionnaire])
            except:
                instanceInterfaceUtilisateur=interfaceUtilisateur.MethodesPartagees()
                instanceInterfaceUtilisateur.MessageFinTraitement(5,'',u'Création simultanée N_BRUIT_ZBR et N_BRUIT_CBS',u"Mizogeo ne peut pas charger le fichier de correspondance ",'')
    for urlfichier in [urlVoiesNouvelles]:
        if len(urlfichier)>0:
            try:
                tableCorrespondance=OuvreCSV(urlfichier) # renvoie une valeur de la matrice : tableCorrespondance[Numéro ligne][Numéro colonne]
                #recherche si les colonnes existes pour après
                nbCodInfra=OutilRechercheNomDansListe('Code infrastructure',tableCorrespondance[0])
                nbGestionnaire=OutilRechercheNomDansListe('gestionnaire',tableCorrespondance[0])
                nbTypeLigne=OutilRechercheNomDansListe('Type ligne si Fer',tableCorrespondance[0])
                nbSIRENCBS=OutilRechercheNomDansListe('Num SIREN CBS',tableCorrespondance[0])
                nbSIRENPPBE=OutilRechercheNomDansListe('Num SIREN PPBE',tableCorrespondance[0])
                nbColoneInfra=OutilRechercheNomDansListe('Nom fichier SIG sans _LDA',tableCorrespondance[0])
                if -1 in [nbCodInfra,nbGestionnaire,nbTypeLigne,nbSIRENCBS,nbSIRENPPBE,nbColoneInfra]:
                    raise ValueError
                for ligne in range(1,len(tableCorrespondance)):
                    if len(tableCorrespondance[ligne][nbColoneInfra])>0:
                        listeNomFichierCorrespondance.append(tableCorrespondance[ligne][nbColoneInfra])
                        listeGestionnaire.append(tableCorrespondance[ligne][nbGestionnaire])
            except:
                instanceInterfaceUtilisateur=interfaceUtilisateur.MethodesPartagees()
                instanceInterfaceUtilisateur.MessageFinTraitement(5,'',u'Création simultanée N_BRUIT_ZBR et N_BRUIT_CBS',u"Mizogeo ne peut pas charger le fichier de correspondance ",'')
    return listeNomFichierCorrespondance,listeGestionnaire
 
#Récupération des données issues du fichier "donneesComplementaires.csv" à  partir du codeDept
def RecuperationAutoritesCompetentes(urlDonneesComplementaires,codeDept,gestionnaire) : 
    """
    en entrée
        urlDonneesComplementaires incluse dans le dossier "ressources" ---> type str
        codeDept au foramt Géostandard ---> type str
        gestionnaire ---> type str
    en sortie
        autComPpbe ---> type str
        autComCbs ---> type str
    """
    donneesComplementaires=OuvreCSV(urlDonneesComplementaires) # renvoie une valeur de la matrice : tab[Numéro ligne][Numéro colonne]
    autComCbs, autComPpbe= "",""
    #détermine le nombre de ligne
    nbLignes=len(donneesComplementaires)
    try :
        codeDept=str(int(codeDept))
    except:
        codeDept=codeDept
    # boucle qui balaye toutes les lignes de la tableCorrespondance.csv
    for ligne in range(nbLignes):
        #recherche de autComCbs en se basant sur le code département et  la nature de l'autorité (pour les grandes infras autComCbs= préfecture de département)
        if donneesComplementaires[ligne][3]==codeDept :
            if donneesComplementaires[ligne][5]=="Prefecture" :
                autComCbs=donneesComplementaires[ligne][0]
            #recherche de autComPpbe
            #si réseau non concédé alors autComPpbe = préfecture de département =autComCbs
            if gestionnaire in ["Etat_nonconcede","Etat_concede","SNCF-Reseau"] and donneesComplementaires[ligne][5]=="Prefecture"  :
                autComPpbe=donneesComplementaires[ligne][0]
            #si réseau non concédé alors autComPpbe = numéro Siren du département ou de la commune
            #quand "Departement" est trouvé dans la colonne n°3 (nature) alors on récupère le autComPpbe en colonne n°0 (numéro Siren)
            elif gestionnaire =="Conseil_Departemental" and donneesComplementaires[ligne][5]=="Departement" :
                autComPpbe=donneesComplementaires[ligne][0]
            #quand le nom de la commune gestionnaire est trouvé dans la colonne n°1 alors on récupère le autComPpbe en colonne n°0 (numéro Siren)
            elif gestionnaire.upper()==donneesComplementaires[ligne][1].replace(" ","-") and donneesComplementaires[ligne][5]=="Commune":
                autComPpbe=donneesComplementaires[ligne][0]
            #si réseau géré par Metropole alors on cherche 
            elif gestionnaire == "Metropole" and donneesComplementaires[ligne][5]=="Metropole" :
                autComPpbe=donneesComplementaires[ligne][0]
    if autComPpbe=="":
        print "autComPpbe pas trouve"
    return (autComCbs, autComPpbe)
    
#Récupération du fichier style selon le type de carte
def RecuperationFichierStyle(nomdB) :
    """
    en entrée
        nomdB ---> type str
    en sortie
        urlFichierStyle inclus dans le dossier "ressources" ---> type str
    """
    if nomdB=="LDA": 
        urlFichierStyle=urlFichierStyleLDA
    if nomdB=="LNA":
        urlFichierStyle=urlFichierStyleLNA
    if nomdB=="LNU" : 
        urlFichierStyle=urlFichierStyleB
    if nomdB=="LDC" : 
        urlFichierStyle=urlFichierStyleLDC
    if nomdB=="LNC" : 
        urlFichierStyle=urlFichierStyleLNC
    if nomdB=="LDD" or nomdB=="LND" : 
        urlFichierStyle=urlFichierStyleD
    return urlFichierStyle
 
#Récupération du contour de département 
def RecuperationContourDepartement(codeDepartement,urlContoursDepartements):
    """
    en entrée
        codeDepartement ---> type str
        urlContoursDepartements ---> type str
    en sortie
        coucheDept ---> type couche ogr
        selectFeat ---> type ???
    """
    coucheDept=QgsVectorLayer(urlContoursDepartements, "coucheDept", "ogr")
    requete=u' codeDept' + "=" + u"'"+str(codeDepartement)+u"'"
    filtre=QgsFeatureRequest(QgsExpression(requete))
    deptSelect=coucheDept.getFeatures(filtre)
    idDeptSelect = [i.id() for i in deptSelect]
    coucheDept.setSelectedFeatures(idDeptSelect)
    selectFeat=coucheDept.selectedFeatures()
    return coucheDept,selectFeat