# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MizogeoDialog
                                 A QGIS plugin
 Mise au format Geostandard des cartes de bruit 2012 .
                             -------------------
        begin                : 2017-04-24
        git sha              : $Format:%H$
        copyright            : (C) 2017 by cerema
        email                : sandra.benelli@cerema.fr
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from PyQt4 import QtGui, uic
import interfaceUtilisateur
#from interfaceUtilisateur import FenetreZbrCbs, FenetrePpbe, FenetreAgregation, FenetreConcatenation, MethodesPartagees

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'mizogeo_dialog_base.ui'))

################Definition des icones#####################################################
iconCerema=QtGui.QPixmap(os.path.join(os.path.dirname(os.path.abspath(__file__)),'icones', "iconCerema.gif"))
iconLogo = QtGui.QPixmap(os.path.join(os.path.dirname(os.path.abspath(__file__)),'icones',"logoMizogeo.gif"))
iconEcrito = QtGui.QPixmap(os.path.join(os.path.dirname(os.path.abspath(__file__)),'icones',"ecritoMizogeo.gif"))
###########################################################################################

class MizogeoDialog(QtGui.QDialog, FORM_CLASS, interfaceUtilisateur.MethodesPartagees):
    def __init__(self, parent=None):
        """Constructor."""
        super(MizogeoDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.ImageCerema.setPixmap(iconCerema)
        self.ImageCerema.setScaledContents(True)
        self.LienCerema.setText('''<a href='http://www.cerema.fr/'>Visitez notre site internet</a>''')
        self.LienCerema.setOpenExternalLinks(True)
        #self.ImageCerema.clicked.connect(http://www.cerema.fr/)
        self.ImageLogo.setPixmap(iconLogo)
        self.ImageLogo.setScaledContents(True)
        self.ImageEcrito.setPixmap(iconEcrito)
        self.ImageEcrito.setScaledContents(True)
        self.Btn_Aide.clicked.connect(lambda : self.OuvrirAide(1))
        self.BoutonZbrCbs.clicked.connect(self.OuvertureFenetreZbrCbs) #lien entre le bouton Btn_ZbrCbs du fichier Dialog, et la méthode fenetreZbrCbs definie dessous. principe du signal / slots  
        self.BoutonPpbe.clicked.connect(self.OuvertureFenetrePpbe)
        self.BoutonAgregation.clicked.connect(self.OuvertureFenetreAgregation)
        self.BoutonAssemblage.clicked.connect(self.OuvertureFenetreAssemblage)
        self.Bonus.clicked.connect(self.EcouterMusiqueRads2011)
    
    def OuvertureFenetreZbrCbs(self): 
        """
        ouverture de la fenetre de creation des ZBR et CBS
        """
        self.fenetre=interfaceUtilisateur.FenetreZbrCbs() #creation de l instance issue de la classe FenetreZbrCbs
        self.fenetre.show() #On utilise exec_() plutot que show() car il bloque la fenetre qui lance la deuxieme, alors que show() laisse la premiere fenetre active
        
    def OuvertureFenetrePpbe(self):
        """
        ouverture de la fenetre de creation des Ppbe
        """
        self.fenetre=interfaceUtilisateur.FenetrePpbe() #creation de l instance issue de la classe FenetrePpbe
        self.fenetre.show()
    
    def OuvertureFenetreAgregation(self):
        """
        ouverture de la fenetre d'agregation
        """
        self.fenetre=interfaceUtilisateur.FenetreAgregation()
        self.fenetre.show()
     
    def OuvertureFenetreAssemblage(self):
        self.fenetre=interfaceUtilisateur.FenetreAssemblage()
        self.fenetre.show()#lancer la fenetre suivante. On utilise exec_() plutot que show() car il bloque la fenetre qui lance la deuxieme, alors que show() laisse la premiere fenetre active
