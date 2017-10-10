# -*- coding: utf-8 -*-
import os 
from qgis.core import *
from PyQt4.QtCore import *
import recuperationDonnees #from recuperationDonnees import RecuperationTableCorres,ReccuperationDonneesComplem,RecuperationListeFichiersATraiter,RecuperationFormatCBS,RecuperationTypeCBS,RecuperationDonneesInfra,RecuperationCodInfra,RecuperationNatureInfra
#from recuperationDonnees import RecuperationTypeLigneFer
from parametresFonctions import CreationArborescenceDossiersGeostandard



"""
fichier parametres.py contient tous les paramètres fixes à reprendre dans les traitements des fichiers
"""
#################################################################################################################################################################################################
#DONNEES RESSOURCES INTEGREES A MIZOGEO
#################################################################################################################################################################################################
#récupération de l'emplacement du fichier "tableCorrespondanceFer.csv" situé dans le dossier "ressources de Mizogeo
urlTableCorrespondanceFer=os.path.join(os.path.dirname(__file__),'ressources','tableCorrespondanceFer.csv')
#récupération de l'emplacement du fichier "tableCorrespondance.csv" situé dans le dossier "ressources de Mizogeo
urlDonneesComplementaires=os.path.join(os.path.dirname(__file__),'ressources','donneesComplementaires.csv')

#récupération de l'url du fichier Sig de limite admnistrative (interne à Mizogeo - dossier ressources) et du SRID (Spatial Reference ID ou EPSG ID correspondant à un système de projection) associé
def UrlFichierSigLimiteAdministrative(codeDept):
    """
    en entrée
        codeDept = 3 caractères décrivant le code du département ---> type str
    en sortie
        urlFichierSigLimiteAdministrative = url du fichier shp contenant les limites administrives ---> type str
        srid = système de coordonnées liées au fichier des limites administratives ---> type QgsCoordinateReferenceSystem
    """
    if codeDept in ("971","972"):
        urlFichierSigLimiteAdministrative = os.path.join(os.path.dirname(__file__),'ressources','departementGuadeloupeMartinique.shp')
        srid=QgsCoordinateReferenceSystem(32620)
    elif codeDept=="973":
        urlFichierSigLimiteAdministrative = os.path.join(os.path.dirname(__file__),'ressources','departementGuyanne.shp')
        srid=QgsCoordinateReferenceSystem(2972)
    elif codeDept=="974":
        urlFichierSigLimiteAdministrative = os.path.join(os.path.dirname(__file__),'ressources','departementLaReunion.shp')
        srid=QgsCoordinateReferenceSystem(2975)
    elif codeDept=="976":
        urlFichierSigLimiteAdministrative = os.path.join(os.path.dirname(__file__),'ressources','departementMayotte.shp')
        srid=QgsCoordinateReferenceSystem(4471)
    else :
        urlFichierSigLimiteAdministrative = os.path.join(os.path.dirname(__file__),'ressources','departementMetropole.shp')
        srid=QgsCoordinateReferenceSystem(2154)
    return urlFichierSigLimiteAdministrative, srid

#récupération de l'emplacement des fichiers style au format qml situés dans le dossier "ressources de Mizogeo
urlFichierStyleLDA=os.path.join(os.path.dirname(__file__),'ressources','couleursIsophonesLDA.qml')
urlFichierStyleLNA=os.path.join(os.path.dirname(__file__),'ressources','couleursIsophonesLNA.qml')
urlFichierStyleB=os.path.join(os.path.dirname(__file__),'ressources','couleursIsophonesB.qml')
urlFichierStyleLDC=os.path.join(os.path.dirname(__file__),'ressources','couleursIsophonesLDC.qml')
urlFichierStyleLNC=os.path.join(os.path.dirname(__file__),'ressources','couleursIsophonesLNC.qml')
urlFichierStyleD=os.path.join(os.path.dirname(__file__),'ressources','couleursIsophonesD.qml')

#################################################################################################################################################################################################
#DETERMINTAION DES VARIABLES RELATIFS AUX FICHIERS A TRAITER DEDUITES DU NOM DU FICHIER ISOPHONE
#################################################################################################################################################################################################
#variables à rechercher dans les tables attributaires des CBS 
ListeChampsImpose=["Valmin","Val","DB_LO","FROM","Values_Polygon","Id","ID","id","LD","ld","lD"]
"""
Valmin pour mithraV4 et V5
Id,ID,id,LD,ld,lD pour CBS 2012
DB_LO pour CadnaA
FROM pour ????
"""

#################################################################################################################################################################################################
#DETERMINTAION DES VARIABLES RELATIFS AUX FICHIERS A CREER SELON LE GEOSTANDARD
#################################################################################################################################################################################################
#pour tous les fichiers GéoStandard définition de l'encodage
encodage="UTF-8"
#pour tous les fichiers GéoStandard définition du driverName pour l'export (= type de fichier)
driverExport="ESRI Shapefile"
#pour tous les fichiers GéoStandard définition du type de geometrie d'objet exporte
typeGeometrie=QGis.WKBPolygon
#définition des varibales fixes pour échéance 2017 mais à  adapter si évolutions Mizogeo
typeTerr="INFRA"#type de territoire cartographié (à  changer si adaptation Mizogeo aux Agglos)
anneeCbsZbr="2017"#année pour échéance 2017 pour fichier N_BRUIT_CBS et N_BRUIT_ZBR (à  changer si utilisation de Mizogeo pour échéance future)
anneePpbe="2018"#année pour échéance 2017 pour fichier N_BRUIT_PPEBE (à  changer si utilisation de Mizogeo pour échéance future)
typePpbe="INFRA_E_TT"

#pour fichier N_BRUIT_CBS (format dbf) liste des champs attributaires selon le GeoStandard 
champsAttributairesCBS=QgsFields() #variable à  reprendre dans la création du fichier dbf (paramètres d'entrée de la fonction CreationCBSdbf)
champsAttributairesCBS.append(QgsField("IDCBS", QVariant.String, len =64))
champsAttributairesCBS.append(QgsField("UUEID", QVariant.String, len =20))
champsAttributairesCBS.append(QgsField("ANNEE", QVariant.Int, len =4))
champsAttributairesCBS.append(QgsField("CODEDEPT", QVariant.String, len =3))
champsAttributairesCBS.append(QgsField("TYPETERR", QVariant.String, len =5))
champsAttributairesCBS.append(QgsField("AUTCOMCBS", QVariant.Int, len =9))
champsAttributairesCBS.append(QgsField("PRODUCTEUR", QVariant.Int, len =9))
champsAttributairesCBS.append(QgsField("CODINFRA", QVariant.String, len =32))
champsAttributairesCBS.append(QgsField("TYPESOURCE", QVariant.String, len =1))
champsAttributairesCBS.append(QgsField("NOMCARTE", QVariant.String, len =254))
champsAttributairesCBS.append(QgsField("URI", QVariant.String, len =254))
champsAttributairesCBS.append(QgsField("ETATDOC", QVariant.String, len =2))
champsAttributairesCBS.append(QgsField("DATEARRETE", QVariant.String, len =10))
champsAttributairesCBS.append(QgsField("CBSTYPE", QVariant.String, len =1))
champsAttributairesCBS.append(QgsField("INDICETYPE", QVariant.String, len =2))
champsAttributairesCBS.append(QgsField("AUTCOMPPBE", QVariant.Int, len =9))
champsAttributairesCBS.append(QgsField("IDPPBE", QVariant.String, len =64))
champsAttributairesCBS.append(QgsField("VALIDEDEB", QVariant.String, len =10))
champsAttributairesCBS.append(QgsField("VALIDEFIN", QVariant.String, len =10))
    
#pour fichier N_BRUIT_ZBR (format shp) liste des champs attributaires selon le GeoStandard
champsAttributairesZBR=QgsFields()
champsAttributairesZBR.append(QgsField("IDZONBRUIT", QVariant.String, len =64))
champsAttributairesZBR.append(QgsField("IDCBS", QVariant.String, len =64))
champsAttributairesZBR.append(QgsField("UUEID", QVariant.String, len =20))
champsAttributairesZBR.append(QgsField("ANNEE", QVariant.Int, len =4))
champsAttributairesZBR.append(QgsField("CODEDEPT", QVariant.String, len =3))
champsAttributairesZBR.append(QgsField("TYPETERR", QVariant.String, len =5))
champsAttributairesZBR.append(QgsField("PRODUCTEUR", QVariant.Int, len =9))
champsAttributairesZBR.append(QgsField("CODINFRA", QVariant.String, len =32))
champsAttributairesZBR.append(QgsField("TYPESOURCE", QVariant.String, len =1))
champsAttributairesZBR.append(QgsField("CBSTYPE", QVariant.String, len =1))
champsAttributairesZBR.append(QgsField("ZONEDEF", QVariant.String, len =2))
champsAttributairesZBR.append(QgsField("LEGENDE", QVariant.String, len =2))
champsAttributairesZBR.append(QgsField("INDICETYPE", QVariant.String, len =2))
champsAttributairesZBR.append(QgsField("VALIDEDEB", QVariant.String, len =10))
champsAttributairesZBR.append(QgsField("VALIDEFIN", QVariant.String, len =10))

#pour fichier N_BRUIT_PPBE (format shp) liste des champs attributaires selon le GeoStandard 
champsAttributairesPPBE=QgsFields()
champsAttributairesPPBE.append(QgsField("IDPPBE", QVariant.String, len =64))
champsAttributairesPPBE.append(QgsField("ANNEE", QVariant.Int, len =4))
champsAttributairesPPBE.append(QgsField("CODEDEPT", QVariant.Int, len =3))
champsAttributairesPPBE.append(QgsField("TYPETERR", QVariant.String, len =5))
champsAttributairesPPBE.append(QgsField("TYPEPPBE", QVariant.String, len =10))
champsAttributairesPPBE.append(QgsField("AUTCOMPPBE", QVariant.String, len =9))
champsAttributairesPPBE.append(QgsField("PRODUCTEUR", QVariant.Int, len =9))
champsAttributairesPPBE.append(QgsField("NOMPPBE", QVariant.String, len =254))
champsAttributairesPPBE.append(QgsField("URI", QVariant.String, len =254))
champsAttributairesPPBE.append(QgsField("ETATDOC", QVariant.String, len =2))
champsAttributairesPPBE.append(QgsField("DATEARRETE", QVariant.String, len =10))
champsAttributairesPPBE.append(QgsField("VALIDEDEB", QVariant.String, len =10))
champsAttributairesPPBE.append(QgsField("VALIDEFIN", QVariant.String, len =10))