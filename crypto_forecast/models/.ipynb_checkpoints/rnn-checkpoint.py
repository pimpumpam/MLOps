import torch
import torch.nn as nn


class LSTMLayer(nn.Module):
    
    def __init__(self, cfg_model):
        super(LSTMLayer, self).__init__()
        
        self.cfg_model = cfg_model
        self.model = nn.ModuleList()
        
        for idx, (module, args) in enumerate(cfg_model.lstm_layer['architecture']):
            layer = eval(module)(*args)
            
            self.model.append(layer)
        
    def forward(self, x):
        
        h = torch.zeros(
            self.cfg_model.gru_layer['num_layers'],
            x.size()[0],
            self.cfg_model.gru_layer['hidden_dim']
        )
        
        c = torch.zeros(
            self.cfg_model.gru_layer['num_layers'],
            x.size()[0], 
            self.cfg_model.gru_layer['hidden_dim']
        )
        
        for layer in self.model:
            x, (h, c) = layer(x, (h, c))
            
        return x
        
    
class GRULayer(nn.Module):
    
    def __init__(self, cfg_model):
        super(GRULayer, self).__init__()
        
        self.cfg_model = cfg_model
        self.model = nn.ModuleList()
        
        for idx, (module, args) in enumerate(cfg_model.gru_layer['architecture']):
            layer = eval(module)(*args)
            
            self.model.append(layer)
        
    def forward(self, x):
        
        h = torch.zeros(
            self.cfg_model.gru_layer['num_layers'],
            x.size(0),
            self.cfg_model.gru_layer['hidden_dim']
        )
        
        for layer in self.model:
            x, h = layer(x, h)
            
        return x