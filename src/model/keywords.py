from .base import Model
import yake
import keybert


class KeywordExtractorYAKE(Model):
    '''
        This is Keyword Extractor class which extracts keywords from the texts.
    '''
    def __init__(self, language='en'):
        super(KeywordExtractorYAKE, self).__init__()
        self.model = yake.KeywordExtractor(lan=language)

    
    def predict(self, texts: list[str]) -> list:
        '''
            Function accepts list of texts and applies YAKE keyword extraction model.

        :texts: The texts we are predicting over
        :return: returns lists of keywords in order in which texts came.
        '''
        keywords = [self.model.extract_keywords(text) for text in texts]

        return keywords
    

class KeywordExtractorKeyBERT(Model):
    def __init__(self, language='en'):
        super(KeywordExtractorKeyBERT, self).__init__()
        self.model = keybert.KeyBERT()


    def predict(self, texts: list[str]) -> list:
        '''
            Function accepts list of texts and applies YAKE keyword extraction model.

        :texts: The texts we are predicting over
        :return: returns lists of keywords in order in which texts came.
        '''
        keywords = self.model.extract_keywords(texts)

        return keywords