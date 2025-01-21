import torch.nn as nn
import torch.multiprocessing as mp

from models.rnn import LSTMLayer, GRULayer
from models.linear import LinearLayer


class Model(nn.Module):
    
    def __init__(self, cfg_model):
        super(Model, self).__init__()
        
        self.cfg_model = cfg_model
        self.model_name = cfg_model.name
        self.linear_layer = LinearLayer(cfg_model)
        if cfg_model.name == 'LSTM':
            self.rnn_layer = LSTMLayer(cfg_model)
        elif cfg_model.name == 'GRU':
            self.rnn_layer = GRULayer(cfg_model)
            
    def forward(self, x):
        
        out = self.rnn_layer(x) # batch x num_seq x hidden
        out = out.reshape(out.size(0), -1) # batch x (num_seq * hidden)
        out = self.linear_layer(out) # batch x (pred_seq * out_feat)
        out = out.reshape(out.size(0), -1, self.cfg_model.output_feat_dim)
        
        return out