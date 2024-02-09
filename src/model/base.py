class Model:
    '''
        This is the base model. 
    '''
    def predict(self, texts: list) -> list:
        raise NotImplementedError('This method must be implemented in the derived model.')
    