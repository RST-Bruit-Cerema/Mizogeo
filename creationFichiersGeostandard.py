# -*- coding: utf-8 -*-
"""
fichier regroupant toutes les fonctions de créations des fichiers au format GéoStandard
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QMessageBox
import interfaceUtilisateur
#from interfaceUtilisateur import ProgressBar, MethodesPartagees
from qgis.core import *
import qgis.utils
import shutil
from outilsFonctions import OutilListingFichiers,OutilDecoupageNomFichier
from recuperationDonnees import RecuperationNatureFichier,RecuperationTypeCBS, RecuperationTypeSource,RecuperationIndiceType
from recuperationDonnees import RecuperationIdentifiants, RecuperationAutoritesCompetentes, RecuperationCodInfra,RecuperationVoieNouvelle
from recuperationDonnees import RecuperationFichierStyle
#from recuperationDonnees import RecuperationGeometrie
from recuperationDonnees import RecuperationContourDepartement
from verificationDonnees import VerificationCompleteIsophone, VerificationFichiersAAssembler, VerificationFichiersAAgreger
from parametres import urlTableCorrespondanceFer,urlDonneesComplementaires, UrlFichierSigLimiteAdministrative
from parametres import typeTerr, anneeCbsZbr, champsAttributairesZBR,champsAttributairesCBS,champsAttributairesPPBE, encodage, driverExport, typeGeometrie, anneePpbe
from parametresFonctions import URLDEPARTEMENT, URLRESUMECBS, URLRESUMEPPBE, URLGEOSTANDARDCBS, URLGEOSTANDARDPPBE, URLGEOSTANDARDCBSMETA,URLGEOSTANDARDPPBEMETA, URLGESTIONNAIRE, URLCODINFRA, URLTYPECARTE
from parametresFonctions import NOMGEOSTANDARDZBR, NOMGEOSTANDARDCBS, NOMGEOSTANDARDQML, NOMGEOSTANDARDPPBE,NOMASSEMBLZBR,NOMASSEMBLCBS, NOMAGREGZBR,NOMAGREGQML
from parametresFonctions import ValeursBordsIsophones,ArborescenceDossiersGeostandardCbs,ArborescenceDossiersGeostandardPpbe,CreationArborescenceDossiersGeostandard,ValeursAttributairesZBR, ValeursAttributairesCBS, ValeursAttributairesPPBE
from traitementsFichiers import DecoupageIsophonesPardB,RegroupementIsophonePardB,TraitementGeometrieIsophones, TransformeEnListeGeomSimple
import os.path
import win32api

####fonction de création du fichier N_BRUIT_ZBR_INFRA_S_ddd.shp
def CreationZbrCbs(urlDossierIsophone,urlCorrespondanceSIG,urlSortie,urlVoiesNouvelles,producteur):
    """
    en entrée 
        urlDossierIsophone = chemin du dossier contenant les fichiers à mettre au GéoStandard ---> type str
        urlCorrespondanceSIG = par défaut fichier "TableCorrepondanceNomSIG.csv" dans dossier "ressources" sinon celui indiqué par l'utilisateur dans l'interface ---> type str
        urlSortie = chemin du dossier contenant les fichiers créés par Mizogeo ---> type str
        urlVoiesNouvelles = par défaut vide sinon celui indiqué par l'utilisateur dans l'interface ---> type str
        producteur = numéro Siren (par défaut celui du Cerema sinon celui indiqué dans l'interface) ---> type str
    en sortie 
        arborescence dossiers préconisée en interne Cerema (si nouvelle voie, dossier "Nouvelles_voies")
        fichiers GéoStandard N_BRUIT_ZBR (shp + dbf + shx + prj) avec fichier style associé conforme à la NF S 31-110 (.qml)
        fichiers GéoStandard N_BRUIT_CBS (dbf)
    """
    # ouverture d'une instance de la classe ProgressBar 
    instanceProgression=interfaceUtilisateur.ProgressBar()
    # afficher la fenetre de progression
    instanceProgression.fenetreProgression.show()
    QCoreApplication.processEvents()     
    listeNomFichierAvecExtension,nbFichiers=OutilListingFichiers(urlDossierIsophone)
    #Initialisation du dictionnaire des fichiers CBS a creer
    dicoListeFichierCbs={}
    #============================================================================================
    #vérification du nommage des fichiers isophones et de la structure du fichier 
    #============================================================================================
    #balayage de tous les fichiers dans listeFichierIsophone, si erreur création du fichier erreursFichiersIsophones.csv
    verifFichier=VerificationCompleteIsophone(urlDossierIsophone,listeNomFichierAvecExtension,urlSortie,urlCorrespondanceSIG,urlVoiesNouvelles)
    #si aucune anomalie, balayage des fichiers à traiter pour créer les fichiers GéoStandard
    if verifFichier==False :
        instanceProgression.fenetreProgression.close()
        instanceProgression.Reset()
        instanceProgression.close()
        del instanceProgression
        return 1
    else :    
        for i in range(len(listeNomFichierAvecExtension)) :
            #vérification si l'utilisateur n'as pas demandé l'arret du traitement
            if instanceProgression.drapeauArretFonctionEnCours==True:
                instanceProgression.fenetreProgression.close()
                instanceProgression.Reset()
                instanceProgression.close()
                del instanceProgression
                return 2
            nomFichierIsophoneAvecExt=listeNomFichierAvecExtension[i]
              
            instanceProgression.labelCoucheATraiter.setText(u'Nombre de fichiers traités :'+ 
                '\n'+ str(i+1)+' / '+ str(nbFichiers) +
                '\n' +
                '\n'+
                "Fichier en cours de traitement :" +
                '\n'+
                nomFichierIsophoneAvecExt[:-4])
            #============================================================================================
            #recuperation des variables propres à chaque fichier à partir du nom du fichier
            #============================================================================================
            #code département pour CBS2012 ou CBSMsig
            #code infra
            #nomdB (LDA, LNA, etc)
            codeDept,codInfra,nomdB=OutilDecoupageNomFichier(nomFichierIsophoneAvecExt[:-4])
            #type de la carte "A, B, C ou D" pour CBS2012 ou CBSMsig
            typeCbs=RecuperationTypeCBS(nomFichierIsophoneAvecExt[:-4])
            #récupération du typeSource au format GéoStandard (R ou F)
            typeSource=RecuperationTypeSource(codInfra)
            #récupération de l'indiceType au format GéoStandard (LD, LN ou 00 si type B)
            indiceType=RecuperationIndiceType(nomdB,typeCbs)           
            #récupération des données issues de tableCorrespondanceSIG et fer
            codInfra,gestionnaire,uueid,nationalRoadName,typeLigne=RecuperationIdentifiants(codInfra,codeDept,urlCorrespondanceSIG)            
            if uueid<>'':
                #récupération des données issues de DonneesComplementaires.csv
                autComCbs,autComPpbe=RecuperationAutoritesCompetentes(urlDonneesComplementaires,codeDept,gestionnaire)
            else :
                # on balaye fichier si voie nouvelle
                if len(urlVoiesNouvelles)>0:
                    codInfra,gestionnaire,uueid,nationalRoadName,typeLigne,autComCbs,autComPpbe=RecuperationVoieNouvelle(codeDept,codInfra,urlVoiesNouvelles)                       
                #sinon
                else:
                    print u'problème de voie = voie pas trouvée'
            #=============================================================================================
            #dossiers de stockages des fichiers N_BRUIT_ZBR_INFRA_S_ddd et N_BRUIT_CBS_INFRA_ddd
            #=============================================================================================
            #vérification si l'utilisateur n'as pas demandé l'arret du traitement
            if instanceProgression.drapeauArretFonctionEnCours==True:
                instanceProgression.fenetreProgression.close()
                instanceProgression.Reset()
                instanceProgression.close()
                del instanceProgression
                return 2
            #verification gestionnaire
            if gestionnaire=='':
                break
            #utilisation d'un nom court pour eviter pb dépassement des 255 caractères
            urlSortie=win32api.GetShortPathName(urlSortie)
            [dossierZbr,dossierCbs]=CreationArborescenceDossiersGeostandard(uueid,urlSortie,gestionnaire,typeSource,typeCbs,codeDept, autComCbs,codInfra)[:2]
            dossierZbr=win32api.GetShortPathName(dossierZbr)
            dossierCbs=win32api.GetShortPathName(dossierCbs)
            #=============================================================================================
            #mise au GéoStandard des isophones sur la partie géométrique
            #=============================================================================================
            #vérification si l'utilisateur n'as pas demandé l'arret du traitement
            if instanceProgression.drapeauArretFonctionEnCours==True:
                instanceProgression.fenetreProgression.close()
                instanceProgression.Reset()
                instanceProgression.close()
                del instanceProgression
                return 2   
            urlSigLimiteAdministrative,srid=UrlFichierSigLimiteAdministrative(codeDept)
            listeGeometriesFormatGeostandard,valeursBordsIsophones=TraitementGeometrieIsophones(urlDossierIsophone,nomdB,typeLigne,typeSource,nomFichierIsophoneAvecExt,urlSigLimiteAdministrative)
            #vérification si l'utilisateur n'as pas demandé l'arret du traitement
            if listeGeometriesFormatGeostandard==1 and valeursBordsIsophones==1 :
                instanceProgression.fenetreProgression.close()
                instanceProgression.Reset()
                instanceProgression.close()
                del instanceProgression
                return 2
            #============================================================================================
            #création de la couche N_BRUIT_ZBR_INFRA_S_ddd
            #=============================================================================================
            #vérification si l'utilisateur n'as pas demandé l'arret du traitement
            if instanceProgression.drapeauArretFonctionEnCours==True:
                instanceProgression.fenetreProgression.close()
                instanceProgression.Reset()
                instanceProgression.close()
                del instanceProgression
                return 2
            #détermination du nom du shapile à créer 
            nomGeostandardZbr=NOMGEOSTANDARDZBR%(typeTerr,typeSource,codInfra,typeCbs,indiceType,codeDept)
            #détermination de la liste des valeurs attributaires
            if typeSource=="R" :
                valeursAttributairesZBRRoute=ValeursAttributairesZBR(anneeCbsZbr,autComCbs,codInfra,codeDept,uueid,typeTerr,producteur,typeLigne)[0]
                valeursAttributairesZbr=valeursAttributairesZBRRoute.get(nomdB)
                valeursAttributairesCBSRoute=ValeursAttributairesCBS(anneeCbsZbr,autComCbs,codInfra,codeDept,uueid,typeTerr,producteur,nationalRoadName,autComPpbe)[0]
                listeAttributairesCbs=valeursAttributairesCBSRoute.get(nomdB)
                if not dossierCbs in dicoListeFichierCbs: #crée un dico avec les références par infra
                    dicoListeFichierCbs[dossierCbs]=[listeAttributairesCbs]#si la clé relative à l'infra n'existe pas on crée la clé et on y associe une valeur
                else:
                    dicoListeFichierCbs[dossierCbs].append(listeAttributairesCbs) #sinon on ajoute une valeur (liste) à celles existantes
            if typeSource=="F"  and typeLigne=="LGV": 
                valeursAttributairesZBRFerLgv=ValeursAttributairesZBR(anneeCbsZbr,autComCbs,codInfra,codeDept,uueid,typeTerr,producteur,typeLigne)[1]
                valeursAttributairesZbr=valeursAttributairesZBRFerLgv.get(nomdB)
                valeursAttributairesCBSFer=ValeursAttributairesCBS(anneeCbsZbr,autComCbs,codInfra,codeDept,uueid,typeTerr,producteur,nationalRoadName,autComPpbe)[1]
                listeAttributairesCbs=valeursAttributairesCBSFer.get(nomdB)
                if not dossierCbs in dicoListeFichierCbs: #crée un dico avec les références par infra
                    dicoListeFichierCbs[dossierCbs]=[listeAttributairesCbs]#si la clé relative à l'infra n'existe pas on crée la clé et on y associe une valeur
                else:
                    dicoListeFichierCbs[dossierCbs].append(listeAttributairesCbs)
            if typeSource=="F"  and typeLigne=="CONV": 
                valeursAttributairesZBRFerConv=ValeursAttributairesZBR(anneeCbsZbr,autComCbs,codInfra,codeDept,uueid,typeTerr,producteur,typeLigne)[2]
                valeursAttributairesZbr=valeursAttributairesZBRFerConv.get(nomdB)
                valeursAttributairesCBSFer=ValeursAttributairesCBS(anneeCbsZbr,autComCbs,codInfra,codeDept,uueid,typeTerr,producteur,nationalRoadName,autComPpbe)[1]
                listeAttributairesCbs=valeursAttributairesCBSFer.get(nomdB)
                if not dossierCbs in dicoListeFichierCbs: #crée un dico avec les références par infra
                    dicoListeFichierCbs[dossierCbs]=[listeAttributairesCbs]#si la clé relative à l'infra n'existe pas on crée la clé et on y associe une valeur
                else:
                    dicoListeFichierCbs[dossierCbs].append(listeAttributairesCbs) #sinon on ajoute une valeur (liste) à celles existantes 
            #vérification si l'utilisateur n'as pas demandé l'arret du traitement
            if instanceProgression.drapeauArretFonctionEnCours==True:
                instanceProgression.fenetreProgression.close()
                instanceProgression.Reset()
                instanceProgression.close()
                del instanceProgression
                return 2
            #création du fichier shapefile
            ecritureCoucheZbr = QgsVectorFileWriter(dossierZbr+os.sep+nomGeostandardZbr,encodage,champsAttributairesZBR,typeGeometrie,srid,driverExport)#QgsVectorFileWriter(dossierZbr+os.sep+nomGeostandardZbr, systCoord, champsAttributairesZBR, QGis.WKBPolygon, None, "ESRI Shapefile")
            #ajout d'entités dans la couche 
            entiteZbr= QgsFeature()
            if nomdB[-1] == 'D':
                valeursBordsIsophones=[['-8',-8],['-5',-5],['-2',-2],['+0',2],['+2',5],['+5',8],['+8',1000]]
            for i in range(len(listeGeometriesFormatGeostandard)):
                if listeGeometriesFormatGeostandard[i].area() >0:
                    entiteZbr.setGeometry(listeGeometriesFormatGeostandard[i])
                    #changer IDZONEBRUIT
                    valeursAttributairesZbr[0]=valeursAttributairesZbr[0][:-2]+str(valeursBordsIsophones[i][0])
                    valeursAttributairesZbr[11]=str(valeursBordsIsophones[i][0])
                    entiteZbr.setAttributes(valeursAttributairesZbr)
                    ecritureCoucheZbr.addFeature(entiteZbr)
            # delete the writer to flush features to disk
            del ecritureCoucheZbr
            os.remove(dossierZbr+os.sep+nomGeostandardZbr[:-4]+".qpj")   
            #============================================================================================
            #création du fichier style assoocée à la couche N_BRUIT_ZBR_INFRA_ddd
            #=============================================================================================
            #récupération de l'emplacement du fichier style associée à la couche 
            urlFichierStyle=RecuperationFichierStyle(nomdB)
            #déterminationr de l'emplacement de stockage du fichier style incluant le nom du fichier style (renommage comme le fichier N_BRUITZBR
            nomGeostandardQml=NOMGEOSTANDARDQML%(typeTerr,typeSource,codInfra,typeCbs,indiceType,codeDept)
            urlGeostandardQml=dossierZbr+os.sep+nomGeostandardQml
            #copie du fichier style initial stocké dans dossier 'ressources' de Mizogeo pour le mettre dans le dossier Zbr avec le même nom que le fichier N_BRUIT_ZBR
            shutil.copyfile(urlFichierStyle, urlGeostandardQml) 
    #============================================================================================
    #création des fichiers N_BRUIT_CBS_INFRA_ddd
    #=============================================================================================
    #vérification si l'utilisateur n'as pas demandé l'arret du traitement
    if instanceProgression.drapeauArretFonctionEnCours==True:
        instanceProgression.fenetreProgression.close()
        instanceProgression.Reset()
        instanceProgression.close()
        del instanceProgression
        return 2
    entiteCbs= QgsFeature()#le conteneur des données est de type QgsFeature, uniqument si le fichier cbs n'existe pas
    for cleCodeInfra in dicoListeFichierCbs.keys(): #parcours des cles du dico
        listeDonneesCbs=dicoListeFichierCbs[cleCodeInfra] #extraction de l'ensemble des elements (listes) relatif à la cle
        cleCodeInfraLong=win32api.GetLongPathName(cleCodeInfra) #recupération du nom de fichier entier pour obtenir les noms de dept et codinfra ok
        departement=cleCodeInfraLong.split("Grandes_infrastructures_Millesime_") #on se sert de ces caractère pour recuperer le departement
        codeDepartement=departement[1][5:8]
        positionCodInfra=cleCodeInfraLong[::-1].find('\\',1)
        codInfra=cleCodeInfraLong[-positionCodInfra:]      
        nomGeostandardCbs=NOMGEOSTANDARDCBS%(typeTerr,codInfra,codeDepartement)+".dbf"
        fichierCbsDbf=os.path.join(cleCodeInfra,nomGeostandardCbs)#url complet du fichier Cbs format dbf
        nomFichierCbsShp=NOMGEOSTANDARDCBS%(typeTerr,codInfra,codeDepartement)+".shp"#selon la norme definie par le geostandard, pour pouvoir créer le fichier shp si le dbf n'existe pas
        fichierCbsShp=os.path.join(cleCodeInfra,nomFichierCbsShp)
        urlFichierCbs=fichierCbsDbf[:-4]#utile pour faire les suppression
        if os.path.isfile(fichierCbsDbf): # si le fichier existe deja
            fichierCbsExistant=QgsVectorLayer(fichierCbsDbf,u"fichierCbsDbfExistant","ogr")#on ouvre le fichier
            entiteCbsExistant=QgsFeature(fichierCbsExistant.pendingFields())#on definit le format des objets du fichier
            objetsfichierCbsExistant=fichierCbsExistant.getFeatures()#on récupere l'ensemble des objets pour pouvoir le parcourir
            for donneesCbs in listeDonneesCbs:#on parcours les liste de données relative à une clé du dico (c.a.d à une route)
                for objet in objetsfichierCbsExistant:#on parcours les objetys du transparent existant
                    if (objet[7]==donneesCbs[7] and objet[13]==donneesCbs[13] and objet[14]==donneesCbs[14]):#si on a un objet dans le transparent avec le mm nom de voie, type de carte et indice, on ne fait rien (ca veut dire que la carte etait deja faite)
                        break
                else:#ce else est associé au for mais depend du if : c'est une structure de controle un peu particuliere de python qui permet de parcourir l'ensemble de la boucle for des objets du fichier existant, et si la condition du if n'est pas remplie, alors on applique le else : on ajoute une ligne au fichier existant
                    entiteCbsExistant.setAttributes(donneesCbs)#on paramètres les attributs
                    fichierCbsExistant.dataProvider().addFeatures([entiteCbsExistant])#on les ajoutes
            del fichierCbsExistant
        else:#si le fichier n'existait pas
            ecritureCoucheCbs = QgsVectorFileWriter(fichierCbsShp,encodage,champsAttributairesCBS,typeGeometrie,None,driverExport)#on crée un fichier shp
            for donneesCbs in listeDonneesCbs: #on ajoute une ligne dans le shp pour chaque occurence dans le dico
                entiteCbs.setAttributes(donneesCbs)
                ecritureCoucheCbs.addFeature(entiteCbs)
            del ecritureCoucheCbs#on efface
            os.remove(urlFichierCbs+".cpg")#on supprime les fichiers inutiles
            os.remove(urlFichierCbs+".shp")
            os.remove(urlFichierCbs+".shx")
    #fermeture de la fenêtre de progression
    instanceProgression.fenetreProgression.close()
    instanceProgression.Reset()
    instanceProgression.close()
    del instanceProgression
    return 0
      
def CreationPPBEshp (departementATraiter,urlSortie,producteur) : 
    """
    en entrée
        departementATraiter = liste de code dépt (str) donné par l'utilisateur dans l'interface ---> type list
        urlSortie = chemin du dossier contenant les fichiers créés par Mizogeo ---> type str
        producteur = numéro Siren (par défaut celui du Cerema sinon celui indiqué dans l'interface) ---> type str
    en sortie
        fichiers GéoStandard N_BRUIT_PPBE (shp + dbf + shx + prj)
    """  
    #détermination du gestionnaire dans le cas des PPBE grandes infras Etat 
    gestionnaire = "Etat_nonconcede"
    #on fixe volontairement le typeCbs et le codInfra comme un caractère vide car pas besoin pour le fichier PPBE mais demandé dans la fonction Arboresence
    typeCbs=str("")
    codInfra=str("")
    # ouverture d'une instance de la classe ProgressBar 
    instanceProgression=interfaceUtilisateur.ProgressBar()
    # afficher la fenetre de progression
    instanceProgression.fenetreProgression.show()
    QCoreApplication.processEvents()     
    departementATraiter=departementATraiter.split(',')
    nbDepartement=len(departementATraiter)
    instanceProgression.labelCoucheATraiter.setText(u'Création des fichiers PPBE')
    #on boucle sur la liste des départements pour lesquels il faut créer le fichier N_BRUI_PPBE
    for i in range(len(departementATraiter)) :
        #vérification si l'utilisateur n'as pas demandé l'arret du traitement
        if instanceProgression.drapeauArretFonctionEnCours==True:
            instanceProgression.fenetreProgression.close()
            instanceProgression.Reset()
            instanceProgression.close()
            del instanceProgression
            return 2
        #informations pour l'affichage de la barre de progression
        codeDept=departementATraiter[i]
        instanceProgression.labelCoucheATraiter.setText(u'Nombre de départements traités :'+ 
                '\n'+ str(i+1)+' / '+ str(nbDepartement) +
                '\n')
        instanceProgression.InitialiserBarreProgressionLocale(nbDepartement, u'Département en cours de traitement : '+ '\n' + codeDept)
        instanceProgression.progressBarLocale.setValue(i) #incrementation de la barre de Progression
        urlFichierSigLimiteAdministrative= UrlFichierSigLimiteAdministrative(codeDept)
        #=============================================================================================
        #récupération du numéro Siren de l'autorité compétente PPBE
        #=============================================================================================
        autComCbs,autComPpbe=RecuperationAutoritesCompetentes(urlDonneesComplementaires,codeDept,gestionnaire)
        #=============================================================================================
        #dossier de stockage du fichier N_BRUIT_ZBR_PPBE
        #=============================================================================================
        listeUrlPpbe=ArborescenceDossiersGeostandardPpbe(urlSortie,codeDept)
        for url in listeUrlPpbe : 
            if not os.path.exists(url) :
                os.makedirs(url)
        dossierPpbe=listeUrlPpbe[3]
        #============================================================================================
        #récupération géométrie des contours départements
        #=============================================================================================
        #définition de l'url du fichier départements intégrés dans le dossier "ressources" en fonction du code département
        urlFichierSigLimiteAdministrative=UrlFichierSigLimiteAdministrative(codeDept)[0]
        #définition du système de projection en fonction du code département
        srid=UrlFichierSigLimiteAdministrative(codeDept)[1]
        #récupération de la géométrie du département
        coucheDept,selectFeat=RecuperationContourDepartement(codeDept,urlFichierSigLimiteAdministrative)
        #============================================================================================
        #création de la couche N_BRUIT_PPBE
        #=============================================================================================
        #création pour la route
        #==========
        #vérification si l'utilisateur n'as pas demandé l'arret du traitement
        if instanceProgression.drapeauArretFonctionEnCours==True:
            instanceProgression.fenetreProgression.close()
            instanceProgression.Reset()
            instanceProgression.close()
            del instanceProgression
            return 2  
        #détermination du nom du shapile à créer 
        nomGeostandardPpbe=NOMGEOSTANDARDPPBE%(typeTerr,codeDept)
        #détermination de la liste des valeurs attributaires
        valeursAttributairesPpbe=ValeursAttributairesPPBE(anneePpbe,codeDept,autComPpbe,typeTerr,producteur) 
        #dictionnaire reprenant le numéro du champs et la valeur attributaire associée
        coupleValNumChamps=dict(zip(range(len(valeursAttributairesPpbe)),valeursAttributairesPpbe))
        #création du fichier shapefile Route
        ecritureCouchePpbe=QgsVectorFileWriter.writeAsVectorFormat(coucheDept,dossierPpbe+os.sep+nomGeostandardPpbe, encodage,None,driverExport,1)
        couchePpbe=QgsVectorLayer(dossierPpbe+os.sep+nomGeostandardPpbe, "couche PPBE", "ogr")
        couchePpbe.startEditing() #autorise modifications des couches - active le crayon dans onglet couche
        ####à ajouter
        suppChamps = couchePpbe.dataProvider().deleteAttributes([0,1])
        #mise a jour des champs
        couchePpbe.updateFields()
        ajoutChamps= couchePpbe.dataProvider().addAttributes(champsAttributairesPPBE)
        couchePpbe.dataProvider().changeAttributeValues({0:coupleValNumChamps })
        #enregistrement des couches pour prendre en compte toutes les modifications
        couchePpbe.commitChanges()
        #incrémentation de la barre de progression
        instanceProgression.progressBarLocale.setValue(i+1)
        QCoreApplication.processEvents()
        # delete the writer to flush features to disk
        del ecritureCouchePpbe
        os.remove(dossierPpbe+os.sep+nomGeostandardPpbe[:-4]+".qpj")
    #fermeture de la barre de progression
    instanceProgression.fenetreProgression.close()
    instanceProgression.Reset()
    instanceProgression.close()
    del instanceProgression
    return 0
        
def CreationAssemblage(urlDbf, urlSortie):  
    """
    en entrée
        urlDbf = chemin du dossier contenant les fichiers à assembler par Mizogeo ---> type str
        urlSortie = chemin du dossier contenant les fichiers créés par Mizogeo ---> type str
    en sortie 
        fichier Assemblage (dbf) à la racine de l'urlSortie
    """  
    #récupération sous forme de liste des noms des fichiers à Assemblageténer - lien avec l'interface
    listeNomFichierAvecExtension,nbFichiers=OutilListingFichiers(urlDbf)
    # ouverture d'une instance de la classe ProgressBar 
    instanceProgression=interfaceUtilisateur.ProgressBar()
    # afficher la fenetre de progression
    instanceProgression.fenetreProgression.show()
    QCoreApplication.processEvents()     
    #============================================================================================
    #vérification du nommage et de la structure des fichiers dbf 
    #============================================================================================
    #balayage de tous les fichiers dans listeFichierIsophone, si erreur création du fichier listeErreursAssemblageageDBF.csv
    verifFichier=VerificationFichiersAAssembler(urlDbf,listeNomFichierAvecExtension,champsAttributairesZBR,champsAttributairesCBS,urlSortie)
    if verifFichier==False :
            instanceProgression.fenetreProgression.close()
            instanceProgression.Reset()
            instanceProgression.close()
            del instanceProgression
            return 1
    #============================================================================================
    #stockage des noms des fichiers dans deux listes distinctes - tous les CBS ensemble et tous les ZBR ensemble
    #============================================================================================
    #initialisation des listes de stokages
    listeFichiersCbs=[]
    listeFichiersZbr=[]
    #on parcourt la liste de fichiers dans le dossier sélectionné par l'utilisateur - lien avec interface
    for nomFichierAvecExt in listeNomFichierAvecExtension :            
        #pour chaque fichier
        if nomFichierAvecExt[0:11]=="N_BRUIT_ZBR" : 
            listeFichiersZbr.append(nomFichierAvecExt)
        if nomFichierAvecExt[0:11]=="N_BRUIT_CBS" : 
            listeFichiersCbs.append(nomFichierAvecExt)
    dicoListeFichierAssemblage=dict(zip(["ZBR","CBS"],[listeFichiersZbr,listeFichiersCbs]))
    #============================================================================================
    #Assemblage des N_BRUIT_CBS et N_BRUIT_ZBR
    #============================================================================================
    for typeFichier in ["ZBR","CBS"] :
        listeFichiersAssemblage=dicoListeFichierAssemblage.get(typeFichier)
        nbFichiers=len(listeFichiersAssemblage)
        if listeFichiersAssemblage==[] :
            print "liste vide" 
        else :
            #initialisation de la liste de stockage de tous les attributs de tous les fichiers à Assemblage
            listeAttrAssemblage=[]
            instanceProgression.InitialiserBarreProgressionLocale(nbFichiers, u"Récupération des tables attributaires pour les fichiers "+typeFichier)
            #pour tous les fichiers contenus dans la liste 
            for j in range(len(listeFichiersAssemblage)) :
                fichierAssemblage=listeFichiersAssemblage[j]
                #informations relatives à la progression du traitement
                instanceProgression.labelCoucheATraiter.setText(u'Nombre de fichiers '+ typeFichier +u' traités :'+ 
                '\n'+ str(j+1)+' / '+ str(nbFichiers) +
                '\n'+'\n'+'\n'+
                u'Fichier en cours de traitement : ' +
                '\n' + fichierAssemblage)
                #vérification si l'utilisateur n'as pas demandé l'arret du traitement
                if instanceProgression.drapeauArretFonctionEnCours==True:
                    instanceProgression.fenetreProgression.close()
                    instanceProgression.Reset()
                    instanceProgression.close()
                    del instanceProgression
                    return 2
                compteur=1
                #on considère le fichier dbf comme une couche SIG
                coucheDbf=QgsVectorLayer(urlDbf+os.sep+fichierAssemblage,fichierAssemblage[:-4], "ogr")
                #on récupère les attributs en les stockant dans la liste
                for i in coucheDbf.getFeatures():
                    #vérification si l'utilisateur n'as pas demandé l'arret du traitement
                    if instanceProgression.drapeauArretFonctionEnCours==True:
                        instanceProgression.fenetreProgression.close()
                        instanceProgression.Reset()
                        instanceProgression.close()
                        del instanceProgression
                        return 2
                    listeAttrAssemblage.append(i.attributes())
                    instanceProgression.progressBarLocale.setValue(compteur) #incrementation de la barre de Progression
                    QCoreApplication.processEvents()
                    compteur=compteur+1
            #définition du fichier final
            #par défaut, on fixe le système de projection 
            srid=QgsCoordinateReferenceSystem(2154)
            #détermination du nom du fichier dbf final 
            if typeFichier=="ZBR" : 
                nomFichierAssemblage=NOMASSEMBLZBR
                champsAttributairesAssemblage=champsAttributairesZBR
            if typeFichier=="CBS":
                nomFichierAssemblage=NOMASSEMBLCBS
                champsAttributairesAssemblage=champsAttributairesCBS
            #incrémentation de la barre de progression
            compteurTotal=len(listeAttrAssemblage)
            instanceProgression.InitialiserBarreProgressionLocale(compteurTotal, u"Assemblage de tous les fichiers "+typeFichier)
            compteur=1
            #on crée la couche SIG Assemblage puis on gardera uniquement le fichier dbf
            #écriture des fichiers 
            ecritureCoucheAssemblage = QgsVectorFileWriter(urlSortie+os.sep+nomFichierAssemblage,encodage,champsAttributairesAssemblage,typeGeometrie,srid,driverExport)
            entiteAssemblage= QgsFeature()
            for attrAssemblage in listeAttrAssemblage :
                #vérification si l'utilisateur n'as pas demandé l'arret du traitement
                if instanceProgression.drapeauArretFonctionEnCours==True:
                    instanceProgression.fenetreProgression.close()
                    instanceProgression.Reset()
                    instanceProgression.close()
                    del instanceProgression
                    return 2
                entiteAssemblage.setAttributes(attrAssemblage)
                ecritureCoucheAssemblage.addFeature(entiteAssemblage)
                instanceProgression.progressBarLocale.setValue(compteur) #incrementation de la barre de Progression
                QCoreApplication.processEvents()
                compteur=compteur+1 
            # delete the writer to flush features to disk
            del ecritureCoucheAssemblage              
            os.remove(urlSortie+os.sep+nomFichierAssemblage+".cpg")
            os.remove(urlSortie+os.sep+nomFichierAssemblage+ ".prj")
            os.remove(urlSortie+os.sep+nomFichierAssemblage+ ".qpj")
            os.remove(urlSortie+os.sep+nomFichierAssemblage+ ".shp")
            os.remove(urlSortie+os.sep+nomFichierAssemblage+".shx")
    #fermeture de la barre de progression
    instanceProgression.fenetreProgression.close()
    instanceProgression.Reset()
    instanceProgression.close()
    del instanceProgression
    return 0
        
    
def CreationAgregation(departementATraiter,urlPerimetre, urlZbr, urlSortie):
    """
    en entrée
        departementATraiter = code dept (str) donné par l'utilisateur dans l'interface ---> type str
        urlPerimetre = si dépt choisi dans liste (urlPerimetre = chemin des fichiers SIG dans dossier "ressources") sinon url indiqué par l'utilisateur dans l'interface ---> type str
        urlZbr = chemin du dossier contenant les fichiers à agréger par Mizogeo ---> type str
        urlSortie = chemin du dossier contenant les fichiers créés par Mizogeo ---> type str
    en sortie
        fichier Agregation par type de carte (shp+dbf+shx+prj) avec fichier style associé (qml) à la racine de l'urlSortie
    """
    #récupération sous forme de liste des noms des fichiers à agréger - lien avec l'interface (contenu du dossier urlZbr)
    listeNomFichierAvecExtension,nbFichiers=OutilListingFichiers(urlZbr)
    # ouverture d'une instance de la classe ProgressBar 
    instanceProgression=interfaceUtilisateur.ProgressBar()
    # afficher la fenetre de progression
    instanceProgression.fenetreProgression.show()
    QCoreApplication.processEvents()     
    #============================================================================================
    #vérification du nommage et de la structure des fichiers à agréger 
    #============================================================================================
    #balayage de tous les fichiers dans listeFichierIsophone, si erreur création du fichier listeErreursAssemblageageDBF.csv
    verifFichier=VerificationFichiersAAgreger(urlZbr,listeNomFichierAvecExtension,champsAttributairesZBR,urlSortie,departementATraiter,urlPerimetre)
    if verifFichier==False :
        instanceProgression.fenetreProgression.close()
        instanceProgression.Reset()
        instanceProgression.close()
        del instanceProgression
        return 1
    #============================================================================================
    #récupération géométrie du périmètre d'agrégation
    #============================================================================================
    #prise en compte du choix de l'utilisateur - échelle départementale ou autre
    if departementATraiter == '' :
        #on considère la couche "périmètre administratif" comme une couche SIG
        couchePerimetre=QgsVectorLayer(urlPerimetre, u"périmètre administratif choisi par utilisateur", "ogr")
        #on fixe le système de coordonnées
        srid=couchePerimetre.crs()
        #on récuère la géométrie du périmètre administratf 
        entitePerimetre=couchePerimetre.getFeatures().next()
        geomPerimetre= entitePerimetre.geometry()
    else :
        urlPerimetre,srid= UrlFichierSigLimiteAdministrative(departementATraiter)
        couchePerimetre,entitePerimetre=RecuperationContourDepartement(departementATraiter,urlPerimetre)
        for feat in entitePerimetre:
            geomPerimetre= feat.geometry() 
    #============================================================================================
    #sélection des isophones compris dans le périmètre administratif - intersection
    #============================================================================================
    #vérification si l'utilisateur n'as pas demandé l'arret du traitement
    if instanceProgression.drapeauArretFonctionEnCours==True:
        instanceProgression.fenetreProgression.close()
        instanceProgression.Reset()
        instanceProgression.close()
        del instanceProgression
        return 2  
    #initialisation de la liste qui stockera les isophones de type A
    listeGeomInterLDA=[]
    listeAttrInterLDA=[]
    listeGeomInterLNA=[]
    listeAttrInterLNA=[]
    #initialisation de la liste qui stockera les isophones de type B
    listeGeomInterB=[]
    listeAttrInterB=[]
    #initialisation de la liste qui stockera les isophones de type C
    listeGeomInterLDC=[]
    listeAttrInterLDC=[]
    listeGeomInterLNC=[]
    listeAttrInterLNC=[]
    #initialisation de la liste qui stockera les isophones de type D
    listeGeomInterLDD=[]
    listeAttrInterLDD=[]
    listeGeomInterLND=[]
    listeAttrInterLND=[]
    #on parcourt la liste de fichiers dans le dossier sélectionné par l'utilisateur - lien avec interface
    compteurNbEntiteTot=0
    for k in range(nbFichiers) :
        nomFichierAvecExt=listeNomFichierAvecExtension[k]
        coucheZbr=QgsVectorLayer(urlZbr+os.sep+nomFichierAvecExt, nomFichierAvecExt[:-4], "ogr")
        nbEntites=coucheZbr.featureCount()
        entitesZbr=coucheZbr.getFeatures()
        for feat in entitesZbr :
            geomZbr=feat.geometry()
            geomOut=geomZbr.buffer(0,0)
            if geomOut.isMultipart():
                for geom in  geomOut.asMultiPolygon():
                    compteurNbEntiteTot=compteurNbEntiteTot+1
            else:
                compteurNbEntiteTot=compteurNbEntiteTot+1
    #informations à afficher dans fenêtre de progression
    instanceProgression.InitialiserBarreProgressionLocale(compteurNbEntiteTot, u"Nombre d'étapes de traitement :" + '\n' + ' 2 / 3' + '\n'+ '\n'+ u"Sélection des isophones situés à l'intérieur du périmètre choisi")
    compteur=1    
    for k in range(len(listeNomFichierAvecExtension)) :
        nomFichierAvecExt=listeNomFichierAvecExtension[k]
        #vérification si l'utilisateur n'as pas demandé l'arret du traitement
        if instanceProgression.drapeauArretFonctionEnCours==True:
            instanceProgression.fenetreProgression.close()
            instanceProgression.Reset()
            instanceProgression.close()
            del instanceProgression
            return 2
        #informations à afficher dans fenêtre de progression
        instanceProgression.labelCoucheATraiter.setText(u'Nombre de fichiers traités :'+ 
                '\n'+ str(k)+' / '+ str(nbFichiers) +
                '\n'+'\n'+'\n'+
                u'Fichier en cours de traitement : ' +
                '\n' + nomFichierAvecExt[:-4])
        #on considère le fichier comme une couche SIG
        coucheZbr=QgsVectorLayer(urlZbr+os.sep+nomFichierAvecExt, nomFichierAvecExt[:-4], "ogr")
        #on récupère les numéros des champs CBSTYPE - utile pour trier les couches et les agréger par type 
        numChampsCbstype=coucheZbr.fieldNameIndex("CBSTYPE")
        numChampsIndicetype=coucheZbr.fieldNameIndex("INDICETYPE")
        numChampsLegende=coucheZbr.fieldNameIndex("LEGENDE")
        #on récupère les numéros de champs dont il faut adapter la valeur pour cause d'agrégation
        numChampsIdzonbruit=coucheZbr.fieldNameIndex("IDZONBRUIT")
        numChampsIdcbs=coucheZbr.fieldNameIndex("IDCBS")
        numChampsUueid=coucheZbr.fieldNameIndex("UUEID")
        numChampsCodedept=coucheZbr.fieldNameIndex("CODEDEPT")
        numChampsCodinfra=coucheZbr.fieldNameIndex("CODINFRA")
        entitesZbr=coucheZbr.getFeatures()
        for feat in entitesZbr :
            #vérification si l'utilisateur n'as pas demandé l'arret du traitement
            if instanceProgression.drapeauArretFonctionEnCours==True:
                instanceProgression.fenetreProgression.close()
                instanceProgression.Reset()
                instanceProgression.close()
                del instanceProgression
                return 2
            geomZbr=feat.geometryAndOwnership()
            attrZbr=feat.attributes() 
            listeGeomZbr=TransformeEnListeGeomSimple(geomZbr)
            listeGeomInter=[]
            for geomZbr in listeGeomZbr :
                #vérification si l'utilisateur n'as pas demandé l'arret du traitement
                if instanceProgression.drapeauArretFonctionEnCours==True:
                    instanceProgression.fenetreProgression.close()
                    instanceProgression.Reset()
                    instanceProgression.close()
                    del instanceProgression
                    return 2
                inter=geomZbr.intersection(geomPerimetre)
                #incrémentation de la barre de progression
                instanceProgression.progressBarLocale.setValue(compteur)
                QCoreApplication.processEvents()
                compteur=compteur+1
                if inter.area()!=0:
                    listeGeomInter.append(inter)
                else : 
                    print "geom vide"
            for geomZbr in listeGeomInter :
                if inter.area() != 0 :
                    #on trie les isophones en fonction du type de carte
                    #vérification si l'utilisateur n'as pas demandé l'arret du traitement
                    if instanceProgression.drapeauArretFonctionEnCours==True:
                        instanceProgression.fenetreProgression.close()
                        instanceProgression.Reset()
                        instanceProgression.close()
                        del instanceProgression
                        return 2
                    #tri des isophones qui intersectent le périmètre en fonction du type de carte (LDA, LNA, B, LDC, LNC, LDD, LND)
                    if attrZbr[numChampsCbstype]=="A"and attrZbr[numChampsIndicetype]=="LD":
                        listeGeomInterLDA.append(geomZbr)
                        listeAttrInterLDA.append(attrZbr)
                        #legende=dicoLegende.get("LDA")
                    elif attrZbr[numChampsCbstype]=="A"and attrZbr[numChampsIndicetype]=="LN":
                        listeGeomInterLNA.append(geomZbr)
                        listeAttrInterLNA.append(attrZbr)
                        #legende=dicoLegende.get("LNA")
                    elif attrZbr[numChampsCbstype]=="B":
                        listeGeomInterB.append(geomZbr)
                        listeAttrInterB.append(attrZbr)
                        #legende=dicoLegende.get("B")
                    elif attrZbr[numChampsCbstype]=="C" and attrZbr[numChampsIndicetype]=="LD":
                        listeGeomInterLDC.append(geomZbr)
                        listeAttrInterLDC.append(attrZbr)
                        #legende=dicoLegende.get("LDC")
                    elif attrZbr[numChampsCbstype]=="C" and attrZbr[numChampsIndicetype]=="LN":
                        listeGeomInterLNC.append(geomZbr)
                        listeAttrInterLNC.append(attrZbr)
                        #legende=dicoLegende.get("LNC")
                    elif attrZbr[numChampsCbstype]=="D"and attrZbr[numChampsIndicetype]=="LD":
                        listeGeomInterLDD.append(geomZbr)
                        listeAttrInterLDD.append(attrZbr)
                    elif attrZbr[numChampsCbstype]=="D"and attrZbr[numChampsIndicetype]=="LN":
                        listeGeomInterLND.append(geomZbr)
                        listeAttrInterLND.append(attrZbr)
                        #legende=dicoLegende.get("D")
                else : 
                    print "aucun isophone dans le perimetre administratif choisi"
    #dictionnaire par type indice des géométries    
    dicoGeomIntersection={"LDA": listeGeomInterLDA, "LNA" :listeGeomInterLNA,"LNU": listeGeomInterB,"LDC" :listeGeomInterLDC, "LNC" : listeGeomInterLNC, "LDD" : listeGeomInterLDD, "LND" : listeGeomInterLND}
    #dictionnaire par type indice des attributs
    dicoAttrIntersection={"LDA": listeAttrInterLDA, "LNA" :listeAttrInterLNA,"LNU": listeAttrInterB,"LDC" :listeAttrInterLDC, "LNC" : listeAttrInterLNC, "LDD" : listeAttrInterLND, "LND" : listeAttrInterLND}
    #============================================================================================
    #agrégation des isophones compris dans le périmètre administratif - création d'un fichier shp
    #============================================================================================
    #dico légende 
    dicoLegende={"LDA" :[55,60,65,70,75],"LNA" :[50,55,60,65,70],"LNU" :['00'], "LDC" :[68,73],"LNC" :[62,65],"LDD" :["+8","+5","+2","+0","-2","-5","-8"], "LND" :["+8","+5","+2","+0","-2","-5","-8"]}
    #liste des indice type carte sur laquelle on va boucler
    listeIndice=["LDA","LNA","LNU","LDC","LNC","LDD", "LND"]
    #informations à afficher dans fenêtre de progression
    instanceProgression.progressBarLocale.setValue(0)
    instanceProgression.labelCoucheATraiter.setText(u'Agrégation géométrique des isophones contenus dans le périmètre\net création des fichiers agrégés')
    compteur=1
    for l in range(len(listeIndice)) :
        #vérification si l'utilisateur n'as pas demandé l'arret du traitement
        if instanceProgression.drapeauArretFonctionEnCours==True:
            instanceProgression.fenetreProgression.close()
            instanceProgression.Reset()
            instanceProgression.close()
            del instanceProgression
            return 2
        indice=listeIndice[l]
        #initialisation des listes de stockage 
        valeursLegende=[]
        #geomAgreg=QgsGeometry.fromWkt('GEOMETRYCOLLECTION()')
        geomAgregDef=[]
        listeGeomIntersection=dicoGeomIntersection.get(indice)
        listeAttrIntersection=dicoAttrIntersection.get(indice)
        legende=dicoLegende.get(indice)
        valeursAttributairesAgreg=[]
        #informations à afficher dans fenêtre de progression
        valeursLegendePourCompte=[]
        compteurNbGeom=0
        if len(listeAttrIntersection)!= 0 :
            for a in range(len(listeAttrIntersection)) :
                valeurLegendePourCompte=listeAttrIntersection [a][numChampsLegende]
                valeursLegendePourCompte.append(valeurLegendePourCompte)
            for b in range(len(legende)) :
                for c in range(len(valeursLegendePourCompte)) :
                    if valeursLegendePourCompte[c]==str(legende[b]) :
                        compteurNbGeom=compteurNbGeom+1
        instanceProgression.progressBarLocale.setValue(0)
        instanceProgression.progressBarLocale.setMaximum(compteurNbGeom)
        instanceProgression.labelNomEtape.setText(u"Nombre d'étapes de traitement :" + '\n' + ' 3 / 3' + '\n'+ '\n'+'Traitement en cours :'  + '\n'+u"Agrégation des isophones issus des cartes de type " + indice)
        #si les isophones intersectent alors
        if len(listeAttrIntersection)!= 0 :
            #détermination d'une liste des valeurs du champ LEGENDE des isophones
            for k in range(len(listeAttrIntersection)) :
                #vérification si l'utilisateur n'as pas demandé l'arret du traitement
                if instanceProgression.drapeauArretFonctionEnCours==True:
                    instanceProgression.fenetreProgression.close()
                    instanceProgression.Reset()
                    instanceProgression.close()
                    del instanceProgression
                    return 2 
                valeurLegende=listeAttrIntersection [k][numChampsLegende]
                valeursLegende.append(valeurLegende)
            #on balaye les valeurs des légendes fixes (extraites du dictionnaire légende)
            compteurAttr=-1
            for j in range(len(legende)) :
                geomPardB=[]
                attrPardB=[]
                geomAgreg=QgsGeometry.fromWkt('GEOMETRYCOLLECTION()')
                for i in range(len(valeursLegende)) :
                	#vérification si l'utilisateur n'as pas demandé l'arret du traitement
                	if instanceProgression.drapeauArretFonctionEnCours==True:
                		instanceProgression.fenetreProgression.close()
                		instanceProgression.Reset()
                		instanceProgression.close()
                		del instanceProgression
                		return 2
                	if valeursLegende[i]==str(legende[j]) :
                		geomPardB.append(listeGeomIntersection[i])
                		attrPardB.append(listeAttrIntersection[i])
                	else : 
                		pass
                try : # gestion d'une erreur pour les fichiers de type C : il peut arriver que attrPardB[0]=rien, ce qui souleve une erreur, qu'on traite avec ce try
                	valeursAttributairesAgreg.append(attrPardB[0])
                	compteurAttr=compteurAttr+1
                	codInfra="-" + valeursAttributairesAgreg[compteurAttr][numChampsIdzonbruit].split("-")[1]
                	if departementATraiter=='' :
                		valeursAttributairesAgreg[compteurAttr][numChampsUueid]=""
                		valeursAttributairesAgreg[compteurAttr][numChampsCodedept]="000"
                		valeursAttributairesAgreg[compteurAttr][numChampsCodinfra]=""
                		valeursAttributairesAgreg[compteurAttr][numChampsIdzonbruit]=valeursAttributairesAgreg[compteurAttr][numChampsIdzonbruit].replace(codInfra, '').replace('%temp%', '000000000000')
                		valeursAttributairesAgreg[compteurAttr][numChampsIdcbs]=valeursAttributairesAgreg[compteurAttr][numChampsIdcbs].replace(valeursAttributairesAgreg[compteurAttr][numChampsIdcbs][7:19],'%temp%').replace(codInfra, '').replace('%temp%', '000000000000')
                	else :
                		valeursAttributairesAgreg[compteurAttr][numChampsUueid]=""
                		valeursAttributairesAgreg[compteurAttr][numChampsCodinfra]=""
                		#valeursAttributairesAgreg[i][numChampsIdzonbruit]=valeursAttributairesAgreg[i][numChampsIdzonbruit].replace(valeursAttributairesAgreg[i][numChampsIdzonbruit][10:19], '000000000')
                		valeursAttributairesAgreg[compteurAttr][numChampsIdzonbruit]=valeursAttributairesAgreg[compteurAttr][numChampsIdzonbruit].replace(valeursAttributairesAgreg[compteurAttr][numChampsIdzonbruit][10:19], '%temp%').replace(codInfra, '').replace('%temp%', '000000000')
                		valeursAttributairesAgreg[compteurAttr][numChampsIdcbs]=valeursAttributairesAgreg[compteurAttr][numChampsIdcbs].replace(valeursAttributairesAgreg[compteurAttr][numChampsIdcbs][10:19],'%temp%').replace(codInfra, '').replace('%temp%', '000000000')
                except :
                	pass
                for k in range(len(geomPardB)) :
                    #vérification si l'utilisateur n'as pas demandé l'arret du traitement
                   	if instanceProgression.drapeauArretFonctionEnCours==True:
                   		instanceProgression.fenetreProgression.close()
                   		instanceProgression.Reset()
                   		instanceProgression.close()
                   		del instanceProgression
                   		return 2       
                   	geom=geomPardB[k]
                   	geomAgreg=geomAgreg.combine(geom)
                    #informations à afficher dans fenêtre de progression
                   	instanceProgression.progressBarLocale.setValue(compteur)
                   	compteur=compteur+1
                   	QCoreApplication.processEvents()
                geomAgregDef.append(geomAgreg)
            #vérification si l'utilisateur n'as pas demandé l'arret du traitement
            if instanceProgression.drapeauArretFonctionEnCours==True:
                instanceProgression.fenetreProgression.close()
                instanceProgression.Reset()
                instanceProgression.close()
                del instanceProgression
                return 2
            if len(geomAgregDef)!= 0:
                #on crée le fichier pour stocker les isophones compris dans le périmètre administratif
                nomFichierAgreg=NOMAGREGZBR%(indice)
                ecritureCoucheAgreg = QgsVectorFileWriter(urlSortie+os.sep+nomFichierAgreg,encodage,champsAttributairesZBR,typeGeometrie,srid,driverExport)
                compteurValeursAttr=range(len(valeursAttributairesAgreg))
                for i in range(len(valeursAttributairesAgreg)) :
                	#ajout d'entités dans la couche
                	entiteAgreg= QgsFeature()
                	entiteAgreg.setGeometry(geomAgregDef[i])
                	entiteAgreg.setAttributes(valeursAttributairesAgreg[i])
                   	ecritureCoucheAgreg.addFeature(entiteAgreg)
                #récupération de l'emplacement du fichier style associée à la couche 
                urlFichierStyle=RecuperationFichierStyle(indice)
                #déterminationr de l'emplacement de stockage du fichier style incluant le nom du fichier style (renommage comme le fichier N_BRUITZBR
                nomAgregQml=NOMAGREGQML%(indice)
                urlAgregQml=urlSortie+os.sep+nomAgregQml
                #copie du fichier style initial stocké dans dossier 'ressources' de Mizogeo pour le mettre dans le dossier Zbr avec le même nom que le fichier N_BRUIT_ZBR
                shutil.copyfile(urlFichierStyle, urlAgregQml)
            del ecritureCoucheAgreg
            os.remove(urlSortie+os.sep+nomFichierAgreg+ ".qpj")
        else :
            print "pas d'isophones pour cet indice"
    #fermeture de la barre de progression
    instanceProgression.fenetreProgression.close()
    instanceProgression.Reset()
    instanceProgression.close()
    del instanceProgression
    return 0
