# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Mizogeo
                                 A QGIS plugin
 Mise au format Geostandard des cartes de bruit 2012 .
                             -------------------
        begin                : 2017-04-24
        copyright            : (C) 2017 by cerema
        email                : outils.bruit@cerema.fr
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load Mizogeo class from file Mizogeo.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .mizogeo import Mizogeo
    return Mizogeo(iface)
