from .base import Model
from transformers import pipeline


class BertSentimentAnalyser(Model):
    def __init__(self):
        super(BertSentimentAnalyser, self).__init__()
        self.model = pipeline('text-classification', 
                              model='bhadresh-savani/distilbert-base-uncased-emotion',
                              return_all_scores=True)
        
    
    def predict(self, texts: list) -> list:
        raw_predictions = [self.model.predict(text[:512]) for text in texts]
        predictions = list(map(lambda preiction: preiction[0], raw_predictions))
        return predictions