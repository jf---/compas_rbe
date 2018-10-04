from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from functools import partial

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import compas

from compas.utilities import hex_to_rgb
from compas.utilities import flatten

from compas.viewers.core import GLWidget
from compas.viewers.core import Grid
from compas.viewers.core import Axes


__all__ = ['View']


hex_to_rgb = partial(hex_to_rgb, normalize=True)


def flist(items):
    return list(flatten(items))


class View(GLWidget):
    """"""

    def __init__(self, controller):
        super(View, self).__init__()
        self.controller = controller
        self.n = 0
        self.v = 0
        self.e = 0
        self.f = 0

    @property
    def assembly(self):
        return self.controller.assembly

    @property
    def blocks(self):
        return self.controller.blocks

    @property
    def settings(self):
        return self.controller.settings

    # ==========================================================================
    # arrays
    # ==========================================================================

    @property
    def array_xyz(self):
        xyz = []
        for block in self.blocks:
            xyz += block.xyz
        return flist(xyz)

    @property
    def array_vertices(self):
        vertices = []
        for block in self.blocks:
            i = len(vertices)
            vertices += [key + i for key in block.vertices]
        return vertices

    @property
    def array_edges(self):
        i = 0
        edges = []
        for block in self.blocks:
            edges += [[u + i, v + i] for u, v in block.edges]
            i += len(list(block.vertices))
        return flist(edges)

    @property
    def array_faces_front(self):
        i = 0
        faces = []
        for block in self.blocks:
            faces += [[u + i for u in face] for face in block.faces]
            i += len(list(block.vertices))
        return flist(faces)

    @property
    def array_faces_back(self):
        i = 0
        faces = []
        for block in self.blocks:
            faces += [[u + i for u in face] for face in block.faces]
            i += len(list(block.vertices))
        return flist(face[::-1] for face in faces)

    @property
    def array_vertices_color(self):
        return flist(hex_to_rgb(self.settings['vertices.color']) for _ in self.array_vertices)

    @property
    def array_edges_color(self):
        return flist(hex_to_rgb(self.settings['edges.color']) for _ in self.array_vertices)

    @property
    def array_faces_color_front(self):
        return flist(hex_to_rgb(self.settings['faces.color:front']) for _ in self.array_xyz)

    @property
    def array_faces_color_back(self):
        return flist(hex_to_rgb(self.settings['faces.color:back']) for _ in self.array_xyz)

    # ==========================================================================
    # CAD
    # ==========================================================================

    def setup_grid(self):
        grid = Grid()
        index = glGenLists(1)
        glNewList(index, GL_COMPILE)
        grid.draw()
        glEndList()
        self.display_lists.append(index)

    def setup_axes(self):
        axes = Axes()
        index = glGenLists(1)
        glNewList(index, GL_COMPILE)
        axes.draw()
        glEndList()
        self.display_lists.append(index)

    # ==========================================================================
    # painting
    # ==========================================================================

    def paint(self):
        glDisable(GL_DEPTH_TEST)
        for dl in self.display_lists:
            glCallList(dl)

        glEnable(GL_DEPTH_TEST)
        self.draw_buffers()

    def make_buffers(self):
        self.buffers = {
            'xyz'              : self.make_vertex_buffer(self.array_xyz),
            'vertices'         : self.make_index_buffer(self.array_vertices),
            'edges'            : self.make_index_buffer(self.array_edges),
            'faces:front'      : self.make_index_buffer(self.array_faces_front),
            'faces:back'       : self.make_index_buffer(self.array_faces_back),
            'vertices.color'   : self.make_vertex_buffer(self.array_vertices_color, dynamic=True),
            'edges.color'      : self.make_vertex_buffer(self.array_edges_color, dynamic=True),
            'faces.color:front': self.make_vertex_buffer(self.array_faces_color_front, dynamic=True),
            'faces.color:back' : self.make_vertex_buffer(self.array_faces_color_back, dynamic=True),
        }
        self.n = len(self.array_xyz)
        self.v = len(self.array_vertices)
        self.e = len(self.array_edges)
        self.f = len(self.array_faces_front)

    def draw_buffers(self):
        if not self.buffers:
            return

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)

        glBindBuffer(GL_ARRAY_BUFFER, self.buffers['xyz'])
        glVertexPointer(3, GL_FLOAT, 0, None)

        if self.settings['faces.on']:
            glBindBuffer(GL_ARRAY_BUFFER, self.buffers['faces.color:front'])
            glColorPointer(3, GL_FLOAT, 0, None)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.buffers['faces:front'])
            glDrawElements(GL_TRIANGLES, self.f, GL_UNSIGNED_INT, None)

            glBindBuffer(GL_ARRAY_BUFFER, self.buffers['faces.color:back'])
            glColorPointer(3, GL_FLOAT, 0, None)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.buffers['faces:back'])
            glDrawElements(GL_TRIANGLES, self.f, GL_UNSIGNED_INT, None)

        if self.settings['edges.on']:
            glLineWidth(self.settings['edges.width:value'])
            glBindBuffer(GL_ARRAY_BUFFER, self.buffers['edges.color'])
            glColorPointer(3, GL_FLOAT, 0, None)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.buffers['edges'])
            glDrawElements(GL_LINES, self.e, GL_UNSIGNED_INT, None)

        if self.settings['vertices.on']:
            glPointSize(self.settings['vertices.size:value'])
            glBindBuffer(GL_ARRAY_BUFFER, self.buffers['vertices.color'])
            glColorPointer(3, GL_FLOAT, 0, None)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.buffers['vertices'])
            glDrawElements(GL_POINTS, self.v, GL_UNSIGNED_INT, None)

        glDisableClientState(GL_COLOR_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    pass