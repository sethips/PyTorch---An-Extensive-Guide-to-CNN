import torch
import torch.optim as optim
from torch.autograd import Variable
import config as cf
import time
from fastprogress import master_bar


use_cuda = torch.cuda.is_available()

best_acc = 0

def train(epoch, net, trainloader, criterion):
    net.train()
    train_loss = 0
    correct = 0
    total = 0
    optimizer = optim.Adam(net.parameters(), lr=cf.lr, weight_decay=5e-4)

    print('\n=> Training Epoch #%d, LR=%.4f' %(epoch, cf.lr))
    for batch_idx, (inputs_value, targets) in enumerate(trainloader):
        if use_cuda:
            inputs_value, targets = inputs_value.cuda(), targets.cuda() # GPU settings
        optimizer.zero_grad()
        inputs_value, targets = Variable(inputs_value), Variable(targets)
        outputs = net(inputs_value)               # Forward Propagation
        loss = criterion(outputs, targets)  # Loss
        loss.backward()  # Backward Propagation
        optimizer.step() # Optimizer update

        train_loss += loss.data[0]
        _, predicted = torch.max(outputs.data, 1)
        total += targets.size(0)
        correct += predicted.eq(targets.data).cpu().sum()
    print ('| Epoch [%3d/%3d] \t\tLoss: %.4f Acc@1: %.3f%%'
                %(epoch, cf.num_epochs, loss.data[0], 100.*correct/total))

    return 100.*correct/total


def test(epoch, net, testloader, criterion):
    global best_acc
    net.eval()
    test_loss = 0
    correct = 0
    total = 0
    for batch_idx, (inputs_value, targets) in enumerate(testloader):
        if use_cuda:
            inputs_value, targets = inputs_value.cuda(), targets.cuda()
        with torch.no_grad():
            inputs_value, targets = Variable(inputs_value), Variable(targets)
        outputs = net(inputs_value)
        loss = criterion(outputs, targets)

        test_loss += loss.data[0]
        _, predicted = torch.max(outputs.data, 1)
        total += targets.size(0)
        correct += predicted.eq(targets.data).cpu().sum()

    # Save checkpoint when best model
    acc = 100. * correct / total
    print("\n| Validation Epoch #%d\t\t\tLoss: %.4f Acc@1: %.2f%%" % (epoch, loss.data[0], acc))

    if acc > best_acc:
        best_acc = acc
    print('* Test results : Acc@1 = %.2f%%' % (best_acc))

    return acc

def start_train_test(net,trainloader, testloader, criterion):
    elapsed_time = 0

    for epoch in range(cf.start_epoch, cf.start_epoch + cf.num_epochs):
        mb = master_bar(range( cf.start_epoch + cf.num_epochs))
        mb.names = ['training acc', 'test acc']

        start_time = time.time()

        train_acc = train(epoch, net, trainloader, criterion)
        test_acc = test(epoch, net, testloader, criterion)

        graphs = [[epoch, train_acc], [epoch, test_acc]]
        x_bounds = [0,range( cf.start_epoch + cf.num_epochs)]
        y_bounds = [0, 100]
        mb.update_graph(graphs, x_bounds, y_bounds)

        epoch_time = time.time() - start_time
        elapsed_time += epoch_time
        print('| Elapsed time : %d:%02d:%02d' % (get_hms(elapsed_time)))

def get_hms(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)

    return h, m, s
