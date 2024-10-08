# -*- coding: utf-8 -*-
"""utils.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/11FAxoZNXXZmQxybtOtvnwfO8En3nOJ-y
"""

# all libraries
import torch
from torch import nn
import torchvision
from torchvision import datasets
from torchvision.transforms import ToTensor
from torchvision import transforms
from torchinfo import summary
from torch.utils.data import DataLoader

from timeit import default_timer as timer
from tqdm.auto import tqdm

import matplotlib.pyplot as plt
import numpy as np

torch.manual_seed(1)
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"device: {device}")

# data setup
def setup_dataloaders(auto_transforms, batch_size, num_workers):
    # Importing data
    train_data = datasets.CIFAR10(
        root="data",
        train=True,
        download=True,
        transform=auto_transforms,
        target_transform=None
    )

    test_data = datasets.CIFAR10(
        root="data",
        train=False,
        download=True,
        transform=auto_transforms
    )

    #Setting up data loaders
    train_dataloader = DataLoader(train_data, batch_size=batch_size, shuffle=True, num_workers=2)
    test_dataloader = DataLoader(test_data, batch_size=batch_size, shuffle=False, num_workers=2)
    print(f"Train dataloader: {len(train_dataloader)} batches of size {batch_size}")
    print(f"Test dataloader: {len(test_dataloader)} batches of size {batch_size}")

    print(f"Training data length: {len(train_data.data)}, Testing data length: {len(test_data.data)}")
    return train_dataloader, test_dataloader

# some functions
def print_train_time(start: float, end: float, device: torch.device = None):
  total_time = end - start
  print(f"Train time on {device}: {total_time:.3f} seconds")
  return total_time

def accuracy_fn(pred, true):
    return 100*sum(pred == true) / len(true)

#Training and testing steps
def train_step(model: torch.nn.Module, data_loader: torch.utils.data.DataLoader, loss_fn: torch.nn.Module, optimizer: torch.optim.Optimizer, accuracy_fn, device: torch.device = device):
    train_loss, train_acc = 0, 0
    model.to(device)
    model.train()
    size = len(data_loader)

    for batch, (X, y) in enumerate(data_loader):
        X, y = X.to(device), y.to(device)
        y_pred = model(X)
        loss = loss_fn(y_pred, y)
        train_loss += loss/size
        train_acc += accuracy_fn(true=y, pred=y_pred.argmax(dim=1))/size
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    print(f"Train loss: {train_loss:.5f} | Train accuracy: {train_acc:.2f}%")
    return train_acc, train_loss

def test_step(data_loader: torch.utils.data.DataLoader, model: torch.nn.Module, loss_fn: torch.nn.Module, accuracy_fn, device: torch.device = device):
    test_loss, test_acc = 0, 0
    model.to(device)
    model.eval()
    size = len(data_loader)

    with torch.inference_mode():
        for X, y in data_loader:
            X, y = X.to(device), y.to(device)
            test_pred = model(X)
            test_loss += loss_fn(test_pred, y)/size
            test_acc += accuracy_fn(true=y, pred=test_pred.argmax(dim=1))/size

    print(f"Test loss: {test_loss:.5f} | Test accuracy: {test_acc:.2f}%\n")
    return test_acc, test_loss