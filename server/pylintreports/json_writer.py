# Copyright (c) 2003-2016 LOGILAB S.A. (Paris, FRANCE).
# http://www.logilab.fr/ -- mailto:contact@logilab.fr
# Licensed under the GPL: https://www.gnu.org/licenses/old-licenses/gpl-2.0.html
# For details: https://github.com/PyCQA/pylint/blob/master/COPYING

"""HTML formatting drivers for ureports"""

import json
from pylint.reporters.ureports import BaseWriter


class JWriter(BaseWriter):
    """format layouts as HTML"""

    def __init__(self, snippet=None):
        ''' Inicializa a clase '''
        super(JWriter, self).__init__()
        self.snippet = snippet
        self.js = {}
        self.title = ''

    def begin_format(self):
        """begin to format a layout"""
        super(JWriter, self).begin_format()
        if self.snippet is None:
            # self.writeln(u'{aqui')

            pass

    def end_format(self):
        """finished to format a layout"""
        if self.snippet is None:
            # self.writeln(u'}')
            self.writeln(json.dumps(self.js))

    def visit_section(self, layout):
        """display a section as html, using div + h[section level]"""

        self.format_children(layout)

    def visit_title(self, layout):
        """display a title using <hX>"""
        self.title = self.compute_content(layout).next().replace(' ', '-')

    def visit_table(self, layout):
        """display a table as html"""

        table_content = self.get_table_content(layout)

        header = []
        table = []
        for i, row in enumerate(table_content):
            table.append([])
            for j, cell in enumerate(row):
                # cell = cell or u'&#160;'

                if (layout.rheaders and i == 0) or \
                   (layout.cheaders and j == 0):
                    header.append(self.convert(cell))

                else:
                    table[i].append(self.convert(cell))
        t = []
        for x in table[1:]:
            h = [header, x]
            t.append((dict(zip(* h))))

        self.js[self.title] = t

    def convert(self, n):
        try:
            return float(n)
        except:
            return n.replace(' ', '@')

    def visit_paragraph(self, layout):
        """display links (using <p>)"""

        self.js['statements'] = self.compute_content(
            layout).next().replace(' ', '-')

    def visit_verbatimtext(self, layout):
        """display verbatim text (using <pre>)"""
        self.js['dependences'] = (layout.data.replace(
            u'&', u'&amp;').strip().replace(u'<', u'&lt;')).replace(' ', '-')

    def visit_text(self, layout):
        """add some text"""
        data = layout.data
        if layout.escaped:
            data = data.replace(u'&', u'').replace(u'<', u'').replace(' ', '_')
        self.write(data)
