import math
import numpy as np
import pandas as pd


def root_mean_square_error(y_hat, y):
    
    y_hat, y = (var.values if isinstance(var, pd.core.frame.DataFrame) else var for var in (y_hat, y))
    
    y_hat = y_hat.ravel()
    y = y.ravel()
    
    return math.sqrt(np.mean((y - y_hat)**2))


def mean_absolute_error(y_hat, y):
    y_hat, y = (var.values if isinstance(var, pd.core.frame.DataFrame) else var for var in (y_hat, y))
    
    y_hat = y_hat.ravel()
    y = y.ravel()
    
    return np.mean(np.abs(y - y_hat))


def mean_absolute_percentage_error(y_hat, y):
    y_hat, y = (var.values if isinstance(var, pd.core.frame.DataFrame) else var for var in (y_hat, y))
    
    y_hat = y_hat.ravel()
    y = y.ravel()
    
    epsilon = np.finfo(float).eps
    
    return np.mean(np.abs((y - y_hat) / (y + epsilon)))    