# -*- coding: utf8 -*-

from . import base


HELP = """
The following replacements are available:
%s
"""


class Czech(base.BaseLanguage):

    patterns = {
        "`a": "á",
        "`e": "é",
        "`i": "í",
        "`u": "ú",
        "`y": "ý",
        "0u": "ů",
        "~e": "ě",
        "~s": "š",
        "~c": "č",
        "~r": "ř",
        "~z": "ž",
    }

    help_text = HELP % '\n'.join('- %s = %s' % item
                                 for item in patterns.items())


create_plugin = Czech
