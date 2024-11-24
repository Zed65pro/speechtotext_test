from sinatools.morphology import morph_analyzer
from sinatools.utils.parser import arStrip


class SinaToolsApi:
    @classmethod
    def get_lemmas(cls, text):
        # Morphological analysis
        analyzed_text = morph_analyzer.analyze(text=text, task='lemmatization')
        return [arStrip(text=text['lemma']) for text in analyzed_text]
