from .base import Model
from transformers import pipeline


class BertSentimentAnalyser(Model):
    def __init__(self):
        super(BertSentimentAnalyser, self).__init__()
        self.model = pipeline('text-classification', 
                              model='bhadresh-savani/distilbert-base-uncased-emotion',
                              return_all_scores=True)
        
    
    def predict(self, texts: list) -> list:
        predictions = [self.model.predict(text) for text in texts]
        return predictions