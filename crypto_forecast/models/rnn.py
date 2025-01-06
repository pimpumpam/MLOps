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
        for layer in self.model:
            x = layer(x)
            
        return x
        
    
class GRULayer(nn.Module):
    
    def __init__(self, cfg_model):
        super(GRULayer, self).__init__()
        
        self.cfg_model = cfg_model
        self.model = nn.ModuleList()
        
        for idx, (module, args) in enumerate(cfg_model.gru_layer['architecture']):
            layer = eval(module)(*args)
            
            self.model.appen(layer)
            
    def forward(self, x):
        for layer in self.model:
            x = layer(x)
            
        return x