import os
import sys
import argparse
from pathlib import Path

import mlflow

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]
sys.path.append(str(ROOT))

from core.load import Loader
from core.train import Trainer
from core.preprocess import Preprocessor
from core.evaluate import Evaluator
from core.inference import Inferer
from core.monitor import Monitor
from utils.utils import load_spec_from_config


class Run:
    def __init__(self, config_name):
        (
            self.cfg_meta,
            self.cfg_database,
            self.cfg_loader,
            self.cfg_preprocessor,
            self.cfg_model,
            self.cfg_hyp,
            self.cfg_train,
            self.cfg_evaluate,
            self.cfg_inference
        ) = load_spec_from_config(config_name)
        
        mlflow.set_tracking_uri(self.cfg_meta.mlflow['DASHBOARD_URL'])

    def load(self):
        loader = Loader(
            self.cfg_meta,
            self.cfg_database,
            self.cfg_loader
        )
        loader.run()
        

    def preprocess(self):
        preprocessor = Preprocessor(
            self.cfg_meta, 
            self.cfg_database, 
            self.cfg_loader, 
            self.cfg_preprocessor
        )
        preprocessor.run()

    def train(self):
        trainer = Trainer(
            self.cfg_meta,
            self.cfg_database,
            self.cfg_preprocessor,
            self.cfg_model,
            self.cfg_hyp,
            self.cfg_train
        )
        trainer.run()

    def evaluate(self):
        evaluator = Evaluator(
            self.cfg_meta,
            self.cfg_database,
            self.cfg_preprocessor,
            self.cfg_evaluate
        )
        evaluator.run()
        
    def inference(self):
        inferer = Inferer(
            self.cfg_meta,
            self.cfg_database,
            self.cfg_preprocessor,
            self.cfg_evaluate,
            self.cfg_inference
        )
        inferer.run()
        
    def monitoring(self):
        monitor = Monitor(
            self.cfg_meta,
            self.cfg_database,
            self.cfg_inference
        )
        condition = monitor.run()

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="dlinear", help="Config Python 파일 명. 확장자 제외.")
    args = parser.parse_args() 

    runner = Run(args.config)   

    # loading
    runner.load() 

    # preprocessing
    runner.preprocess()

    # training
    runner.train() 
    
    # evaluating
    runner.evaluate()  

    # inferencing
    #runner.inference()
    
