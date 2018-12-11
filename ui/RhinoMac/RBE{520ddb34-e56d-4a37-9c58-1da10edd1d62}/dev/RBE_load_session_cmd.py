from __future__ import print_function
from __future__ import absolute_import
from __future__ import division


import rhinoscriptsyntax as rs
import scriptcontext as sc

import Rhino

import os
import sys
import traceback

import compas_rhino
import compas_rbe

HERE = os.path.abspath(os.path.dirname(__file__))
SESSIONS = os.path.join(HERE, '../sessions')


__commandname__ = "RBE_load_session"


def RunCommand(is_interactive):
    try:

        if not 'RBE' in sc.sticky:
            raise Exception('Initialise RBE first!')

        RBE = sc.sticky['RBE']

        path = compas_rhino.select_file(folder=SESSIONS, filter='JSON files (*.json)|*.json||')

        if not path:
            return

        with open(path, 'r') as fo:
            data = json.load(fo)

        if 'RBE' in data:
            RBE = data['RBE']
        else:
            RBE = data

        blocks = RBE['blocks']
        interfaces = RBE['interfaces']
        assembly = RBE['assembly'] = Assembly.from_blocks_and_interfaces(blocks, interfaces)

        assembly.draw(RBE['settings'])

    except Exception as error:

        print(error)
        print(traceback.format_exc())

    finally:

        sc.sticky['RBE'] = RBE
