import sys
import numpy as np
from operator import attrgetter

class Result:
    def __init__(self, tag, result):
        self.tag = tag
        self.result = result

    def print(self):
        print(f"{self.tag} {self.result}")


class Connection:
    def __init__(self, length):
        self.slots = np.zeros(320)
        self.length = length

    def free(self, taskId):
        for i in range(len(self.slots)):
            if self.slots[i] == taskId:
                self.slots[i] = 0


class Route:
    def __init__(self, startNodeId, stopNodeId, connections, length):
        self.startNodeId = startNodeId
        self.stopNodeId = stopNodeId
        self.connections = connections
        self.length = length

    def print(self):
        print(
            f"StartNodeId: {self.startNodeId}, StopNodeId: {self.stopNodeId}, connections: {self.connections}, length: {self.length}")


class Task:
    def __init__(self, id, startTime, stopTime, startNodeId, stopNodeId, bitrate):
        self.id = id
        self.startTime = startTime
        self.stopTime = stopTime
        self.startNodeId = startNodeId
        self.stopNodeId = stopNodeId
        self.bitrate = bitrate
        self.connections = []

    def print(self):
        print(
            f"Id: {self.id}, StartTime: {self.startTime}, StopTime: {self.stopTime}, StartNodeId: {self.startNodeId}, StopNodeId: {self.stopNodeId}, Bitrate: {self.bitrate}, Connections: {self.connections}")

    def addRoute(self, connections):
        self.connections = connections


class Modulation:
    def __init__(self, name, maxLength, bitrate, slots):
        self.name = name
        self.maxLength = maxLength
        self.bitrate = bitrate
        self.slots = slots

    def print(self):
        print(f"Name: {self.name}, MaxLength: {self.maxLength}, Bitrate: {self.bitrate}, Slots: {self.slots}")


def checkModulation(bitrate, length):
    if bitrate == 800:
        if length <= 200:
            return [9]
        elif length <= 800:
            return [6, 6]
        else:
            return [9, 9]
    elif bitrate == 600:
        if length <= 1600:
            return [9]
        else:
            return [6, 6, 6]
    elif bitrate == 400:
        if length <= 800:
            return [6]
        else:
            return [9]
    else:
        return [6]


def allocateConnections(connsArr, slotsQuantity, slotsGroups, taskId):
    slotIds = []
    lastIndex = 0
    for group in range(slotsGroups):
        for slotId in range(lastIndex, len(connections[0].slots) - slotsQuantity):
            sum = 0
            for connId in connsArr:
                sum += checkSlotGroup(connId, slotId, slotsQuantity)
            if sum == 0:
                lastIndex = slotId + slotsQuantity;
                slotIds.append(slotId)
                break
    if len(slotIds) == slotsGroups:
        for connId in connsArr:
            for slotId in slotIds:
                for i in range(slotsQuantity):
                    connections[connId].slots[slotId + i] = taskId
        return True
    else:
        return False


def checkSlotGroup(connId, slotId, slotsQuantity):
    sum = 0
    for i in range(slotsQuantity):
        sum += connections[connId].slots[slotId + i]
    return sum


def runTest(k, factor, fileSet):
    time = 0
    rejectedTasks = 0
    bbp = 0
    sumOfRejectedBitrate = 0
    sumOfAllBitrate = 0
    connections.clear()
    routes.clear()
    alltasks.clear()
    availableTasks = []
    startedTasks = []
    modulations.clear()

    file1 = open(fileSet[0], 'r').read()
    lines = file1.split('\n')
    nodeQuantity = int(lines[0])
    connectionQuantity = int(lines[1])
    linesQuantity = len(lines)

    for x in range(2, linesQuantity):
        fields = lines[x].split()
        for field in fields:
            if int(field) != 0:
                connections.append(Connection(int(field)))

    file2 = open(fileSet[1], 'r').read()
    lines = file2.split('\n')
    lines.remove(lines[0])
    tmp = 0;
    for a in range(nodeQuantity):
        for b in range(nodeQuantity):
            if a != b:
                for c in range(k):
                    conns = lines[tmp + c].split()
                    connsArr = []
                    length = 0
                    for d in range(len(conns)):
                        if int(conns[d]) == 1:
                            connsArr.append(int(d))
                            length = length + connections[d].length
                    routes.append(Route(a, b, connsArr.copy(), length))
                tmp = tmp + 30

    file3 = open(fileSet[2], 'r').read()
    lines = file3.split('\n')
    taskQuantity = int(lines[0])
    lines.remove(lines[0])
    data = lines[0].split()
    alltasks.append(
        Task(taskQuantity, int(data[0]), int(factor * int(data[1]) + int(data[0])), int(data[2]), int(data[3]),
             int(data[4])))
    for l in range(1, taskQuantity):
        data = lines[l].split()
        alltasks.append(
            Task(l, int(data[0]), int(factor * int(data[1]) + int(data[0])), int(data[2]), int(data[3]), int(data[4])))

    modulations.append(Modulation("QPSK", sys.maxsize, 200, 6))
    modulations.append(Modulation("8QAM", sys.maxsize, 400, 9))
    modulations.append(Modulation("16QAM", 800, 400, 6))
    modulations.append(Modulation("16QAM", 1600, 600, 9))
    modulations.append(Modulation("32QAM", 200, 800, 9))

    while len(alltasks) > 0 or len(availableTasks) > 0 or len(startedTasks) > 0:
        # delete all completed tasks
        completedTasks = []

        for task in startedTasks:
            if task.stopTime == time:
                for connId in task.connections:
                    connections[connId].free(task.id)
                completedTasks.append(task)

        for task in completedTasks:
            startedTasks.remove(task)

        completedTasks.clear()

        # move all ready to start tasks to availableTasks
        for task in alltasks:
            if task.startTime == time:
                availableTasks.append(task)
                sumOfAllBitrate += task.bitrate

        for i in range(len(availableTasks)):
            alltasks.remove(alltasks[0])

        # sort availableTasks by bitrate descending
        availableTasks.sort(key=attrgetter("bitrate"), reverse=True)

        # find possible routes
        for task in availableTasks:
            possibleRoutes = list(
                filter(lambda route: route.startNodeId == task.startNodeId and route.stopNodeId == task.stopNodeId,
                       routes))

            for route in possibleRoutes:
                slots = checkModulation(task.bitrate, route.length)
                if allocateConnections(route.connections, slots[0], len(slots), task.id) == True:
                    task.addRoute(route.connections)
                    startedTasks.append(task)
                    break
            if not task.connections:
                rejectedTasks += 1
                sumOfRejectedBitrate += task.bitrate

        availableTasks.clear()

        # increment time
        time += 1

    bbp = sumOfRejectedBitrate / sumOfAllBitrate

    return rejectedTasks, bbp


k = 2
factors = [1, 1.5, 2, 2.5, 3]
fileSets = [
    ['euro28.net.txt', 'euro28.pat.txt', 'euro28.ddem.txt', 'euro28'],
    ['us26.net.txt', 'us26.pat.txt', 'us26.ddem.txt', 'us26']
]
rejected = []
bbpArr = []
table = []
table2 = []
connections = []
routes = []
alltasks = []
modulations = []

table.append(Result('factor', factors))
for fileSet in fileSets:
    rejected.clear()
    bbpArr.clear()
    for factor in factors:
        rej, bbp = runTest(k, factor, fileSet)
        rejected.append(rej)
        bbpArr.append(bbp)
    table.append(Result(fileSet[3], rejected.copy()))
    table.append(Result("bbp", bbpArr.copy()))

print(f"Number of routes per pair of nodes k={k}")
for t in table:
    t.print()

print("===========================================")

k = 4
table2.append(Result('factor', factors))
for fileSet in fileSets:
    rejected.clear()
    bbpArr.clear()
    for factor in factors:
        rej, bbp = runTest(k, factor, fileSet)
        rejected.append(rej)
        bbpArr.append(bbp)
    table2.append(Result(fileSet[3], rejected.copy()))
    table2.append(Result("bbp", bbpArr.copy()))

print(f"Number of routes per pair of nodes k={k}")
for t in table2:
    t.print()


