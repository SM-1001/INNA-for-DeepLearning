# Example inspired from https://pytorch.org/tutorials/beginner/blitz/cifar10_tutorial.html#sphx-glr-beginner-blitz-cifar10-tutorial-py

import torch
import torchvision
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
import numpy as np

# Load Cifar 10 Dataset
transform = transforms.Compose(
[transforms.ToTensor(),
 transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])

trainset = torchvision.datasets.CIFAR10(root='./data', train=True,
                                        download=True, transform=transform)
trainloader = torch.utils.data.DataLoader(trainset, batch_size=32,
                                          shuffle=True, num_workers=2)

testset = torchvision.datasets.CIFAR10(root='./data', train=False,
                                       download=True, transform=transform)
testloader = torch.utils.data.DataLoader(testset, batch_size=32,
                                         shuffle=False, num_workers=2)

classes = ('plane', 'car', 'bird', 'cat',
           'deer', 'dog', 'frog', 'horse', 'ship', 'truck')


# Define the Network
import torch.nn as nn
import torch.nn.functional as F


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(3, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 16 * 5 * 5)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x

net = Net()


# Define the loss
import torch.optim as optim
criterion = nn.CrossEntropyLoss()

#Import and initialize INNA 

from inna import INNA

learning_rate = 0.1
alpha = 0.1 ; beta = 0.1
decaypower = 1./4

optimizer = INNA(net.parameters(), lr=learning_rate, 
    alpha=alpha, beta=beta, decaypower=decaypower)


# Train the model

nbiter = int(50000/32)
hist_loss = []

for epoch in range(6):  # loop over the dataset multiple times
    
    running_loss = 0.0
    for i, data in enumerate(trainloader, 0):
        # get the inputs; data is a list of [inputs, labels]
        inputs, labels = data
        
        # zero the parameter gradients
        net.zero_grad()
        
        # forward + compute gradient
        outputs = net(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        
        #Optimize
        optimizer.step()
        
        # print statistics
        running_loss += loss.item()
        if i % nbiter == nbiter - 1:    # print every 500 mini-batches
            print('[%d, %5d] loss: %.3f' %
                  (epoch + 1, i + 1, running_loss / nbiter))
            hist_loss.append(running_loss / nbiter)
            running_loss = 0.0
print('Finished Training')


# Plot the evolution of the log of the loss function
plt.plot( np.log10( np.concatenate(([2.30],hist_loss))  ) )
plt.xlim(0,len(hist_loss))
plt.show()