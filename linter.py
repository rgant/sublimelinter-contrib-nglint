""" Based on SublimeLinter-tslint
https://github.com/SublimeLinter/SublimeLinter-tslint/blob/43f6771008da67a9487d467ac5b4f9306c247fac/linter.py
"""
import logging
import os.path
import re

from SublimeLinter.lint import NodeLinter


class Nglint(NodeLinter):
    """
    Since Angular CLI v8 ng lint can lint single files.
    https://github.com/angular/angular-cli/issues/13668
    """
    cmd = 'ng lint --format=verbose --typeCheck=true --files ${ng_project_file_path}'
    regex = (
        r'^(?:'
        r'(ERROR:\s+\((?P<error>.*)\))|'
        r'(WARNING:\s+\((?P<warning>.*)\))'
        r')?'
        r'\s+(?P<filename>.+?)'
        r'\[(?P<line>\d+), (?P<col>\d+)\]: '
        r'(?P<message>.+)'
    )
    multiline = False
    tempfile_suffix = '-'
    defaults = {
        'selector': 'source.ts'
    }

    def run(self, cmd, code):
        # ng lint doesn't understand full file paths and needs a relative path.
        # Assumption here is that the sublime project root will equal the angular project root.
        self.context['ng_project_file_path'] = os.path.relpath(self.context['file'],
                                                               self.context['project_root'])
        return super().run(cmd, code)

    def on_stderr(self, output):
        """ Suppress the message from ng lint when lint errors are found. """
        logger = logging.getLogger(__name__)
        output = re.sub('Lint errors found in the listed files.\n', '', output)

        if output:
            self.notify_failure()
            logger.error(output)
