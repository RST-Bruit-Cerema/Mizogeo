# -*- coding: utf-8 -*-
"""
Module comportant les classes et methodes necessaires à l'interface utilisateur
"""

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from qgis.core import *
import sys
import glob
import inspect, os, subprocess, csv
import _winreg as winreg
from creationFichiersGeostandard import CreationZbrCbs, CreationPPBEshp,CreationAgregation,CreationAssemblage
#import traitementsFichiers
import fenetre_menu_ZBR_CBS_Ui, fenetre_menu_PPBE_Ui, fenetre_menu_Agregation_Ui, fenetre_menu_Assemblage_Ui
from verificationDonnees import VerificationDepartementPpbe

################Definition des icones#####################################################
iconSearch=QtGui.QIcon()
iconSearch.addPixmap(QtGui.QPixmap(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icones', "iconSearch.png")))
iconOk= QtGui.QIcon()#creer les icones 
iconOk.addPixmap(QtGui.QPixmap(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icones', "iconOk.png")))
iconPasOk = QtGui.QIcon()
iconPasOk.addPixmap(QtGui.QPixmap(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icones',"iconPasOk.png")))
iconAttention=QtGui.QPixmap(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icones',"iconMessageRouge.png"))
###########################################################################################

################definition des variables globales de sauvegarde des chemin ################
cheminChoixIso=''#initialisation de la variable de memorisation du chemin
cheminChoixCorrespondance=''
cheminChoixVoieNouvelle=''
cheminChoixSortie=''
cheminChoixProducteur=''
cheminChoixDbf=''
cheminChoixPerimetre=''
cheminChoixZbr=''
###########################################################################################

def ArretForce():
    msg = QMessageBox()
    horizontalSpacer = QtGui.QSpacerItem(800, 0, 0, 0)
    msg.setFixedSize(800,400)
    layout=msg.layout()
    layout.addItem(horizontalSpacer, layout.rowCount(), 0, 1, layout.columnCount())
    msg.setWindowTitle("Avertissement")
    msg.setIconPixmap(iconAttention)
    msg.setText("Attention" + '\n' + '\n' + u"Vous allez arrêter le traitement en cours de Mizogeo !" +'\n' + '\n' + u"Etes-vous sûr de vouloir stopper le traitement ?")
    font = QtGui.QFont()
    font.setFamily("Calibri Light")
    font.setPointSize(11)
    font.setBold(False)
    font.setItalic(False)
    font.setWeight(40)
    msg.setFont(font)
    msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    toto=msg.exec_()
    if toto==QtGui.QMessageBox.Yes:
	    ProgressBar.drapeauArretFonctionEnCours=True
    elif toto==QtGui.QMessageBox.No:
        return
    
class MethodesPartagees():
    """Classe regroupant les methodes appelees par les instances d'au moins 1 des 4 fenêtres secondaires de Mizogeo"""
    def EcouterMusiqueRads2011(self) :
        urlMp3=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bonus','MizogeoSong.mp3')
        subprocess.Popen([urlMp3],shell=True).wait() 
    def MemoriserCheminIsophone(self):
        global cheminChoixIso
        cheminChoixIso=self.line_isophone.text()
    def MemoriserCheminCorrespondance(self):
        global cheminChoixCorrespondance
        cheminChoixCorrespondance=self.line_CorrespondanceVc.text()
    def MemoriserCheminVoieNouvelle(self):
        global cheminChoixVoieNouvelle
        cheminChoixVoieNouvelle=self.line_VoiesNouvelles.text()
    def MemoriserCheminSortie(self):
        global cheminChoixSortie
        cheminChoixSortie=self.line_Sortie.text()
    def MemoriserProducteur(self):
        global cheminChoixProducteur
        cheminChoixProducteur=self.line_Producteur.text()
    def MemoriserCheminDbf(self):
        global cheminChoixDbf
        cheminChoixDbf=self.line_Dbf.text()
    def MemoriserCheminZbr(self):
        global cheminChoixZbr
        cheminChoixZbr=self.line_Zbr.text()
    def MemoriserCheminPerimetre(self):
        global cheminChoixPerimetre
        cheminChoixPerimetre=self.line_perimetre.text()
    def MettreAJourIcone(self):
        envoyeur=self.sender()#recuperer le widget emettant le signal
        if envoyeur.text()!="" : 
            if envoyeur.objectName()=='line_isophone':
                self.Btn_ChoixIsophones.setStyleSheet('QToolButton {background-color: #A5D50C}')
                self.Btn_ChoixIsophones.setIcon(iconOk)
            elif envoyeur.objectName()=='line_CorrespondanceVc' :
                self.Btn_ChoixCorrespondanceVc.setStyleSheet('QToolButton {background-color: #A5D50C}')
                self.Btn_ChoixCorrespondanceVc.setIcon(iconOk)
            elif envoyeur.objectName()=='line_Zbr' :
                self.Btn_Zbr.setStyleSheet('QToolButton {background-color: #A5D50C}')
                self.Btn_Zbr.setIcon(iconOk)
            elif envoyeur.objectName()=='line_perimetre' :
                self.Btn_perimetre.setStyleSheet('QToolButton {background-color: #A5D50C}')
                self.Btn_perimetre.setIcon(iconOk)
            elif envoyeur.objectName()=='line_Dbf' :
                self.Btn_dbf.setStyleSheet('QToolButton {background-color: #A5D50C}')
                self.Btn_dbf.setIcon(iconOk)
            elif envoyeur.objectName()=='line_VoiesNouvelles':
                self.Btn_VoiesNouvelles.setStyleSheet('QToolButton {background-color: #A5D50C}')
                self.Btn_VoiesNouvelles.setIcon(iconOk)
            else : 
                self.Btn_ChoixSortie.setStyleSheet('QToolButton {background-color: #A5D50C}')
                self.Btn_ChoixSortie.setIcon(iconOk)
        else:
            if envoyeur.objectName()=='line_isophone':
                self.Btn_ChoixIsophones.setStyleSheet('QToolButton {background-color: #FF0000}')
                self.Btn_ChoixIsophones.setIcon(iconPasOk)
            elif envoyeur.objectName()=='line_CorrespondanceVc' :
                self.Btn_ChoixCorrespondanceVc.setStyleSheet('QToolButton {background-color: #FF0000}')
                self.Btn_ChoixCorrespondanceVc.setIcon(iconPasOk)
            elif envoyeur.objectName()=='line_Zbr' :
                self.Btn_Zbr.setStyleSheet('QToolButton {background-color: #FF0000}')
                self.Btn_Zbr.setIcon(iconPasOk)
            elif envoyeur.objectName()=='line_perimetre' :
                self.Btn_perimetre.setStyleSheet('QToolButton {background-color: #FF0000}')
                self.Btn_perimetre.setIcon(iconPasOk)
            elif envoyeur.objectName()=='line_Dbf' :
                self.Btn_dbf.setStyleSheet('QToolButton {background-color: #FF0000}')
                self.Btn_dbf.setIcon(iconPasOk)
            elif envoyeur.objectName()=='line_VoiesNouvelles' :
                self.Btn_VoiesNouvelles.setStyleSheet('QToolButton {background-color: #FF0000}')
                self.Btn_VoiesNouvelles.setIcon(iconPasOk)
            else :
                self.Btn_ChoixSortie.setStyleSheet('QToolButton {background-color: #FF0000}')
                self.Btn_ChoixSortie.setIcon(iconPasOk)
    def VerifValiditeProducteur(self):
        """
        vérifier que le Qlineedit servant à decrire le producteur contient bien 9 characteres
        """
        envoyeur=self.sender()
        if envoyeur.text()!="" and len(envoyeur.text())!=9 :
            envoyeur.setStyleSheet('QLineEdit {background-color: #FF0000}')
        else : 
            envoyeur.setStyleSheet('QLineEdit {background-color: #A5D50C}')
    def VerifSeparateurCsv(self,fichier):
        """
        Pour controler le separateur des fichiers csv renseignes par les utilisateurs (correspondance voie et voie nouvelles)
        en entree nom du fichier ---> type str
        """
        with open(fichier) as csvfile:
            dialect = csv.Sniffer().sniff(csvfile.read())
            separateur=dialect.delimiter
        return separateur
    def TrouverFichierAide(self):
        """
        pour recuperer l'url du fichier d'aide.pdf
        localisation du fichier : dans le repertoire ressources à la racine du dossier du plugin
        nom du fichier : Aide.pdf
        en sortie, url du fichier aideMizogeo.df ---> type str
        """
        urlFichierAide= os.path.join(os.path.dirname(__file__),'ressources','aideMizogeo.pdf')  
        return urlFichierAide
    def OuvrirAide(self,page):#methode d'ouverture du fichier d'aide
        """
        ouverture du fichier pdf d'Aide de Mizogeo
        en entre : page est un entier
        """
        urlAide=self.TrouverFichierAide()#obtenir l'url du fichier d'aide
        urlAcrobatReaderBrut = winreg.QueryValue(winreg.HKEY_CLASSES_ROOT,'Software\\Adobe\\Acrobat\Exe') #pour trouver le path de adobe reader peu importe la version(le chemin comporte "' au debut)
        urlAcrobatReaderModifie=urlAcrobatReaderBrut.replace('\"',"")#pour remplacer le "' du debut et fin par '
        subprocess.Popen([urlAcrobatReaderModifie, "/A", "page="+str(page),urlAide],shell=True)#pour ouvrir le pdf à la page souhaitee #le module subprocess permet d'acceder a d'autre processus de l'os   
    def ChoixIsophone(self): #methode d'appel de la boite de dialogue et remplissage de la ligne de texte pour le choix du dossier contenant les isophones
        """
        Boite de dialogue permettant le choix du dossier contenant les isophones en entree de Mizogeo
        transfert du path de ce dossier dans un widget Qlineedit
        """
        isophones= QtGui.QFileDialog.getExistingDirectory(self,u"Sélectionner le dossier contenant les isophones",cheminChoixIso) #recuperation du chemin du dossier via fenetre contextuelle et choix utilisateur
        self.line_isophone.setText(isophones) #repercussion du nom du dossier dans objet qlineedit     
    def ChoixSortie(self):#methode d'appel de la boite de dialogue et remplissage de la ligne de texte pour le choix du dossier de sortie
        """
        Boite de dialogue permettant le choix du dossier de sortie des isophones convertis au format GeoStandard
        transfert du path de ce dossier dans un widget Qlineedit
        """
        sortie= QtGui.QFileDialog.getExistingDirectory(self,u"Sélectionner le dossier dans lequel seront stockés les fichiers au format GéoStandard","c:/") #recuperation du chemin du dossier via fenetre contextuelle
        self.line_Sortie.setText(sortie)

    def ChoixZbr(self): #methode d'appel de la boite de dialogue et remplissage de la ligne de texte pour le choix du dossier contenant les fichier N_BRUIT_ZBR
        """
        Boite de dialogue permettant le choix du dossier contenant les fichiers N_BRUIT_ZBR necessaire à l'agregation. format des fichiers : .Shp
        transfert du path de ce dossier dans un widget Qlineedit
        """
        zbr= QtGui.QFileDialog.getExistingDirectory(self,u"Sélectionner le dossier contenant les fichiers N_BRUIT_ZBR","c:/") #recuperation du chemin du dossier via fenetre contextuelle et choix utilisateur
        self.line_Zbr.setText(zbr) #repercussion du nom du dossier dans objet qlineedit
    def ChoixPerimetre(self):#methode d'appel de la boite de dialogue et remplissage de la ligne de texte pour le choix du fichier de perimetre d'agregation
        """
        Boite de dialogue permettant le choix du fichier allant delimiter les fichiers N_BRUIT_ZBR necessaire à l'agregation. format du fichier : .Shp
        transfert du path de ce dossier dans un widget Qlineedit
        """
        perimetre=QtGui.QFileDialog.getOpenFileName(self,u"Sélectionner le fichier SIG contenant le périmètre d'agrégation","C:/","ESRI Shapefile (*.shp)") #recuperation du chemin du fichier via fenetre contextuelle et choix utilisateur, le fichier doit etre de type .shp
        self.line_perimetre.setText(perimetre)
    def ChoixDbf(self):#methode d'appel de la boite de dialogue et remplissage de la ligne de texte pour le choix du dossier contenant les fichier dbf pour la concatenation
        """
        Boite de dialogue permettant le choix du dossier contenant les N_BRUIT_ZBR et/ou N_BRUIT_CBS necessaires à la concatenation. format du fichier : .dbf
        transfert du path de ce dossier dans un widget Qlineedit
        """
        dbf=QtGui.QFileDialog.getExistingDirectory(self,u"Sélectionner le dossier contenant les fichiers .dbf à assembler","c:/") #recuperation du fichier de donnees complementaire, en positionant la fenetre d'appel sur le fichier qui devrait exister
        self.line_Dbf.setText(dbf)
    def ChoixCorrespondanceVc(self):
        """
        Boite de dialogue permettant le choix du fichier contenant le tableur de Correspondance nom de fichier SIG <-> nom de rapportage pour les VC. format du fichier : .csv
        transfert du path de ce dossier dans un widget Qlineedit
        """
        urlTableCorrespondanceVc=os.path.join(os.path.dirname(__file__),'ressources','TableCorrespondanceNomSIG.csv')
        correspondanceVc=QtGui.QFileDialog.getOpenFileName(self,"Sélectionner le fichier contenant le fichier de correspondance nom SIG - nom rapportage UE","c:/","Comma Separated Value (*.csv)")
        self.line_CorrespondanceVc.setText(correspondanceVc)    
    def ChoixVoiesNouvelles(self):
        """
        Boite de dialogue permettant le choix du fichier contenant le tableur de Correspondance nom de fichier SIG <-> nom de rapportage pour les VC. format du fichier : .csv
        transfert du path de ce dossier dans un widget Qlineedit
        """
        VoiesNouvelles=QtGui.QFileDialog.getOpenFileName(self,"Sélectionner le fichier contenant le fichier .csv de recensement des voies nouvelles","c:/","Comma Separated Value (*.csv)")
        self.line_VoiesNouvelles.setText(VoiesNouvelles)
    def CreationListeDepartement(self):
        """
        lister les valeurs des departements contenus dans les fichiers departement*.shp du dossier ressource
        """
        listeFichiersDepartement=['departementMetropole.shp','departementMayotte.shp','departementLaReunion.shp','departementGuyanne.shp','departementGuadeloupeMartinique.shp']
        listeDepartement=[]#initialisation de la liste des departement
        for fichier in listeFichiersDepartement :
            transparent = QgsVectorLayer(os.path.join(os.path.dirname(__file__),'ressources',fichier), fichier, "ogr")
            listeFeatures=transparent.getFeatures()
            for feature in listeFeatures :
                listeDepartement.append(feature[0]+'   '+feature[1])
        listeDepartement.sort()
        return listeDepartement
    def ChoixDepartementPpbe(self):
        """
        indiquer les departement retenus pour la creation des Ppbe dans un widget de type linedit pour faciliter la visu
        """
        departementSelectionne=self.listWidget_departementPpbe.selectedItems()#recuperer les objets selectionnes dans le widget
        listedepartementSelectionne=[]#initialiser la liste
        for departement in departementSelectionne : #parcourir la liste
            listedepartementSelectionne.append(departement.text()[:3])#extrire le texte des objkets du widget
        texteListedepartementSelectionne=','.join(listedepartementSelectionne)#convertir la liste en string 
        self.line_DepartementPpbe.setText(texteListedepartementSelectionne)#inserer le resultat dans le widget d'affichage
    def MessageErreurFichierNonSelectionne(self):
        """
        fonction de creation de la boite d'affichage appelee lorsque tout les parametres d'une fenetre ne sont pas renseignes
        """
        fenetreErreurFichierNonSelectionne=QMessageBox()
        font = QtGui.QFont()
        font.setFamily("Calibri Light")
        font.setPointSize(11)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(40)
        horizontalSpacer = QtGui.QSpacerItem(700, 0, 0, 0)
        fenetreErreurFichierNonSelectionne.setFixedSize(700,400)
        layout=fenetreErreurFichierNonSelectionne.layout()
        layout.addItem(horizontalSpacer, layout.rowCount(), 0, 1, layout.columnCount())
        fenetreErreurFichierNonSelectionne.setFont(font)
        fenetreErreurFichierNonSelectionne.setIconPixmap(iconAttention)
        fenetreErreurFichierNonSelectionne.setWindowTitle("Avertissement")
        fenetreErreurFichierNonSelectionne.setText("Attention" + '\n'+  '\n'+u"Les données obligatoires demandées par Mizogeo ne sont pas renseignées" +'\n'+ '\n'+u"Veuillez les compléter")
        fenetreErreurFichierNonSelectionne.exec_()
    def MessageFinTraitement(self,indicateurFichierNonConforme, urlSortie,classeTraitement,messageText,nomFichier):
        """
        Affiche une fenetre d'avertissement precisant que des erreurs ont ete detectees
        Arrete l'execution de la fonction de traitement des donnees
        @param IndicateurErreurGeometrie : traduit s'il y a eu des erreurs geometriques decelees dans les transparents cibles de la fonction de traitement 
        @type IndicateurErreurGeometrie : booleen True=il y a un erreur False=pas d'erreur
        @param urlSortie : chemin du dossier contenant les donnees de sortie 
        @type IndicateurErreurGeometrie : text
        @param classeTraitement : type de traitement parmi les 4 possibles : Creation Zbr et Cbs, Ppbe etc... 
        @type classeTraitement : text
        """
        if indicateurFichierNonConforme==1:
            urlFichierSortie=os.path.join(urlSortie,nomFichier)
            messageFichierSortie=u'Se reporter au fichier '+urlFichierSortie+"\n"+"\n"+u'Veuillez corriger les erreurs'
            fenetreMessageErreurGeometrie=QMessageBox()
            horizontalSpacer = QtGui.QSpacerItem(1000, 0, 0, 0)
            layout=fenetreMessageErreurGeometrie.layout()
            layout.addItem(horizontalSpacer, layout.rowCount(), 0, 1, layout.columnCount())
            fenetreMessageErreurGeometrie.setIconPixmap(QPixmap(os.path.join(os.path.dirname(os.path.abspath(__file__)),'icones', "iconMessageRouge.png")))
            fenetreMessageErreurGeometrie.setText(messageText)
            font = QtGui.QFont()
            font.setFamily("Calibri Light")
            font.setPointSize(11)
            font.setBold(False)
            font.setItalic(False)
            font.setWeight(40)
            fenetreMessageErreurGeometrie.setFont(font)
            fenetreMessageErreurGeometrie.setInformativeText(messageFichierSortie)
            fenetreMessageErreurGeometrie.setWindowTitle(classeTraitement+u' - erreurs détectées dans le(s) fichier(s)')
            boutonOuvrirCsv=fenetreMessageErreurGeometrie.addButton("Ouvrir CSV", QMessageBox.ActionRole)
            fenetreMessageErreurGeometrie.setStandardButtons(QMessageBox.Ok | QMessageBox.Help)
            retourFenetre=fenetreMessageErreurGeometrie.exec_()
            if fenetreMessageErreurGeometrie.clickedButton()==boutonOuvrirCsv:
                subprocess.Popen([urlFichierSortie],shell=True)
            elif retourFenetre==QMessageBox.Help:
                self.OuvrirAide(3) 
            elif retourFenetre==QMessageBox.Ok :
                fenetreMessageErreurGeometrie.close()
        elif indicateurFichierNonConforme==0:
            messageArret=QMessageBox()
            horizontalSpacer = QtGui.QSpacerItem(800, 0, 0, 0)
            messageArret.setFixedSize(800,300)
            layout=messageArret.layout()
            layout.addItem(horizontalSpacer, layout.rowCount(), 0, 1, layout.columnCount())
            messageArret.setWindowTitle(classeTraitement + u' - fin de traitement')
            font = QtGui.QFont()
            font.setFamily("Calibri Light")
            font.setPointSize(11)
            font.setBold(False)
            font.setItalic(False)
            font.setWeight(40)
            messageArret.setFont(font)
            messageArret.setIconPixmap(QPixmap(os.path.join(os.path.dirname(os.path.abspath(__file__)),'icones',"iconMessageVert.png")))
            messageArret.setText(messageText +'\n')
            messageArret.setInformativeText(u'Fichiers créés dans le dossier suivant : ' +'\n'+ urlSortie)
            messageArret.exec_()
        elif indicateurFichierNonConforme==3:
            urlFichiersSortie=urlSortie.split(' et le fichier ')
            messageFichierSortie=u'Se reporter au fichier '+urlSortie+"\n"+"\n"+u'Veuillez modifier le séparateur en point-virgule'
            fenetreMessageErreurGeometrie=QMessageBox()
            horizontalSpacer = QtGui.QSpacerItem(1000, 0, 0, 0)
            layout=fenetreMessageErreurGeometrie.layout()
            layout.addItem(horizontalSpacer, layout.rowCount(), 0, 1, layout.columnCount())
            fenetreMessageErreurGeometrie.setIconPixmap(QPixmap(os.path.join(os.path.dirname(os.path.abspath(__file__)),'icones', "iconMessageRouge.png")))
            fenetreMessageErreurGeometrie.setText(messageText)
            font = QtGui.QFont()
            font.setFamily("Calibri Light")
            font.setPointSize(11)
            font.setBold(False)
            font.setItalic(False)
            font.setWeight(40)
            fenetreMessageErreurGeometrie.setFont(font)
            fenetreMessageErreurGeometrie.setInformativeText(messageFichierSortie)
            fenetreMessageErreurGeometrie.setWindowTitle(classeTraitement+u' - erreurs détectées dans le(s) fichier(s)')
            boutonOuvrirCsv=fenetreMessageErreurGeometrie.addButton("Ouvrir CSV", QMessageBox.ActionRole)
            fenetreMessageErreurGeometrie.setStandardButtons(QMessageBox.Ok | QMessageBox.Help)
            retourFenetre=fenetreMessageErreurGeometrie.exec_()
            if fenetreMessageErreurGeometrie.clickedButton()==boutonOuvrirCsv:
                for fichiers in urlFichiersSortie:
                    subprocess.Popen([fichiers],shell=True)
            elif retourFenetre==QMessageBox.Help:
                urlAide=self.TrouverFichierAide()#obtenir l'url du fichier d'aide
                urlAcrobatReaderBrut = winreg.QueryValue(winreg.HKEY_CLASSES_ROOT,'Software\\Adobe\\Acrobat\Exe') #pour trouver le path de adobe reader peu importe la version(le chemin comporte "' au debut)
                urlAcrobatReaderModifie=urlAcrobatReaderBrut.replace('\"',"")#pour remplacer le "' du debut et fin par '
                subprocess.Popen([urlAcrobatReaderModifie, "/A", "page=3",urlAide],shell=True)#pour ouvrir le pdf à la page souhaitee
            elif retourFenetre==QMessageBox.Ok :
                fenetreMessageErreurGeometrie.close()
        elif indicateurFichierNonConforme==4 :
            messageArret=QMessageBox()
            horizontalSpacer = QtGui.QSpacerItem(800, 0, 0, 0)
            messageArret.setFixedSize(800,300)
            layout=messageArret.layout()
            layout.addItem(horizontalSpacer, layout.rowCount(), 0, 1, layout.columnCount())
            messageArret.setWindowTitle(classeTraitement + u' - département(s) non valide(s)')
            font = QtGui.QFont()
            font.setFamily("Calibri Light")
            font.setPointSize(11)
            font.setBold(False)
            font.setItalic(False)
            font.setWeight(40)
            messageArret.setFont(font)
            messageArret.setIconPixmap(QPixmap(os.path.join(os.path.dirname(os.path.abspath(__file__)),'icones', "iconMessageRouge.png")))
            messageArret.setText(messageText +'\n')
            messageArret.setInformativeText(urlSortie)
            messageArret.exec_()
        elif indicateurFichierNonConforme==5 :
            messageArret=QMessageBox()
            horizontalSpacer = QtGui.QSpacerItem(800, 0, 0, 0)
            #messageArret.setFixedSize(800,300)
            layout=messageArret.layout()
            layout.addItem(horizontalSpacer, layout.rowCount(), 0, 1, layout.columnCount())
            messageArret.setWindowTitle(classeTraitement)
            font = QtGui.QFont()
            font.setFamily("Calibri Light")
            font.setPointSize(11)
            font.setBold(False)
            font.setItalic(False)
            font.setWeight(40)
            messageArret.setFont(font)
            messageArret.setIconPixmap(QPixmap(os.path.join(os.path.dirname(os.path.abspath(__file__)),'icones', "iconMessageRouge.png")))
            #messageArret.setText("redondance de voies dans le fichier de correspondance et le fichier de voies nouvelles"+'\n')
            messageArret.setInformativeText(messageText)
            messageArret.exec_()
        else:
            messageArret=QMessageBox()
            horizontalSpacer = QtGui.QSpacerItem(800, 0, 0, 0)
            messageArret.setFixedSize(800,300)
            layout=messageArret.layout()
            layout.addItem(horizontalSpacer, layout.rowCount(), 0, 1, layout.columnCount())
            messageArret.setWindowTitle(classeTraitement + u" - fin de traitement sur demande de l'utilisateur")
            font = QtGui.QFont()
            font.setFamily("Calibri Light")
            font.setPointSize(11)
            font.setBold(False)
            font.setItalic(False)
            font.setWeight(40)
            messageArret.setFont(font)
            messageArret.setIconPixmap(QPixmap(os.path.join(os.path.dirname(os.path.abspath(__file__)),'icones', "iconMessageRouge.png")))
            messageArret.setText(messageText +'\n')
            messageArret.setInformativeText(u'Fichiers créés dans le dossier suivant : ' +'\n'+ urlSortie)
            messageArret.exec_()    
    def DisponibiliteChoixPerimetre(self):
        envoyeur=self.sender()
        if envoyeur.objectName()=='line_DepartementPpbe' and envoyeur.text()!="":
            self.groupBox_perimetre.setDisabled(True)
            self.Btn_perimetre.setStyleSheet('QToolButton {background-color: #9D9D9D}')
        elif envoyeur.objectName()=='line_perimetre' and envoyeur.text()!="":
            self.groupBox_administratif.setDisabled(True)
        elif envoyeur.objectName()=='line_DepartementPpbe' and envoyeur.text()=="":
            self.groupBox_perimetre.setDisabled(False)
        elif envoyeur.objectName()=='line_perimetre' and envoyeur.text()=="":
            self.groupBox_administratif.setDisabled(False)
        
class ProgressBar(QtGui.QWidget):# La classe ProgressBar n'est pas issue d'un fichier Ui afin de ne pas presenter de methode __init__ (ce qui creerai des attributs d'instance, or les instances ne sont pas ouvrable dans une fonction puis rappelable dans une autre)
    """
    Classe permettant l'affichage des barres de progression
    les elements des barres de progression sont des attributs de classe pour pouvoir etre appeles depuis differentes fonctions et renvoyer toujours a la meme fenetre
    """
    fenetreProgression=QtGui.QWidget() #définition de la fenetre allant abriter les objets labels et barres de progression
    fenetreProgression.setWindowModality(QtCore.Qt.WindowModal)
    fenetreProgression.setWindowTitle(u'Mizogeo - progression du traitement')
    miseEnPage = QtGui.QVBoxLayout(fenetreProgression) #peremt une mise en page automatique des objets qui y seront inseres
    miseEnPageH1=QtGui.QHBoxLayout()
    miseEnPageH1.setSpacing(30)
    miseEnPageH1.setContentsMargins(50, 20, 500, 0)
    #miseEnPageH1.setSizeConstraint (500)
    miseEnPageH2=QtGui.QHBoxLayout()
    miseEnPageH2.setSpacing(30)
    miseEnPageH2.setContentsMargins(50, 50, 500, 0)
    miseEnPageH3=QtGui.QHBoxLayout()
    miseEnPageH3.setSpacing(30)
    miseEnPageH3.setContentsMargins(70, 20, 150, 0)
    iconeFichier=QtGui.QLabel()
    iconFichier=QtGui.QPixmap(os.path.join(os.path.dirname(os.path.abspath(__file__)),'icones',"iconFichier.png"))
    iconeFichier.setPixmap(iconFichier)
    iconeTraitement=QtGui.QLabel()
    iconTraitement=QtGui.QPixmap(os.path.join(os.path.dirname(os.path.abspath(__file__)),'icones',"iconTraitement.png"))
    iconeTraitement.setPixmap(iconTraitement)
    labelNomEtape = QtGui.QLabel()
    labelNomEtape.setMinimumSize(QtCore.QSize(500, 130))
    labelNomEtape.setText(u'En attente')
    font = QtGui.QFont()
    font.setFamily("Calibri Light")
    font.setPointSize(11)
    font.setBold(False)
    font.setItalic(False)
    font.setWeight(40)
    labelNomEtape.setFont(font)
    #definition du label de titre de la barre de progresion locale par transparent
    labelCoucheATraiter = QtGui.QLabel()
    labelCoucheATraiter.setMinimumSize(QtCore.QSize(500, 130))
    labelCoucheATraiter.setText(u'Initialisation')
    labelCoucheATraiter.setFont(font)
    boutonArret=QtGui.QPushButton()
    boutonArret.setMinimumSize(QtCore.QSize(80, 30))
    boutonArret.setMaximumSize(QtCore.QSize(80, 30))
    boutonArret.setText(u'Arrêt forcé')
    boutonArret.clicked.connect(ArretForce)
    #progressBarLocale = QtGui.QProgressBar(fenetreProgression)#definition de la barre de progression du fichier en cours
    progressBarLocale = QtGui.QProgressBar()
    progressBarLocale.setInvertedAppearance(False)
    styleProgressBarLocale="""QProgressBar{border: 2px solid grey ;border-radius: 5px;text-align: center;font: bold 15px ;padding: 2px}
    QProgressBar::chunk {
    background-color: #2887A6;
    width: 10px;
    margin: 1px;}
    """
    progressBarLocale.setStyleSheet(styleProgressBarLocale)
    miseEnPageH1.addWidget(iconeFichier)
    miseEnPageH1.addSpacerItem(QSpacerItem(30,1))
    miseEnPageH1.addWidget(labelCoucheATraiter)
    miseEnPageH2.addWidget(iconeTraitement)
    miseEnPageH2.addSpacerItem(QSpacerItem(30,1))
    miseEnPageH2.addWidget(labelNomEtape)
    miseEnPageH3.addSpacerItem(QSpacerItem(100,20))
    miseEnPageH3.addWidget(progressBarLocale)
    miseEnPageH3.addSpacerItem(QSpacerItem(30,1))
    #miseEnPageH4.addSpacerItem(QSpacerItem(10,0))
    miseEnPage.addLayout(miseEnPageH1)
    miseEnPage.addLayout(miseEnPageH2)
    miseEnPage.addLayout(miseEnPageH3)
    miseEnPage.addWidget(boutonArret)
    drapeauArretFonctionEnCours=False
    def Reset(self):
        self.fenetreProgression.setWindowTitle(u'Mizogeo - progression du traitement')
        self.labelNomEtape.setText(u'En attente')
        self.labelCoucheATraiter.setText(u'Initialisation')
        self.progressBarLocale.setValue(0)
        ProgressBar.drapeauArretFonctionEnCours=False
    def InitialiserBarreProgressionLocale(self,nombreObjetMaximum, etapeTraitement):
        """
        Definit la valeur max de la barre et le titre de la progression locale
        en entrée, nombreObjetMaximum  ---> int
        en entrée, etapeTraitement  ---> str
        """
        self.progressBarLocale.setValue(0) #on passe la barre de progression locale à 0
        self.progressBarLocale.setMaximum(nombreObjetMaximum) #initialisation du nombre max de la barre de progression locale
        self.labelNomEtape.setText(etapeTraitement) #initialiser le descriptif du traitement en cour

class FenetreZbrCbs(QtGui.QDialog,fenetre_menu_ZBR_CBS_Ui.Ui_Dialog_ZbrCbs,MethodesPartagees): 
    """
    classe permettant l'ouverture d'une fenetre pour la creation des Zbr et Cbs par l'appel du fichier Ui
    """
    def __init__(self,parent=None):
        """
        constructeur des instances de la classe FenetreZbrCbs
        """
        super(FenetreZbrCbs,self).__init__(parent)#on recupere le constrcuteur des classes mères
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)#on recupere la methode setupUi de la classe mère
        self.Btn_ChoixIsophones.setIcon(iconSearch)#initialisation de l'icone bouton ici plutot que dans le .ui pour eviter les conflits avec le fichier resources.qrc
        self.Btn_ChoixIsophones.setStyleSheet('QToolButton {background-color: #26819E}')
        self.Btn_ChoixSortie.setIcon(iconSearch)
        self.Btn_ChoixSortie.setStyleSheet('QToolButton {background-color: #26819E}')
        self.Btn_ChoixCorrespondanceVc.setIcon(iconSearch)
        self.Btn_ChoixCorrespondanceVc.setStyleSheet('QToolButton {background-color: #26819E}')
        self.Btn_VoiesNouvelles.setIcon(iconSearch)
        self.Btn_VoiesNouvelles.setStyleSheet('QToolButton {background-color: #26819E}')
        self.Btn_ChoixIsophones.clicked.connect(self.ChoixIsophone) #lien entre le bouton Btn_ChoixIsophones du fichier Ui, et la methode choixDossier definie dessous. principe du signal / slots
        self.Btn_ChoixCorrespondanceVc.clicked.connect(self.ChoixCorrespondanceVc) #lien entre le bouton Btn_ChoixCorrespondanceVc du fichier Ui, et la methode ChoixCorrespondanceVc definie dessous. principe du signal / slots
        self.Btn_ChoixSortie.clicked.connect(self.ChoixSortie) #lien entre le bouton Btn_ChoixIsophones du fichier Ui, et la methode choixDossier definie dessous. principe du signal / slots
        self.Btn_VoiesNouvelles.clicked.connect(self.ChoixVoiesNouvelles)
        self.ButtonBox_Final.rejected.connect(self.reject)
        self.ButtonBox_Final.accepted.connect(self.executionZbrCbs)
        self.ButtonBox_Final.helpRequested.connect(lambda : self.OuvrirAide(14))
        self.line_isophone.textChanged.connect(self.MettreAJourIcone)
        self.line_isophone.textChanged.connect(self.MemoriserCheminIsophone)
        self.line_CorrespondanceVc.textChanged.connect(self.MettreAJourIcone)
        self.line_CorrespondanceVc.textChanged.connect(self.MemoriserCheminCorrespondance)
        self.line_Sortie.textChanged.connect(self.MettreAJourIcone)
        self.line_Sortie.textChanged.connect(self.MemoriserCheminSortie)
        self.line_VoiesNouvelles.textChanged.connect(self.MettreAJourIcone)
        self.line_VoiesNouvelles.textChanged.connect(self.MemoriserCheminVoieNouvelle)
        self.line_Producteur.textChanged.connect(self.VerifValiditeProducteur)
        self.line_Producteur.textChanged.connect(self.MemoriserProducteur)
        self.line_isophone.setText(cheminChoixIso)
        self.line_CorrespondanceVc.setText(cheminChoixCorrespondance)
        self.line_Sortie.setText(cheminChoixSortie)
        self.line_VoiesNouvelles.setText(cheminChoixVoieNouvelle)
        self.line_Producteur.setText(cheminChoixProducteur)         
    def executionZbrCbs(self): 
        """
        methode recuperant les donnees contenu dans les 4 lignes de la fenetre de creation des Zbr et Cbs et lancant la fonction globale de creation des Zbr et Cbsl
        """
        urlDossierIsophone=self.line_isophone.text() #affectation des contenus des Qlineedit dans des variables
        if self.line_CorrespondanceVc.text()=='':
            urlCorrespondanceVc=os.path.join(os.path.dirname(__file__),'ressources','TableCorrespondanceNomSIG.csv')
        else :
            urlCorrespondanceVc=self.line_CorrespondanceVc.text()
        urlSortie=self.line_Sortie.text()
        urlVoiesNouvelles=self.line_VoiesNouvelles.text()
        
        if self.line_Producteur.text()=='':
            producteur='130018310'
        else:
            producteur=self.line_Producteur.text()
        if urlDossierIsophone=='' or  urlSortie =='' or (producteur !='' and len(producteur)!=9) : #analyse du contenu des Qlineedit, si vide alors message d'erreur
            self.MessageErreurFichierNonSelectionne()
            return #ne pas enchainer sur la suite de la fonction dans ce cas pour permettre a utilisatuer de renseigner le champs manquant
        ############gestion des separateur des fichiers csv
        separateurCorrespondanceVc=self.VerifSeparateurCsv(urlCorrespondanceVc)
        print urlCorrespondanceVc, separateurCorrespondanceVc
        if urlVoiesNouvelles!='':
            separateurVoiesNouvelles=self.VerifSeparateurCsv(urlVoiesNouvelles)
        else :
            separateurVoiesNouvelles=';'
        if separateurCorrespondanceVc!=';' and separateurVoiesNouvelles !=';' :
            self.MessageFinTraitement(3,urlCorrespondanceVc +' et le fichier '+ urlVoiesNouvelles,u'Création simultanée N_BRUIT_ZBR et N_BRUIT_CBS', u'Mizogeo peut ni ouvrir ls fichiers de correspondance nom SIG-nom rapportage UE et ni le fichier de recensement des voies nouvelles', urlCorrespondanceVc)
        elif separateurCorrespondanceVc!=';' :
            self.MessageFinTraitement(3,urlCorrespondanceVc,u'Création simultanée N_BRUIT_ZBR et N_BRUIT_CBS', u'Mizogeo ne peut pas ouvrir le fichier de correspondance nom SIG-nom rapportage UE', urlCorrespondanceVc)
        elif separateurVoiesNouvelles !=';' :
            self.MessageFinTraitement(3,urlVoiesNouvelles,u'Création simultanée N_BRUIT_ZBR et N_BRUIT_CBS', u'Mizogeo ne peut pas ouvrir le fichier de recensement des voies nouvelles', urlVoiesNouvelles)
        ##########si les separateurs sont ok
        else :        
            statutEvolutionTraitement=CreationZbrCbs(urlDossierIsophone,urlCorrespondanceVc,urlSortie,urlVoiesNouvelles,producteur)#executer la fonction globale
            if statutEvolutionTraitement==1 :
                listeFichierErreur=glob.glob(urlSortie+os.sep+'listeErreursIsophones_*.csv') #trouver les fichier csv relatifs aux erreurs issu de creation zbr
                listeNumero=[]
                for fichier in listeFichierErreur:
                    try :
                        numero=int(fichier.split('listeErreursIsophones_')[1][:-4]) #isoler les numero de fichier
                        listeNumero.append(numero)
                    except:
                        1
                self.MessageFinTraitement(statutEvolutionTraitement,urlSortie,u'Création simultanée N_BRUIT_ZBR et N_BRUIT_CBS', u'Mizogeo ne peut pas traiter le(s) fichier(s) sélectionné(s)', 'listeErreursIsophones_'+str(max(listeNumero))+'.csv')
            elif statutEvolutionTraitement==2 :
                self.MessageFinTraitement(statutEvolutionTraitement,urlSortie,u'Création simultanée N_BRUIT_ZBR et N_BRUIT_CBS', u'Arrêt du traitement forcé par l\'utilisateur','')
            else:
                self.MessageFinTraitement(statutEvolutionTraitement,urlSortie,u'Création simultanée N_BRUIT_ZBR et N_BRUIT_CBS', u'Mise au GéoStandard réussie','')
        self.close()

class FenetrePpbe(QtGui.QDialog,fenetre_menu_PPBE_Ui.Ui_Dialog_PPBE,MethodesPartagees): 
    """
    classe permettant l'ouverture d'une fenetre pour la creation des ppbe par l'appel du fichier Ui
    """
    def __init__(self,parent=None):
        """
        constructeur des instances de la classe FenetrePpbe
        """
        super(FenetrePpbe,self).__init__(parent)
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        
        self.Btn_ChoixSortie.setIcon(iconSearch)
        self.Btn_ChoixSortie.setStyleSheet('QToolButton {background-color: #26819E}')
        listeDepartementFranceEntiere=self.CreationListeDepartement()#recuperer la liste des departement present dans les fichiers lus par la fonction CreationListeDepartement
        self.listWidget_departementPpbe.addItems(listeDepartementFranceEntiere)#ajouter la liste des dept au widget      
        self.listWidget_departementPpbe.itemSelectionChanged.connect(self.ChoixDepartementPpbe)#quand la selection change on appelle la fonction definie dans methodepartagee
        self.Btn_ChoixSortie.clicked.connect(self.ChoixSortie) #lien entre le bouton Btn_ChoixIsophones du fichier Ui, et la methode choixDossier definie dessous. principe du signal / slots
        self.ButtonBox_Final.rejected.connect(self.reject)
        self.ButtonBox_Final.accepted.connect(self.executionPpbe)
        self.ButtonBox_Final.helpRequested.connect(lambda : self.OuvrirAide(37))
        self.line_Sortie.textChanged.connect(self.MettreAJourIcone)
        self.line_Sortie.textChanged.connect(self.MemoriserCheminSortie)
        self.line_Producteur.textChanged.connect(self.VerifValiditeProducteur)
        self.line_Producteur.textChanged.connect(self.MemoriserProducteur)
        self.line_Sortie.setText(cheminChoixSortie)
        self.line_Producteur.setText(cheminChoixProducteur)
    def executionPpbe(self):
        """
        methode recuperant les donnees contenu dans les 4 lignes de la fenetre de creation des ppbe et lancant la fonction globale de creation des Ppbe
        """
        departementATraiter=self.line_DepartementPpbe.text()   #affectation des contenus des Qlineedit dans des variables
        urlSortie =self.line_Sortie.text()
        if departementATraiter =='' or  urlSortie =='': #analyse du contenu des Qlineedit, si vide alors message d'erreur
            self.MessageErreurFichierNonSelectionne()
            return #ne pas enchainer sur la suite de la fonction dans ce cas pour permettre a utilisatuer de renseigner le champs manquant
        if self.line_Producteur.text()=='':
            producteur='130018310'
        else:
            producteur=self.line_Producteur.text()
        
        if urlSortie =='' or (producteur !='' and len(producteur)!=9) : #analyse du contenu des Qlineedit, si vide alors message d'erreur
            self.MessageErreurFichierNonSelectionne()
            return
        #verification du texte contenant les departements et execution si tout ok
        erreurTexteDepartement=VerificationDepartementPpbe(departementATraiter)
        if erreurTexteDepartement==1 :
            self.MessageFinTraitement(4,u'les erreurs possibles sont : \n - présence de caractères non numériques ou séparateur différent de la virgule \n - longueur du code département différente de 3 caractères',u'Création N_BRUIT_PPBE', u'Mizogeo ne peut pas traiter le(s) département(s) indiqué(s)','')
        else :
            statutEvolutionTraitement=CreationPPBEshp(departementATraiter,urlSortie,producteur)
            if statutEvolutionTraitement==1 :
                self.MessageFinTraitement(statutEvolutionTraitement,urlSortie,u'Création N_BRUIT_PPBE', u'Mizogeo ne peut pas traiter les fichiers sélectionnés','')
            elif statutEvolutionTraitement==2 :
                self.MessageFinTraitement(statutEvolutionTraitement,urlSortie,u'Création N_BRUIT_PPBE', u'Arrêt du traitement forcé par l\'utilisateur','')
            else:
                self.MessageFinTraitement(statutEvolutionTraitement,urlSortie,u'Création N_BRUIT_PPBE', u'Mise au GéoStandard réussie','')
        self.close()

class FenetreAgregation(QtGui.QDialog,fenetre_menu_Agregation_Ui.Ui_Dialog_Agregation,MethodesPartagees):
    """
    classe permettant l'ouverture d'une fenetre pour l'Agregation des fichiers N_BRUIT_ZBR par l'appel du fichier Ui
    """
    def __init__(self,parent=None):
        """
        constructeur des instances de la classe FenetreAgregation
        """
        super(FenetreAgregation,self).__init__(parent)
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.Btn_ChoixSortie.setIcon(iconSearch)
        self.Btn_ChoixSortie.setStyleSheet('QToolButton {background-color: #26819E}')
        self.Btn_Zbr.setIcon(iconSearch)
        self.Btn_Zbr.setStyleSheet('QToolButton {background-color: #26819E}')
        self.Btn_perimetre.setIcon(iconSearch)
        self.Btn_perimetre.setStyleSheet('QToolButton {background-color: #26819E}')
        listeDepartementFranceEntiere=self.CreationListeDepartement()
        self.listWidget_departementPpbe.addItems(listeDepartementFranceEntiere)
        self.listWidget_departementPpbe.itemSelectionChanged.connect(self.ChoixDepartementPpbe)
        self.line_DepartementPpbe.textChanged.connect(self.DisponibiliteChoixPerimetre)
        self.line_perimetre.textChanged.connect(self.DisponibiliteChoixPerimetre)
        self.Btn_ChoixSortie.clicked.connect(self.ChoixSortie)
        self.Btn_Zbr.clicked.connect(self.ChoixZbr)
        self.Btn_perimetre.clicked.connect(self.ChoixPerimetre)
        self.ButtonBox_Final.rejected.connect(self.reject)
        self.ButtonBox_Final.accepted.connect(self.executionAgregation)
        self.ButtonBox_Final.helpRequested.connect(lambda : self.OuvrirAide(67))
        self.line_Sortie.textChanged.connect(self.MettreAJourIcone)
        self.line_Sortie.textChanged.connect(self.MemoriserCheminSortie)
        self.line_Zbr.textChanged.connect(self.MettreAJourIcone)
        self.line_Zbr.textChanged.connect(self.MemoriserCheminZbr)
        self.line_perimetre.textChanged.connect(self.MettreAJourIcone)
        self.line_perimetre.textChanged.connect(self.MemoriserCheminPerimetre)
        self.line_perimetre.setText(cheminChoixPerimetre)
        self.line_Zbr.setText(cheminChoixZbr)
        self.line_Sortie.setText(cheminChoixSortie)
    def executionAgregation(self): 
        """
        methode recuperant les donnees contenu dans les 3 lignes de la fenetre d'Agregation et lancant la fonction globale d'agregation
        """
        departementATraiter=self.line_DepartementPpbe.text()
        urlPerimetre=self.line_perimetre.text() #affectation des contenus des Qlineedit dans des variables
        urlZbr=self.line_Zbr.text()
        urlSortie=self.line_Sortie.text()
        if (urlPerimetre=='' and departementATraiter=='') or urlZbr=='' or  urlSortie=='': #analyse du contenu des Qlineedit, si vide alors message d'erreur
            self.MessageErreurFichierNonSelectionne()
            return #ne pas enchainer sur la suite de la fonction dans ce cas pour permettre a utilisatuer de renseigner le champs manquant
        if len(departementATraiter)!=3 : #verification que le departement est bien code sur 3 caracteres et execution si ok
            self.MessageFinTraitement(4,u'Longueur du code département différente de 3 caractères',u'Agrégation N_BRUIT_ZBR par périmètre', u'Mizogeo ne peut pas traiter le département indiqué','')
        else : 
            statutEvolutionTraitement=CreationAgregation(departementATraiter,urlPerimetre,urlZbr,urlSortie)#executer la fonction globale
            if statutEvolutionTraitement==1 :
                listeFichierErreur=glob.glob(urlSortie+os.sep+'listeErreursAgregation_*.csv') #trouver les fichier csv relatifs aux erreurs issu de creation zbr
                listeNumero=[]
                for fichier in listeFichierErreur:
                    numero=int(fichier.split('listeErreursAgregation_')[1][:-4]) #isoler les numero de fichier
                    listeNumero.append(numero)
                self.MessageFinTraitement(statutEvolutionTraitement,urlSortie,u'Agrégation N_BRUIT_ZBR par périmètre', u'Mizogeo ne peut pas traiter les fichiers selectionnés','listeErreursAgregation_'+str(max(listeNumero))+'.csv')
            elif statutEvolutionTraitement==2 :
                self.MessageFinTraitement(statutEvolutionTraitement,urlSortie,u'Agrégation N_BRUIT_ZBR par périmètre', u'Arrêt du traitement forcé par l\'utilisateur','')
            else:
                self.MessageFinTraitement(statutEvolutionTraitement,urlSortie,u'Agrégation N_BRUIT_ZBR par périmètre', u'Agrégation réussie','')
        self.close()

class FenetreAssemblage(QtGui.QDialog,fenetre_menu_Assemblage_Ui.Ui_Dialog_Assemblage,MethodesPartagees): 
    """
    classe permettant l'ouverture d'une fenetre pour la concatenation des Zbr et Cbs par l'appel du fichier Ui
    """
    def __init__(self,parent=None):
        """
        constructeur des instances de la classe FenetreConcatenation
        """
        super(FenetreAssemblage,self).__init__(parent)
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.Btn_ChoixSortie.setIcon(iconSearch)
        self.Btn_ChoixSortie.setStyleSheet('QToolButton {background-color: #26819E}')
        self.Btn_dbf.setIcon(iconSearch)
        self.Btn_dbf.setStyleSheet('QToolButton {background-color: #26819E}')
        self.Btn_ChoixSortie.clicked.connect(self.ChoixSortie)
        self.Btn_dbf.clicked.connect(self.ChoixDbf)
        self.ButtonBox_Final.rejected.connect(self.reject)
        self.ButtonBox_Final.accepted.connect(self.executionAssemblage)
        self.ButtonBox_Final.helpRequested.connect(lambda : self.OuvrirAide(53))
        self.line_Sortie.textChanged.connect(self.MettreAJourIcone)
        self.line_Sortie.textChanged.connect(self.MemoriserCheminSortie)
        self.line_Dbf.textChanged.connect(self.MettreAJourIcone)
        self.line_Dbf.textChanged.connect(self.MemoriserCheminDbf)
        self.line_Dbf.setText(cheminChoixDbf)
        self.line_Sortie.setText(cheminChoixSortie)
    def executionAssemblage(self): 
        """
        methode recuperant les donnees contenu dans les 2 lignes de la fenetre de concatenation et lancant la fonction globale d'agregation
        """
        urlDbf=self.line_Dbf.text()#affectation des contenus des Qlineedit dans des variables
        urlSortie=self.line_Sortie.text()
        if urlDbf=='' or  urlSortie=='': #analyse du contenu des Qlineedit, si vide alors message d'erreur
            self.MessageErreurFichierNonSelectionne()
            return #ne pas enchainer sur la suite de la fonction dans ce cas pour permettre a utilisatuer de renseigner le champs manquant
        statutEvolutionTraitement=CreationAssemblage(urlDbf, urlSortie)
        if statutEvolutionTraitement==1 :
            listeFichierErreur=glob.glob(urlSortie+os.sep+'listeErreursFichiersAssemblage_*.csv') #trouver les fichier csv relatifs aux erreurs issu de creation zbr
            listeNumero=[]
            for fichier in listeFichierErreur:
                numero=int(fichier.split('listeErreursFichiersAssemblage_')[1][:-4]) #isoler les numero de fichier
                listeNumero.append(numero)
            self.MessageFinTraitement(statutEvolutionTraitement,urlSortie,u'Assemblage des tables attributaires', u'Mizogeo ne peut pas traiter les fichiers sélectionnés', 'listeErreursFichiersAssemblage_'+str(max(listeNumero))+'.csv')
        elif statutEvolutionTraitement==2 :
            self.MessageFinTraitement(statutEvolutionTraitement,urlSortie,u'Assemblage des tables attributaires', u'Arrêt du traitement forcé par l\'utilisateur','')
        else:
            self.MessageFinTraitement(statutEvolutionTraitement,urlSortie,u'Assemblage des tables attributaires', u'Assemblage réussi','')
     	self.close()
