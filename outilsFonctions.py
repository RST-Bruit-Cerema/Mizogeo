# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------------------------------------------------------------------------------------
#Fichier regroupant toutes les fonctions dites "outils" servant de bases aux fonctions globales de vérifications, traitement, récupération
#----------------------------------------------------------------------------------------------------------------------------------------------------------

import os
from qgis.core import *

#fonction de listing des fichiers isophones contenus dans le dossier sélectionné par l'utilisateur en fonction
def OutilListingFichiers(dossierUtilisateur) :
    """
    en entrée
        dossierUtilisateur = dossier indiqué par l'utilisateur via l'interface graphique ---> type str
    en sortie
        liste des noms des fichiers avec extensions ---> type list 
        nombre de fichiers listés ---> type int
    """
    listeFichiers = os.listdir(dossierUtilisateur)
    fichiersSHP=[]
    fichiersTAB=[]
    fichiersMID=[]
    fichiersDBF=[]
    for fichier in listeFichiers :
        if fichier[-4:].lower() in ['.shp'] : # or txt[-7:].lower()=='lna.shp':
            fichiersSHP.append(fichier)
        elif fichier[-4:].lower() in ['.tab'] :# or txt[-7:].lower()=='lna.tab':
            fichiersTAB.append(fichier)
        elif fichier[-4:].lower() in ['.mid'] :# or txt[-7:].lower()=='lna.mid':
            fichiersMID.append(fichier)
        elif fichier[-4:].lower() in ['.dbf'] :# or txt[-7:].lower()=='lna.mid':
            fichiersDBF.append(fichier)
    listeNomFichierAvecExtension=[]
    listeNomFichierSansExtension=[]
    for fichierTypeSig in [fichiersSHP, fichiersTAB, fichiersMID, fichiersDBF]:
        for sig_path in fichierTypeSig:
            nomFichierUtf8=sig_path.encode('utf-8')
            if not(nomFichierUtf8[:-4] in listeNomFichierSansExtension) :
                listeNomFichierAvecExtension.append(nomFichierUtf8)
                listeNomFichierSansExtension.append(nomFichierUtf8[:-4])
    #définition du nombre de fichiers listés 
    nbFichiers=len(listeNomFichierAvecExtension)
    return listeNomFichierAvecExtension,nbFichiers
    
#fonction de détection de "underscore" dans le nom du fichier
def OutilDetectionStructureNomFichier(nomFichierIsophoneSansExtension) :
    """
    en entrée
        nom du fichier sans l'extenstion (ex : 063_D2089_LDA) --> type str 
    en sortie
        texte d'erreur 'OK' ou 'Problème du nombre d'underscore' --> type str
    """
    #compter le nombre d'underscores contenus dans le nom du fichier isophone
    nbUnderscore=nomFichierIsophoneSansExtension.count("_")
    #si il y a moins de 2 underscore pb
    if nbUnderscore<2:
        txtDetectionUnderscore= "Problème de structure"
    #si il y a moins de 3 underscore et fichier MithraSig pb
    elif nbUnderscore<3 and nomFichierIsophoneSansExtension[:4]=='msig':
        txtDetectionUnderscore= "Problème de structure"
    else :
        txtDetectionUnderscore= "OK"
    return txtDetectionUnderscore,nbUnderscore
    
    
#fonction de découpage de nom de fichier en fonction des underscore
def OutilDecoupageNomFichier(nomFichierIsophoneSansExtension) :
    """
    en entrée
        nom du fichier sans l'extenstion (ex : 063_D2089_LDA) --> type str 
    en sortie 
        codeDeptPresume ---> type str
        codInfraPresume ---> type str
        nomdBPresume ---> type str
    """
    #decomposition du nom du fichier en coupant au niveau des underscores
    donneesInfra=nomFichierIsophoneSansExtension.split("_")
    #vérification de la structure du nom du fichier
    i=0    
    if nomFichierIsophoneSansExtension[:4]=='msig':
      i=1
    codeDeptPresume=donneesInfra[i+0]
    codInfraPresume='_'.join(donneesInfra[i+1:-1])
    nomdBPresume=donneesInfra[-1]
    return codeDeptPresume, codInfraPresume, nomdBPresume


#fonction de détection du code du département dans le nom du fichier
def OutilDetectionCodeDept(codeDeptPresume) :
    """
    en entrée
        codeDeptPresume (résultat de la fonction OutilDecoupageNomFichier) ---> type str
    en sortie
        texte d'erreur "code département OK" ou "code département doit être sur les 3 premiers caractères" ---> type str
    """
    #initialisation du texte 
    txtDetectionCodeDept = str("")
    #cas où le nombre d'underscore est 2 (cas CBS2012) ou 3 (cas CBS issues de MithraSIG) -> info connue via fonction OutilDetectionUnderscore(nomFichierIsophoneSansExtension)
    if len(codeDeptPresume)==3 : 
        if codeDeptPresume in ('02A','02B'):
            txtDetectionCodeDept+="OK"
        else :
            try:
                numDeptPresume=int(codeDeptPresume)
                if numDeptPresume < 96 or numDeptPresume  in range (971,977) and len(codeDeptPresume) ==3:
                    txtDetectionCodeDept+="OK"
                else : 
                    txtDetectionCodeDept+="code département doit être sur les 3 premiers caractères"
            except : 
                txtDetectionCodeDept+="code département doit être sur les 3 premiers caractères"
    else : 
        txtDetectionCodeDept+="code département doit être sur les 3 premiers caractères"
    return txtDetectionCodeDept


#fonction de détection du code infra (route et fer) dans le nom du fichier
def OutilDetectionCodInfra(codInfraPresume): 
    """
    en entrée
        codInfraPresume (résultat de la fonction OutilDecoupageNomFichier) ---> type str
            du type route : 1er lettre A,N,D,V puis chiffre, et éventuellement une lettre
            du type fer : 6 chiffres
    en sortie
        texte d'erreur ---> type str
    """
    #initialisation du texte 
    txtDetectionCodInfra = str("")
    typeVoie=codInfraPresume[0]
    #pour les voies ferrées
    if typeVoie in ["0","1","2","3","4","5","6","7","8","9"] :
        try :
            #vérification si que des chiffres
            int(codInfraPresume)
            #vérification de la longueur du codInfra
            if len(codInfraPresume)!= 6 :
                txtDetectionCodInfra+="numéro ligne ferroviaire doit être sur 6 caractères"
            else :
                txtDetectionCodInfra+="numéro ligne ferroviaire OK"
        except :            
            txtDetectionCodInfra+="numéro ligne ferroviaire doit être sur 6 caractères"
    #pour les infras routières
    elif typeVoie in ["A","N","D","V","C"] :
        txtDetectionCodInfra+="code route OK"
    #si ni conforme au code fer ni conforme au code route	
    else:
        txtDetectionCodInfra+="Code route doit commencer par A,N,D,V ou C"
    return txtDetectionCodInfra
  
  
#fonction de détection du code infra (route et fer) dans le nom du fichier
def OutilDetectionNomdB(nomdBPresume): 
    """
    en entrée
        nomdBPresume (ex : LDA) (résultat de la fonction OutilDecoupageNomFichier) ---> type str
    en sortie
        texte d'erreur ---> type str
    """
    #initialisation du texte 
    txtDetectionNomdB= str("")
    #vérification du nomdB (idem aux infras routières et ferroviaires)
    if nomdBPresume in ["LDA","LNA","LNU","LDC","LNC","LDD","LND"] :
        txtDetectionNomdB+="OK"
    else : 
        txtDetectionNomdB+="plage niveau de bruit différente de LDA,LNA,LNU,LDC,LNC,LDD ou LND"
    return txtDetectionNomdB

#fonction qui détecte la présence de champs attributaires
def OutilDetectionNomChampsAttributaires(coucheSig,listeChampsImpose) :
    """
    en entrée 
        coucheSig ---> type QgdVectorLayer
        listeChampsImpose --> type list                             
    en sortie 
        txtDetectionNomChampsAttributaires ---> type str
        numChamps ---> tpe int                             
    """
    #récupération des noms des champs attributaires sous forme de liste
    champsAttributares = coucheSig.pendingFields()
    listeNomsChampsAttributaires=[field.name() for field in champsAttributares]
    #Valeur si on ne trouve pas le champs imposé
    txtDetectionNomChampsAttributaires="pas de champ attributaire correct"
    numChamps=-1
    #pour chaque champs de la couche Sig - vérifier s'il est parmi le nom des champs imposés (id pour isophones et nom pour limites adminsitratives)
    for nomChamps in listeChampsImpose : 
        if nomChamps in listeNomsChampsAttributaires :
            txtDetectionNomChampsAttributaires= "OK"
            numChamps=coucheSig.fieldNameIndex(nomChamps)
            return txtDetectionNomChampsAttributaires,numChamps
    return txtDetectionNomChampsAttributaires,numChamps
    
#fonction de recherche du nom de champs imposé parmi les champs attributaires d'une couche Sig
def OutilDetectionNomChampsAttributairesAssemblageAgregation(coucheSig,listeChampsImpose) :
    """
    en entrée : 
        coucheSig ---> type QgdVectorLayer
        listeChampsImpose --> type list                             
    en sortie : 
        txtDetectionNomChampsAttributaires ---> type str
        numChamps ---> tpe int                             
    """
    #récupération des noms des champs attributaires sous forme de liste
    champsAttributares = coucheSig.pendingFields()
    listeNomsChampsAttributaires=[field.name() for field in champsAttributares]
    #Valeur si on ne trouve pas le champs imposé
    #pour chaque champs de la couche Sig - vérifier s'il est parmi le nom des champs imposés (id pour isophones et nom pour limites adminsitratives)
    for i in range(len(listeChampsImpose)):
        if listeNomsChampsAttributaires[i] != listeChampsImpose[i] :
            txtDetectionNomChampsAttributaires= "pas de champ attributaire correct"
            numChamps=-1
            break
        else : 
            numChamps=coucheSig.fieldNameIndex(listeChampsImpose[i])
            txtDetectionNomChampsAttributaires="OK"
    return txtDetectionNomChampsAttributaires,numChamps

#fonction de recherche des noms des attributs des objets de la couche Sig 
def OutilDetectionValeursAttributaires(coucheSig,numChamps) :
    """
    en entrée 
        coucheSig ---> type QgsVectorLayer
        numChamps ---> type int (résultat de la fonction OutilDetectionNomChampsAttributaires)
    en sortie 
        texte d'erreur ---> type str
    """ 
    #initialisation des textes 
    txtValeursFoireuses=str("")
    txtValeursNickel=str("")
    #cas de numChamps=-1 donc le champ imposé n'est pas trouvé
    if numChamps==-1 : 
        txtValeursFoireuses+=str("impossible de vérifier la valeur attributaire")
        txtValeursNickel+=str("")
    else : 
        #initialisation de la liste qui va sotcker les valeurs qui ne respectent pas les règles de nommage 
        valeursFoireuses=[]
        #initialisation de la liste qui va stocker les valeurs qui respectent les règles de nomma
        valeursNickel=[]
        #pour chaque ojet de la couche Isophone
        for objetIsophone in coucheSig.getFeatures() :
            #on récupère la la valeur attributaire du champs Id ou valmin ou nom en fonction du numero de champs 
            valeurAtt=objetIsophone[numChamps]
            #si il n'y pas de valeur
            if valeurAtt==None:
                valeurAtt="Pas de donnees attributaire"
            #si ce n'est pas du text je le change en texte
            elif not(isinstance(valeurAtt, basestring)):
                valeurAtt = str(int(valeurAtt))
            #cas des CBS 2012                
            if len(valeurAtt) > 2 :
                classedB=valeurAtt[-4:]
                if  classedB in ["LDNU","_LNU"] or (classedB[:2] in ('LD','LN') and classedB[2:] in ('50','55','60','62','65','68','70','71','73','75','80','-8','-5','-2','00','+2','+5','+8')): 
                    valeursNickel.append(valeurAtt)
                else :
                    valeursFoireuses.append(valeurAtt)
            #cas des CBS issues de MithraSIG
            else :               
                classedB=valeurAtt
                if classedB in ('50','55','60','62','65','68','70','71','73','75','80','-8','-5','-2','00','+2','+5','+8'):
                    valeursNickel.append(valeurAtt.encode('utf-8'))
                else :
                    valeursFoireuses.append(valeurAtt.encode('utf-8'))
        if valeursNickel==[]:
            txtValeursNickel+=str("Pas de bonne Valeur, ")
        else : 
            txtValeursNickel+="OK pour les valeurs attributaires "+str(valeursNickel)+'    '
        if valeursFoireuses==[]:
            txtValeursFoireuses+=str("")
        else : 
            txtValeursFoireuses+="Problème de nommage pour la(les) valeur(s) attributaire(s) "+str(valeursFoireuses)+'    '
    txtDetectionValeursAtributaires= txtValeursNickel + txtValeursFoireuses
    return  txtDetectionValeursAtributaires
    
#fonction de détection des erreurs géométriques des isophones - balayage de tous les objets isophones constituant le fichier carte isophones
def OutilDetectionErreursGeometriques(coucheSig,numChamps) :
    """
    en entrée 
        coucheIsophone ---> type QgsVectorLayer
    en sortie
        texte d'erreur ---> type str
    """
    #initialisation du texte
    txtGeomFoireuses=str("")
    txtGeomValides=str("")
    ##cas de numChamps=-1 donc le champ imposé n'est pas trouvé
    if numChamps==-1 :
        txtGeomFoireuses+=str("impossible de vérifier la validité géométrique des isophones")
        txtGeomValides+=str("")
    else : 
        #initialisation des listes de géométries 
        geomFoireuses=[]
        geomValides=[]
        #pour chaque entité dans la coucheIsophone
        for objetIsophone in coucheSig.getFeatures():
            valeurAtt=str(objetIsophone[numChamps])
            geom = objetIsophone.geometry()
            if geom==None:
                #on peut s'intteroger si geom vide est bon ou pas bon
                geomFoireuses.append(valeurAtt.encode('utf-8'))
            elif not(geom.isGeosValid()):
                geomFoireuses.append(valeurAtt.encode('utf-8'))
            else:
                geomValides.append(valeurAtt.encode('utf-8'))
        if geomValides==[] : 
            txtGeomValides+=str("")
        else : 
            txtGeomValides+="OK pour la(les) valeur(s)"+str(geomValides)
        if geomFoireuses==[] : 
            txtGeomFoireuses+=str("")
        else : 
            txtGeomFoireuses+="La géométrie n'est pas valide pour la(les) valeur(s)"+str(geomFoireuses)
    txtDetectionErreursGeom=txtGeomFoireuses+txtGeomValides
    return txtDetectionErreursGeom
	
#fonction qui détecte si les isophones sont des multipolygones
def OutilDetectionAnomaliesGeometriques(coucheSig) :
    """
    en entrée
        coucheSig ---> type QgsVectorLayer
    en sortie
        texte d'erreur ---> type str
    """
    #vérification géométrique : il faut que le format soit polygone ou multi polygone (3ème colonne du fichier "listeErreursIsophones.csv")
    if not(coucheSig.wkbType() in [3,6,3003,3006]):# == QGis.WKBPolygon or coucheSig.wkbType() == QGis.WKBMultiPolygon or coucheSig.wkbType() == 3003) :
    
        txtDetectionAnomalieGeom = "Les objets doivent être des polygones ou multipolygones"
    else:
        txtDetectionAnomalieGeom = 'OK'
    return txtDetectionAnomalieGeom

#fonction qui détect le bon chargement d'une couche SIG
def OutilDetectionChargementCouche(coucheSig) : 
    """ 
    en entrée, coucheSig ---> type QgsVectorLayer
    en sortie, texte d'erreur ---> type str
    """
    #vérification du bon chargement de la couche Isophone
    if not coucheSig.isValid() :
        txtVerifChargement= "La couche n'a pas été chargée"
    else : 
        txtVerifChargement="OK"
    return txtVerifChargement

#fonction de compteur de caracrères 
def OutilCompteur(caractereRecherche, dansQuoi) : 
    """
    en entrée 
        caractereRecherche = le caractère qui est recherché, sur lequel le compteur va se baser pour s'incrémenter ---> type str
        dansQuoi = liste ou chaine de caractère dans laquelle on cherche le caractère ---> type str
    en sortie 
        compteur ---> type int
    """
    #initialisation compteur 
    compteur=0
    #recherche et comptage du du caractère recherché dans le dansQuoi 
    compteur+=dansQuoi.count(caractereRecherche)
    return compteur

#fonction qui permet de mettre l'isophone dans la bonne case
def OutilRechercherValeursdBIsophones(valeurdB,valeursBordsIsophones):
    """
    en entrée
        le niveau en dB et la liste des bords des isophones en dB pour chaque couche ---> type list de str
    en sortie
        le numéro de la liste dans lequel doit se trouver le niveau en dB ---> type int
    """
    #par défaut, numCaseValeurdB fixé à -1 
    numCaseValeurdB=-1
    #numCasValeurdB prend la valeur du numéro de la case dans la liste des valeurs des bords des isophones
    for i in range(len(valeursBordsIsophones)):
        if valeurdB >= valeursBordsIsophones[i][0] and valeurdB <valeursBordsIsophones[i][1]:
            numCaseValeurdB=i
    return numCaseValeurdB

#fonction qui recherche partie d'un nom dans une liste
def OutilRechercheNomDansListe(nom,liste):
    """
    en entrée
        nom = le nom à chercher ---> type str
        liste = liste de nom à chercher ---> type list
    en sortie
        le numéro du nom dans la liste ---> type int
    """
    for i in range(len(liste)):
        if nom in liste[i]:
            return i
    return -1
    
#fonction qui recherche partie d'un nom dans une liste
def OutilVerficationDoublon(listeNomFichierCorrespondance):
    """
    en entrée
        listeNomFichierCorrespondance ---> type list de str
    en sortie
        listeDoublon ---> type list
    """
    listeDoublon=[]
    nb=len(listeNomFichierCorrespondance)
    for m in range(nb):
        for n in range(m+1,nb):
            if listeNomFichierCorrespondance[m]==listeNomFichierCorrespondance[n]:
                listeDoublon.append(listeNomFichierCorrespondance[m])    
    return listeDoublon
