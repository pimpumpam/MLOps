import os
from tqdm import tqdm

import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import transforms
from torch.utils.data import DataLoader

import mlflow

from preprocessor.data_preparation import TimeseriesDataset, ToTensor

from utils.logger import setup_logger
from utils.utils import PROGRESS_BAR_FORMAT

LOGGER = setup_logger(__name__, 'train_workflow.log')

def train(dataset, model, batch_size, num_epochs, learning_rate, device):
    """
    모델 학습

    parameter
    ----------
    dataset (tuple): input과 label array로 이루어진 tuple
    model (torch.nn):
    batch_size (int):
    num_epochs (int):
    learning_rate(float): 
    device (str):
    
    """
    X, y = dataset
    
    dataset = TimeseriesDataset(
        feat=X,
        label=y, 
        transform=transforms.Compose([
            ToTensor()
        ])
    )
    
    dataloader = DataLoader(
        dataset, 
        batch_size=batch_size, 
        shuffle=True,
        num_workers=0
    )
    
    model.to(device)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    
    # LOGGER.info(('%20s'*3)%('Epoch', 'GPU_Mem', 'Loss'))
    print(('%20s'*3)%('Epoch', 'GPU_Mem', 'Loss'))
    for epoch in range(num_epochs):
        model.train()    
        with tqdm(dataloader, total=len(dataloader), bar_format=PROGRESS_BAR_FORMAT) as tq:
                for step, mini_batch in enumerate(tq):
                    
                    optimizer.zero_grad()
                    feat = mini_batch['feature'].to(device)
                    label = mini_batch['label'].to(device)
                    pred = model(feat)
                    
                    loss = criterion(pred, label)
                    loss.backward()
                    optimizer.step()
                    
                    mem = f"{torch.cuda.memory_reserved()/1E9 if torch.cuda.is_available() else 0:.3g}G"
                    tq.set_description(('%20s'*3)%(f"{epoch+1}/{num_epochs}", mem, f"{loss.item():.4}"))
                    # LOGGER.info(('%20s'*3)%(f"{epoch+1}/{num_epochs}", mem, f"{loss.item():.4}"))


def setup_experiment(experiment_name, artifact_location):
    
    try:
        mlflow.create_experiment(
            experiment_name, 
            artifact_location=artifact_location
        )

        LOGGER.info(
            f"🧪 Experiment {experiment_name} is not Exist. \
            Create Experiment."
        )
    except:
        LOGGER.info(
            f"🧪 Experienmt {experiment_name} is Already Exist. \
            Execute Run on the \"{experiment_name}\"."
        )
            
    # set experiment
    mlflow.set_experiment(experiment_name)