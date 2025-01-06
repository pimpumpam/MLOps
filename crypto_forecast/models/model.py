import torch.nn as nn

from models.rnn import LSTMLayer, GRULayer
from models.linear import LinearLayer

class Model(nn.Module):
    
    def __init__(self, cfg_model):
        super(Model, self).__init__()
        
        self.model_name = cfg_model.name
        self.linear_layer = LinearLayer(cfg_model)
        if cfg_model.name == 'LSTM':
            self.rnn_layer = LSTMLayer(cfg_model)
        elif cfg_model.name == 'GRU':
            self.rnn_layer = GRULayer(cfg_model)
            
    def forward(self, x):
        
        rnn_out = self.rnn_layer(x)
        pred = self.linear_layer(rnn_out)
        
        return pred