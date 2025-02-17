import os
import numpy as np
from tqdm import tqdm

import torch
from torchvision import transforms
from torch.utils.data import DataLoader

from preprocessor.data_preparation import TimeseriesDataset, ToTensor
from utils.logger import setup_logger
from utils.utils import PROGRESS_BAR_FORMAT

LOGGER = setup_logger(__name__, 'train_workflow.log')

def evaluate(dataset, model, batch_size, device):
    
    X, y = dataset
    
    if len(X.shape) == 2:
        X = np.expand_dims(X, 0)
        
    if len(y.shape) == 2:
        y = np.expand_dims(y, 0)
    
    dataset = TimeseriesDataset(
        feat = X,
        label = y,
        transform=transforms.Compose([
            ToTensor()
        ])
    )
    
    dataloader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=0
    )
    
    pred = []
    truth = []
    
    model.to(device)
    
    print(('%20s'*3)%('Iteration', 'GPU_Mem', ''))
    with torch.no_grad():
        model.eval()
        # with tqdm(dataloader, total=len(dataloader), bar_format=PROGRESS_BAR_FORMAT, disable=True) as tq:
            
        for step, mini_batch in enumerate(dataloader):
            feat = mini_batch['feature'].to(device)
            label = mini_batch['label']
            pred_ = model(feat)
        
            pred.extend(pred_.detach().cpu().tolist())
            truth.extend(label.detach().cpu().tolist())
            
            mem = f"{torch.cuda.memory_reserved()/1E9 if torch.cuda.is_available() else 0:.3g}G"
            if step % 100 == 0:
                print(('%20s'*3)%(f"{step+1}/{len(dataloader)}", mem, " "))
                
    return pred, truth