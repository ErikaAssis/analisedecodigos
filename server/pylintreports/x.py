# Licensed under the GPL: https://www.gnu.org/licenses/old-licenses/gpl-2.0.html
# For details: https://github.com/PyCQA/pylint/blob/master/COPYING

"""JSON reporter"""

from __future__ import absolute_import, print_function

import cgi
import json
import sys
from pylint.interfaces import IReporter
from pylint.reporters import BaseReporter
from json_writer import JWriter


class JReporter(BaseReporter):
    """report messages and layouts in HTML"""

    __implements__ = IReporter
    name = 'x'
    extension = 'x'

    def __init__(self, output=sys.stdout):
        BaseReporter.__init__(self, output)
        self.messages = []

    def handle_message(self, message):
        """Manage message of different type and in the context of path.
           pylint: disable=deprecated-method; deprecated since 3.2.
        """
        self.messages.append({
            'type': message.category,
            'module': message.module,
            'obj': message.obj,
            'line': message.line,
            'column': message.column,
            'path': message.path,
            'symbol': message.symbol,
            'message': cgi.escape(message.msg or ''),
        })

    def display_messages(self, layout):
        """Launch layouts display"""
        if self.messages:
            print(json.dumps(self.messages, indent=4), file=self.out)

    def _display(self, layout):
        """launch layouts display

        overridden from BaseReporter to add insert the messages section
        (in add_message, message is not displayed, just collected so it
        can be displayed in an html table)
        """
        JWriter().format(layout, self.out)


def register(linter):
    """Register the reporter classes with the linter."""
    linter.register_reporter(JReporter)
