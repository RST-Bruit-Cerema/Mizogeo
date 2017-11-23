# -*- coding: utf-8 -*-

import os
from qgis.core import *
import qgis.utils
from outilsFonctions import OutilDetectionStructureNomFichier,OutilDecoupageNomFichier,OutilDetectionCodeDept,OutilDetectionNomdB,OutilVerficationDoublon,OutilRechercheNomDansListe
from outilsFonctions import OutilDetectionErreursGeometriques,OutilDetectionAnomaliesGeometriques
from outilsFonctions import OutilDetectionNomChampsAttributaires,OutilDetectionNomChampsAttributairesAssemblageAgregation,OutilDetectionValeursAttributaires
from outilsFonctions import OutilDetectionChargementCouche,OutilDetectionCodInfra
from outilsFonctions import OutilCompteur
from recuperationDonnees import RecuperationIdentifiants,RecuperationListeNomFichierCorrespondance,RecuperationCodInfra, RecuperationContourDepartement,OuvreCSV
from parametres import ListeChampsImpose, UrlFichierSigLimiteAdministrative,urlDonneesComplementaires
import interfaceUtilisateur
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QCoreApplication
from PyQt4.QtGui import QMessageBox


#Vérification complète du fichier Isophone (CBS 2012 Route/Fer et CBS issues MithraSIG Route/Fer)
def VerificationCompleteIsophone(urlDossierIsophone,listeNomFichierAvecExtension,urlSortie,urlCorrespondanceSIG,urlVoiesNouvelles) :
    """
    en entrée
        urlDossierIsophone ---> type str
        listeNomFichierAvecExtension ---> type liste str (type tupple)
        urlSortie ---> type str
    en sortie
        texte d'erreur ---> type str
    """
    listeNomFichierCorrespondance,listeGestionnaire = RecuperationListeNomFichierCorrespondance(urlCorrespondanceSIG,urlVoiesNouvelles)
    doublonsFichiers=OutilVerficationDoublon(listeNomFichierCorrespondance)
    #initialisation du texte global 
    txtFichierErreurs=str("")
    #informations relatives à afficher dans la barre de progression
    progression=interfaceUtilisateur.ProgressBar()
    nombreFichier=len(listeNomFichierAvecExtension)
    progression.InitialiserBarreProgressionLocale(nombreFichier, u'Vérification de la validité des fichiers' + '\n' + u'étape 1 / 5 du traitement')
    #balayage de la liste des noms des fichiers sans extension
    for i in range(len(listeNomFichierAvecExtension)) :
        nomFichierIsophoneAvecExtension=listeNomFichierAvecExtension[i]
        #vérification de présence de doublons entre les voies contenues dans TableCorrespondanceNomSIG.csv et TableVoieNouvelle.csv
        if nomFichierIsophoneAvecExtension[:-8] in doublonsFichiers : 
            txtRedondance=u'Le fichier est déclaré à la fois dans tableCorrespondanceNomSIG.csv et tableVoieNouvelle.csv'
        else : 
            txtRedondance='OK'
        #on considère le fichier Isophone comme une couche SIG
        coucheIsophone= QgsVectorLayer(urlDossierIsophone+os.sep+nomFichierIsophoneAvecExtension, nomFichierIsophoneAvecExtension[:-4], "ogr")
        #vérification du bon chargement de la couche Isophone
        txtVerifChargement=OutilDetectionChargementCouche(coucheIsophone)
        #vérification de la validité du nom du fichier 
        txtVerifNomFichier=OutilDetectionStructureNomFichier(nomFichierIsophoneAvecExtension[:-4])[0]
        if txtVerifNomFichier=="OK" :
            #separation en [DDD][nom][Iso]
            codeDept, codInfra, nomdBPresume = OutilDecoupageNomFichier(nomFichierIsophoneAvecExtension[:-4])
            #verification du code département 
            txtVerifNomFichier +=';'+OutilDetectionCodeDept(codeDept)
            #verification du code infra pour route et fer
            txtVerifNomFichier +=';'+OutilDetectionCodInfra(codInfra)
            #verification de la plage des niveaux de bruit (LDA, par exemple)
            txtVerifNomFichier +=';'+OutilDetectionNomdB(nomdBPresume)
            if OutilCompteur("OK",txtVerifNomFichier)==4 :
                if codeDept+'_'+codInfra in listeNomFichierCorrespondance or codeDept+'_'+RecuperationCodInfra(codInfra) in listeNomFichierCorrespondance:
                    txt='pb'
                    nb=OutilRechercheNomDansListe(codeDept+'_'+codInfra,listeNomFichierCorrespondance)
                    if listeGestionnaire[nb] in ["Etat_nonconcede","Etat_concede","SNCF-Reseau","Conseil_Departemental"]:
                        txt=''
                    else :
                        donneesComplementaires=OuvreCSV(urlDonneesComplementaires) # renvoie une valeur de la matrice : tab[Numéro ligne][Numéro colonne]
                        for ligne in donneesComplementaires:
                            if listeGestionnaire[nb] == "Metropole" :
                            	if listeGestionnaire[nb]==ligne[5] :
                            		txt=''
                            		break
                            else :
                            	if listeGestionnaire[nb].upper()==ligne[1].replace(" ","-"):
                                	txt=''
                                	break
                      		
                    if txt=='':
                        txtVerifNomFichier +=';OK'
                    else :
                        txtVerifNomFichier +=";le gestionnaire de l'infra, " + listeGestionnaire[nb]+ ", n'a pas été trouvé dans la table Donnees complementaires"
                else:
                    txtVerifNomFichier +=";le code de l'infra n'est pas dans les tables de correspondance route, fer ou VC."
            else:
                txtVerifNomFichier +=";le nom du fichier n'est pas conforme"
        else :
           txtVerifNomFichier += ";Le format doit être du type (msig_)DDD_YY...YY_LDA avec underscore comme séparateurs;;" 
        if txtVerifChargement == "OK" :
            #numéro du champs où il y a le champs imposé CBS2012 ou CBS issues de MithraSIG
            txtVerifAttributaire,numChamps=OutilDetectionNomChampsAttributaires(coucheIsophone,ListeChampsImpose)
            #vérification de la validité de la table attributaire de la couche Isophone
            txtVerifAttributaire += ";" + OutilDetectionValeursAttributaires(coucheIsophone,numChamps)
            #vérification de la validité géométrique de la couche Isophone
            try :
                txtVerifGeom=VerificationGeometrieIsophones(codeDept,coucheIsophone,numChamps)
            except:
                txtVerifGeom='non verifie'
        else : 
            txtVerifAttributaire=str("")
            txtVerifGeom=str("")
            #alimentation du texte global qui sera repris dans le fichier csv 
        txtVerifComplete= nomFichierIsophoneAvecExtension+ ";"+txtVerifChargement + ";" + txtVerifNomFichier + ";" + txtVerifAttributaire + ";" + txtVerifGeom + ";" + txtRedondance +'\n'
        if OutilCompteur("OK",txtVerifComplete)==12 :
            txtFichierErreurs+=str("")
        else : 
            txtFichierErreurs+=txtVerifComplete
        #incrémentation de la barre de progression
        progression.progressBarLocale.setValue(i+1)
        QCoreApplication.processEvents()
    #fermeture de la barre de progression
    progression.close()
    if txtFichierErreurs=="": 
        return True
    else :
        j = 1
        while os.path.exists(urlSortie+os.sep+'listeErreursIsophones_%s.csv'%j):
            j += 1
        fichierErreursCsv = open(urlSortie+os.sep+'listeErreursIsophones_%s.csv'%j, 'w')
        fichierErreursCsv.write('Fichier;Chargement couche;Structure nom fichier;Code département;Code infra;Classe niveaux;Correspondance 2017;Noms champs attributaires;Noms valeurs attributaires;Validité géométrique;Type objet (multi-)polygone;Système de projection;Redondance fichier de correspondance - fichier voies nouvelles\n')
        fichierErreursCsv.write(txtFichierErreurs)
        return False
    
    
#Vérification de validité géométrique + système de projection des fichiers Isophones
def VerificationGeometrieIsophones(codeDept,coucheIsophone,numChamps) :
    """
    en entrée
        codeDept = code département issue de la couche Isophone ---> type str
        coucheIsophone ---> type QgsVectorLayer
        numChamps ---> integer
    en sortie
        texte d'erreur ---> type str
    """
    #détection des erreurs géométriques
    txtDetectionErreursGeom=OutilDetectionErreursGeometriques(coucheIsophone,numChamps)
    #détection des anomalies géométriques
    txtDetectionAnomaliesGeom=OutilDetectionAnomaliesGeometriques(coucheIsophone)
    #détection du système de projection
    empriseCouche=coucheIsophone.extent()
    if codeDept in ['971','972','973','974']:
        textVerifProjection='OK'
    elif empriseCouche.xMaximum() < 1250000 and empriseCouche.xMinimum() > 100000 and empriseCouche.yMaximum()< 7130000 and empriseCouche.yMinimum()> 6025000 :
        textVerifProjection='OK'
    else:
        textVerifProjection=str("La projection n'est pas RGF93")
    txtVerifGeom= txtDetectionErreursGeom + ";" + txtDetectionAnomaliesGeom + ";" + textVerifProjection
    return txtVerifGeom

#Vérification de validité des fichiers à assembler (fichier dbf N_BRUIT_ZBR et N_BRUIT_CBS)
def VerificationFichiersAAssembler(urlDbf,listeNomFichierAvecExtension,champsAttributairesZBR,champsAttributairesCBS,urlSortie) : 
    """
    en entrée 
        urlDbf = chemin du dossier contenant les fichiers à assembler par Mizogeo (lien avec interface) ---> type str
        listeNomFichierAvecExtension = liste des fichiers contenus dans urlDbf ---> type list de str
        champsAttributairesZBR = définis dans parametres.py ---> type QgsFields
        champsAttributairesCBS = définis dans parametres.py ---> type QgsFields
        urlSortie = chemin du dossier contenant les fichiers créés par Mizogeo (fichier erreur ou fichiers Assemblage) (lien avec interface) ---> type str
    en sortie
        fichier csv d'erreurs à la racine du dossier urlSortie
    """
    #initialisation du texte global 
    txtFichierErreurs=str("")
    #vérification nom "N_BRUIT_CBS" ou "N_BRUIT_ZBR"
    for nomFichierAvecExt in listeNomFichierAvecExtension : 
        #on considère le fichier comme une couche SIG
        coucheDbf=QgsVectorLayer(urlDbf+os.sep+nomFichierAvecExt, nomFichierAvecExt[:-4], "ogr")
        #vérification du format du fichier (.dbf)
        if nomFichierAvecExt[-4:]==".dbf" : 
            txtVerifFormat="OK"
        else :
            txtVerifFormat="Le format du fichier n'est pas .dbf"
        #vérification de la présence de "N_BRUIT_ZBR" ou "N_BRUIT_CBS"
        if nomFichierAvecExt[0:11] =="N_BRUIT_ZBR" :
            txtDebutNom="OK"
            #vérification de la struture du nom du fichier (nombre d'underscore)
            if nomFichierAvecExt.count("_") == 9 and (nomFichierAvecExt[20] in ["A","N","D"]) : 
                txtNbUnderscore="OK"
            elif omFichierAvecExt.count("_") == 10 and nomFichierAvecExt[20]=="C" : 
                txtNbUnderscore="OK"
            else : 
                txtNbUnderscore="Problème de structure dans le nom du fichier"
            #vérification attributaire (présence champs GéoStandard)
            if len([field.name() for field in champsAttributairesZBR]) != len([field.name() for field in coucheDbf.pendingFields()]) :
               txtVerifAttributaire="Absence de champs spécifiques au type de fichier" 
            else : 
                txtVerifAttributaire=OutilDetectionNomChampsAttributairesAssemblageAgregation(coucheDbf,[field.name() for field in champsAttributairesZBR])[0]
        elif nomFichierAvecExt[0:11] =="N_BRUIT_CBS" :
            txtDebutNom="OK"
            #vérification de la struture du nom du fichier (nombre d'underscore)
            if nomFichierAvecExt.count("_")== 5 and (nomFichierAvecExt[18] in ["A","N","D","C"]) : 
                txtNbUnderscore="OK"
            elif nomFichierAvecExt.count("_")== 6 and nomFichierAvecExt[18]=="C" : 
                txtNbUnderscore="OK"
            else : 
                txtNbUnderscore="Problème de structure du nom du fichier"
            #vérification attributaire (présence champs GéoStandard)
            if len([field.name() for field in champsAttributairesCBS]) != len([field.name() for field in coucheDbf.pendingFields()]) :
               txtVerifAttributaire="Absence de champs spécifiques au type de fichier" 
            else : 
                txtVerifAttributaire=OutilDetectionNomChampsAttributairesAssemblageAgregation(coucheDbf,[field.name() for field in champsAttributairesCBS])[0]
        else :
            txtDebutNom="Le fichier ne commence pas par N_BRUIT_ZBR ou N_BRUIT_CBS"
            txtNbUnderscore="Impossible de vérifier la structure du nom du fichier"
            txtVerifAttributaire="La table attributaire n'a pas été vérifiée"
        txtVerifFichier=nomFichierAvecExt + ";" + txtVerifFormat + ";" + txtDebutNom + ";" + txtNbUnderscore +";" + txtVerifAttributaire +'\n'
        if OutilCompteur("OK",txtVerifFichier)==4 :
            txtFichierErreurs+=str("")
        else : 
            txtFichierErreurs+=txtVerifFichier  
    if txtFichierErreurs=="": 
        return True
    else :
        j = 1
        while os.path.exists(urlSortie+os.sep+'listeErreursFichiersAssemblage_%s.csv'%j):
            j += 1
        fichierErreursCsv = open(urlSortie+os.sep+'listeErreursFichiersAssemblage_%s.csv'%j, 'w')
        fichierErreursCsv.write('Fichier;Format DBF;Conformité nom fichier;Structure nom fichier;Noms champs attributaires\n')
        fichierErreursCsv.write(txtFichierErreurs)
        return False

#Vérification de validité des fichiers à agrégation (fichier shp N_BRUIT_ZBR)
def VerificationFichiersAAgreger(urlZbr,listeNomFichierAvecExtension,champsAttributairesZBR,urlSortie,departementATraiter,urlPerimetre) : 
    """
    en entrée 
        urlZbr = chemin du dossier contenant les fichiers à agréger par Mizogeo (lien avec interface) ---> type str
        listeNomFichierAvecExtension = liste des fichiers contenus dans urlDbf ---> type list de str
        champsAttributairesZBR = définis dans parametres.py ---> type QgsFields
        urlSortie = chemin du dossier contenant les fichiers créés par Mizogeo (fichier erreur ou fichiers Assemblage) (lien avec interface) ---> type str
        departementATraiter = code dept (str) donné par l'utilisateur dans l'interface ou vide ---> type str
        urlPerimetre = chemin du dossier contenant le shp du périmètre donné par l'utilisateur dans l'interface ou vide ---> type str
    en sortie 
        fichier csv d'erreurs à la racine du dossier urlSortie
    """
    #initialisation du texte global 
    txtFichierErreurs=str("")
    #initialisation barre progression
    progression=interfaceUtilisateur.ProgressBar()
    nombreFichier=len(listeNomFichierAvecExtension)
    i=0
    nbObjetTot=0
    #initialisation du nb de traitement geometrique#vérification nom "N_BRUIT_CBS" ou "N_BRUIT_ZBR"
    for nomFichierAvecExt in listeNomFichierAvecExtension :
        coucheZbr=QgsVectorLayer(urlZbr+os.sep+nomFichierAvecExt, nomFichierAvecExt[:-4], "ogr")
        features=coucheZbr.getFeatures()
        for feat in features :
            nbObjetTot=nbObjetTot+1
    #informations relatives aux informations à afficher dans la fenêtre de progression
    progression.InitialiserBarreProgressionLocale(nbObjetTot, u'Vérification de la validité des fichiers' + '\n' + u'étape 1 / 3 du traitement')
    #recuperation des geometries de decoupage (identique à creationAgregation)
    if departementATraiter == '' :
        #on considère la couche "périmètre administratif" comme une couche SIG
        couchePerimetre=QgsVectorLayer(urlPerimetre, u"périmètre administratif choisi par utilisateur", "ogr")
        #on fixe le système de coordonnées
        srid=couchePerimetre.crs()
        #on récuère la géométrie du périmètre administratf 
        entitePerimetre=couchePerimetre.getFeatures().next()
        #print "entitePerimetre"
        geomPerimetre= entitePerimetre.geometry()
    else :
        urlPerimetre,srid= UrlFichierSigLimiteAdministrative(departementATraiter)
        couchePerimetre,entitePerimetre=RecuperationContourDepartement(departementATraiter,urlPerimetre)
        for feat in entitePerimetre:
            geomPerimetre= feat.geometry()
    #vérification nom "N_BRUIT_CBS" ou "N_BRUIT_ZBR"
    for nomFichierAvecExt in listeNomFichierAvecExtension : 
        #informations relatives aux informations à afficher dans la fenêtre de progression
        progression.labelCoucheATraiter.setText(u'Fichier en cours de traitement : ' + '\n' + nomFichierAvecExt[:-4])
        #on considère le fichier comme une couche SIG
        coucheZbr=QgsVectorLayer(urlZbr+os.sep+nomFichierAvecExt, nomFichierAvecExt[:-4], "ogr")
        #vérification de la présence de "N_BRUIT_ZBR"
        if nomFichierAvecExt[0:11] =="N_BRUIT_ZBR" :
            txtDebutNom="OK"
            #vérification de la struture du nom du fichier (nombre d'underscore)
            if nomFichierAvecExt.count("_") == 9 and (nomFichierAvecExt[20] in ["A","N","D"]) : 
                txtNbUnderscore="OK"
            elif nomFichierAvecExt.count("_") == 10 and nomFichierAvecExt[20]=="C" : 
                txtNbUnderscore="OK"
            else : 
                txtNbUnderscore="Probleme de structure dans le nom du fichier"
            #vérification attributaire (présence champs GéoStandard)
            if len([field.name() for field in champsAttributairesZBR]) != len([field.name() for field in coucheZbr.pendingFields()]) :
               txtVerifAttributaire=u"Absence de champs specifiques au type de fichier" 
            else : 
                txtVerifAttributaire=OutilDetectionNomChampsAttributairesAssemblageAgregation(coucheZbr,[field.name() for field in champsAttributairesZBR])[0]
        else :
            txtDebutNom=u"Le fichier ne commence pas par N_BRUIT_ZBR"
            txtNbUnderscore=u"Impossible de verifier la structure du nom du fichier"
            txtVerifAttributaire=u"La table attributaire n\'a pas ete verifiee"
        #verification de l'intersection de l'intégralité des objets de la couche zbr avec la couhce de perimètre, creation de la validite geometrique
        features=coucheZbr.getFeatures()
        verifIntersectionObjet=[]
        verifValiditeGeometrique=[] 
        for feat in features :
            try :
                if feat.geometry().intersects(geomPerimetre):
                    verifIntersectionObjet.append("OK")
                else :
                    verifIntersectionObjet.append("ERREUR")
                verifValiditeGeometrique.append("OK")
            except :
                verifValiditeGeometrique.append("ERREUR")
            #incrémentation de la barre de progression
            i=i+1
            progression.progressBarLocale.setValue(i)
            QCoreApplication.processEvents()
        if verifIntersectionObjet.count("OK")==len(verifIntersectionObjet): #si tout les objets intersecte le contour
            txtVerifIntersection="OK"
        else : 
            txtVerifIntersection=u"Un ou plusieurs objets du fichier n\'intersectent pas le contour de decoupe"

        if verifValiditeGeometrique.count("OK")==len(verifValiditeGeometrique): #si tout sont geometriquemnt ok
            txtValiditeGeometrique="OK"
        else : 
            txtValiditeGeometrique=u"Un ou plusieurs objets du fichier presente des geometries erronnees"
        txtVerifFichier=nomFichierAvecExt + ";" + txtDebutNom + ";" + txtNbUnderscore +";" + txtVerifAttributaire + ";"+ txtVerifIntersection + ";" + txtValiditeGeometrique + '\n'
        if OutilCompteur("OK",txtVerifFichier)==5 :
            txtFichierErreurs+=str("")
        else : 
            txtFichierErreurs+=txtVerifFichier
    if txtFichierErreurs=="": 
        return True
    else :
        j = 1
        while os.path.exists(urlSortie+os.sep+'listeErreursAgregation_%s.csv'%j):
            j += 1
        fichierErreursCsv = open(urlSortie+os.sep+'listeErreursAgregation_%s.csv'%j, 'w')
        titre=u"Fichier a agreger;Conformite nom fichier;Structure nom fichier;Noms champs attributaires;Intersection fichier-contour;Validite Geometrique\n"
        fichierErreursCsv.write(titre)
        fichierErreursCsv.write(txtFichierErreurs)
        return False

#Vérification des données contenues dans le QlineEdit résumant les départements sélectionnés
def VerificationDepartementPpbe(listeDepartement):
    """
    en entree 
        listeDepartement ----> tye list de string
    en sortie 
        1 ou 0 ---> type int
    """
    nbCaracteresNonToleres=len(listeDepartement)-sum(c.isdigit() for c in listeDepartement)-listeDepartement.count(',')#deduction d'apres le calcul du nombre de chiffre et de , dans le texte
    
    departementATraiter=listeDepartement.split(',')#verification que chaque departement est bien ecrit sur 3 chiffres
    nbErreurlongueur=0
    for dept in departementATraiter :
        if len(dept) !=3 :
            nbErreurlongueur+=1
    
    if nbCaracteresNonToleres !=0 or nbErreurlongueur!=0 :
        return 1
    else : 
        return 0    