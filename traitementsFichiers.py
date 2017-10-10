# -*- coding: utf-8 -*-

from recuperationDonnees import RecuperationGeometrie
from parametresFonctions import ValeursBordsIsophones
import interfaceUtilisateur
import os
from qgis.core import *
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QCoreApplication
       
###################################################################################################
#FONCTIONS INTERNES A LA FONCTION TraitementGeometrieIsophones()
###################################################################################################
#fonction de découpage des isophones 
def DecoupageIsophonesPardB(listeGeometries):
    """
    en entrée
        listeGeometries= liste de liste de géométries simples regroupées par dB et à découper dans l'orde de 55 à 75 ---> type tuple
    en sortie
        listeGeometriesDiscontinues = cette même liste mais avec des géométries découpées ---> type tuple
    """
    listeGeometriesDiscontinues=[]
    #barre de progression
    progression=interfaceUtilisateur.ProgressBar()
    compteurTotal=0
    for i in range(len(listeGeometries)): # transforme en liste de polygones
        ListeGeom=listeGeometries[i]
        for j in range(i+1,len(listeGeometries)):
            compteurTotal=compteurTotal+(len(ListeGeom)*len(listeGeometries[j]))     
    progression.InitialiserBarreProgressionLocale(compteurTotal, u'Découpage des isophones'+ '\n' + u'étape 3 / 5 du traitement')
    compteur=1
    for i in range(len(listeGeometries)): # transforme en liste de polygones
        ListeGeom=listeGeometries[i]
        for j in range(i+1,len(listeGeometries)):
            ListeGeom,compteur=DecoupageIsophone(ListeGeom,listeGeometries[j],compteur)
            #vérification si l'utilisateur n'as pas demandé l'arret du traitement
            if ListeGeom==1 and compteur==1 :
                return 1
        listeGeometriesDiscontinues.append(ListeGeom)
    progression.close()
    return listeGeometriesDiscontinues

#fonction de regroupement des objets isophones découpés pour n'avoir qu'un seul multipolygone par intervalle de niveau de bruit
def RegroupementIsophonePardB(listeGeometriesDiscontinues):
    """
    en entrée
        listeGeometriesDiscontinues= liste de liste de géométries simples regroupées par dB et découpées ---> type tuple
    en sortie
        listeGeometriesFormatGeostandard= liste de géométries fusionnées par dB dans l'ordre ---> type tuple
    """
    listeGeometriesFormatGeostandard=[] # liste des objets isophones discontinus et regroupés pour n'avoir qu'un seul multipolygone par intervalle de niveau de bruit
    #barre de progression
    progression=interfaceUtilisateur.ProgressBar()
    compteurTotal=0
    for i in range(len(listeGeometriesDiscontinues)): # transforme en liste de polygones
        geomOut= QgsGeometry.fromWkt('GEOMETRYCOLLECTION()')
        for path_geom in listeGeometriesDiscontinues[i]:
            geom=path_geom#listeGeometriesDiscontinues[i][j]
            if geom!=None:
                compteurTotal=compteurTotal+1
    progression.InitialiserBarreProgressionLocale(compteurTotal, u"Regroupement des isophones" + '\n' + u"étape 5 / 5 du traitement")
    compteur=1
    for i in range(len(listeGeometriesDiscontinues)): # transforme en liste de polygones
        geomOut= QgsGeometry.fromWkt('GEOMETRYCOLLECTION()')
        for path_geom in listeGeometriesDiscontinues[i]:
            geom=path_geom#listeGeometriesDiscontinues[i][j]
            if geom!=None:
                #vérification si l'utilisateur n'as pas demandé l'arret du traitement
                if progression.drapeauArretFonctionEnCours==True:
                    return 1
                geomOut = geomOut.combine(geom)
                progression.progressBarLocale.setValue(compteur) #incrementation de la barre de Progression
                QCoreApplication.processEvents()
                compteur=compteur+1
            else:
                print "géométrie vide"
        listeGeometriesFormatGeostandard.append(geomOut)
    #fermeture de la fenêtre de progression
    progression.close()
    return listeGeometriesFormatGeostandard

###################################################################################################
#FONCTION TraitementGeometrieIsophones()
###################################################################################################
def TraitementGeometrieIsophones(urlDossierIsophone,nomdB,typeLigne,typeSource,nomFichierIsophoneAvecExt,urlSigLimiteAdministrative):
    """
    en entrée
        urlDossierIsophone = url donné par l'utilisateur via l'interface qui contient les isophones à mettre au GéoStandard ---> type str
        nomdB (LDA,LNA...) ---> type str
        typeLigne (CONV ou LGV si fer) ---> type str
        typeSource (R ou F) ---> type str
        nomFichierIsophoneAvecExt ---> type str
        urlSigLimiteAdministrative = url du fichier contour départemental issu du dossier "ressources" ---> type str
    en sortie
        listeGeometriesFormatGeostandard = liste de liste des géométries des isophones au format GéoStandard ---> type tuple
        valeursBordsIsophones = liste d'une liste de int (niveau des bords des isophones) ---> type tuple
    """
    #recuperation de la geometrie du dep
    coucheIsophoneDep= QgsVectorLayer(urlSigLimiteAdministrative, "couche Dep", "ogr") #j ouvre le fichier
    for objetIsophoneDep in coucheIsophoneDep.getFeatures() :
        if objetIsophoneDep[0]==nomFichierIsophoneAvecExt[:3] :
            geomDep=TransformeEnListeGeomSimple(objetIsophoneDep.geometry())
    del coucheIsophoneDep,objetIsophoneDep
    if nomdB=='LNU':
        progression=interfaceUtilisateur.ProgressBar()
        coucheIsophone= QgsVectorLayer(urlDossierIsophone+os.sep+nomFichierIsophoneAvecExt, nomFichierIsophoneAvecExt[:-4], "ogr") #j ouvre le fichier
        listeGeometriesLNU=[]
        for objetIsophone in coucheIsophone.getFeatures() :
            #vérification si l'utilisateur n'as pas demandé l'arret du traitement
            if progression.drapeauArretFonctionEnCours==True:
                return 1,1
            listeGeometriesLNU= listeGeometriesLNU + TransformeEnListeGeomSimple(objetIsophone.geometry())
        #barre de progression
        compteurTotal=len(listeGeometriesLNU)            
        progression.InitialiserBarreProgressionLocale(compteurTotal, u'Découpage selon la limite administrative de référence' + '\n' + u'étape 4 / 5 du traitement')
        compteur=1        
        listeGeometriesLNU,compteur=IntersectionGeometrie(listeGeometriesLNU,geomDep,compteur)
        #vérification si l'utilisateur n'as pas demandé l'arret du traitement
        if listeGeometriesLNU==1 and compteur==1 :
            return 1,1
        #regroupement des isophones par tranche de niveau de bruit pour n'avoir qu'un seul multipolygone par intervalle de dB
        listeGeometriesFormatGeostandard=RegroupementIsophonePardB([listeGeometriesLNU])
        #vérification si l'utilisateur n'as pas demandé l'arret du traitement
        if listeGeometriesFormatGeostandard==1 :
            return 1,1
        valeursBordsIsophones=[['00','']]
    else :
        #valeurs des niveaux de bruit qu'on doit retrouver en fonction du nomdB (LDA,LNA, etc)
        valeursBordsIsophones=ValeursBordsIsophones(nomdB,typeLigne,typeSource)
        #récupération des géométries des isophones CBS2012
        listeGeometries=RecuperationGeometrie(urlDossierIsophone,valeursBordsIsophones,nomFichierIsophoneAvecExt)
        #vérification si l'utilisateur n'as pas demandé l'arret du traitement
        if listeGeometries==1 :
            return 1,1
        #découpage des isophones CBS2012 pour avoir des isophones discontinus
        listeGeometriesDiscontinues=DecoupageIsophonesPardB(listeGeometries)
        #vérification si l'utilisateur n'as pas demandé l'arret du traitement
        if listeGeometriesDiscontinues==1 :
            return 1,1
        #informations relatives à l'affichage du contenu de la barre de progression
        progression=interfaceUtilisateur.ProgressBar()
        compteurTotal=0
        for i in range(len(listeGeometriesDiscontinues)):
            compteurTotal=compteurTotal+(len(listeGeometriesDiscontinues[i]))
        progression.InitialiserBarreProgressionLocale(compteurTotal, u'Découpage selon la limite administrative de référence' + '\n' + u'étape 4 / 5 du traitement')
        compteur=1
        #découpage des isophones CBS2012 avec le contour
        for i in range(len(listeGeometriesDiscontinues)):
            listeGeometriesDiscontinues[i],compteur=IntersectionGeometrie(listeGeometriesDiscontinues[i],geomDep,compteur)
            #vérification si l'utilisateur n'as pas demandé l'arret du traitement
            if listeGeometriesDiscontinues[i]==1 and compteur==1 :
                return 1,1 
        #regroupement des isophones par tranche de niveau de bruit pour n'avoir qu'un seul multipolygone par intervalle de dB
        listeGeometriesFormatGeostandard=RegroupementIsophonePardB(listeGeometriesDiscontinues)
        #vérification si l'utilisateur n'as pas demandé l'arret du traitement
        if listeGeometriesFormatGeostandard==1 :
            return 1,1 
    #fermeture de la fenêtre de progression 
    progression.close()
    return listeGeometriesFormatGeostandard,valeursBordsIsophones

#Fonction de découpage qui supprime d'une liste de géométrie les élèments d'une autre lsite de géométrie pour le découpage d'isophone entre elle
def DecoupageIsophone(listeGeometriesIn,listeGeometriesCut,compteurEntre):
    """
    en entrée, 
        listeGeometriesIn = liste de géométries simples regroupées par dB ---> type list
        listeGeometriesCut = liste de géométries simples pour découper ---> type list
        compteurEntre = pour incrémentation de la barre de progression ---> type int
    en sortie
        listeGeometriesOut = cette même liste mais découpée par la deuxième ---> type list
        compteurEntre = pour incrémentation de la barre de progression ---> type int
    """
    listeGeometriesOut=[]
    for geometrieIn in listeGeometriesIn:
        if geometrieIn.area()!=0:
            geom=geometrieIn
            for geometrieCut in listeGeometriesCut:#on découpe pour chaque geometrie
                #vérification si l'utilisateur n'as pas demandé l'arret du traitement
                if interfaceUtilisateur.ProgressBar.drapeauArretFonctionEnCours==True:
                    return(1,1)
                geom=geom.difference(geometrieCut)
                interfaceUtilisateur.ProgressBar.progressBarLocale.setValue(compteurEntre)
                QCoreApplication.processEvents()
                compteurEntre=compteurEntre+1
            listeGeometriesOut.append(geom)
        else:
            print "geom vide"
    return (listeGeometriesOut,compteurEntre)

#Fonction qui coupe une liste de géométrie (isophones) selon une autre liste de géométrie (limite administrative du département dans lequel sont situés les isophones)
def IntersectionGeometrie(listeGeometriesIn,listeGeometriesCut,compteurEntre):
    """
    en entrée
        listeGeometriesIn = liste de géométries simples regroupées par dB ---> type list
        listeGeometriesCut = liste de géométries simples pour découper ---> type list
        compteurEntre = pour incrémentation de la barre de progression ---> type int
    en sortie
        listeGeometriesOut = cette même liste mais découpée par la deuxième ---> type list
        compteurEntre = pour incrémentation de la barre de progression ---> type int
    """
    listeGeometriesOut=[]   
    for geometrieIn in listeGeometriesIn:
        if geometrieIn.area()!=0:
            for geometrieCut in listeGeometriesCut:#on découpe pour chaque geometrie
            
                #vérification si l'utilisateur n'as pas demandé l'arret du traitement
                if interfaceUtilisateur.ProgressBar.drapeauArretFonctionEnCours==True:
                    return(1,1)
                geom=geometrieIn.intersection(geometrieCut)
                interfaceUtilisateur.ProgressBar.progressBarLocale.setValue(compteurEntre)
                QCoreApplication.processEvents()
                compteurEntre=compteurEntre+1
                if geom.area()!=0:
                    listeGeometriesOut.append(geom)
        else:
            print "geom vide"
    return (listeGeometriesOut,compteurEntre)

#Fonction transforme des multipolygones en liste de polygones simples
def TransformeEnListeGeomSimple(geometrieIn):
    """
    en entrée 
        GeometriesIn = une géométrie simples ou multipe ---> type QgsGeometry
    en sortie
        listeGeometriesOut= liste de géométries simples ---> type list de QgsGeometry
    """
    listeGeometriesOut=[]
    try:
        geomOut=geometrieIn.buffer(0,0)
        if geomOut.isMultipart():
            for geom in  geomOut.asMultiPolygon():
                listeGeometriesOut.append(QgsGeometry().fromPolygon(geom))
        else:
            listeGeometriesOut.append(geomOut)
    except :
        print 'PB TransformeEnListeGeomSimple'
    return listeGeometriesOut