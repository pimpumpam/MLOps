import torch
import torch.nn as nn

class LinearLayer(nn.Module):
    
    def __init__(self, cfg_model):
        super(LinearLayer, self).__init__()
        
        self.cfg_model = cfg_model
        self.model = nn.ModuleList()
        
        for idx, (module, args) in enumerate(cfg_model.linear_layer['architecture']):
            layer = eval(module)(*args)
            
            self.model.append(layer)
            
    def forward(self, x):
        for layer in self.model:
            x = layer(x)
            
        return x