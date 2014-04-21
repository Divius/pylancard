class BaseLanguage:

    help_text = ""

    patterns = {}

    def __init__(self, store):
        self.store = store

    def convert_word(self, word):
        for pattern, replace in self.patterns.items():
            word = word.replace(pattern, replace)
        return word
