#Date: 02/24/2017
#Author: Sean Kinahan
#Python v. 3.6.0

#Instructions:
#Write a function that takes two lists as input and produces one list as output. The function should have the signature `def apply_port_exclusions(include_ports, exclude_ports)`.
#The function should expect that the input lists will be a list of low-high pairs which are lists of length two. The function should return a minimized and ordered list of include port ranges
#that result after processing the exclude port ranges.
#Include whatever tests and comments you normally provide for completed code.​  Additionally, provide a solution that is performant comparing 10000 ranges to 10000 ranges.

#Class to represent an interval
class Interval:
    def __init__(self, intLow, intHigh):
        assert intLow <= intHigh
        self.low = intLow
        self.high = intHigh

#Check if intervals i1 and i2 overlap
def doOverlap(i1, i2):
    return (i1.low <= i2.high and i2.low <= i1.high)

#Class to represent a node in an IST (interval search tree)
class INode:
    def __init__(self, interval, left, right):
        self.Interval = interval
        self.left = left
        self.right = right
        self.max = interval.high
    def in_order(self):
        if self.left is not None:
            for value in self.left.in_order():
                yield value
        yield [self.Interval.low, self.Interval.high]
        if self.right is not None:
            for value in self.right.in_order():
                yield value
    def delete(self, i):       
        if ((self.Interval.low == i.low) and (self.Interval.high == i.high)):
            if self.left and self.right:
                [psucc, succ] = self.right._findMin(self)
                if psucc.left == succ:
                    psucc.left = succ.right
                else:
                    psucc.right = succ.right
    
                succ.left = self.left
                succ.right = self.right
    
                return succ
            else:
                if self.left:
                    return self.left
                else:
                    return self.right
        else:
            if self.Interval.high > i.high:
                if self.left:
                    self.left = self.left.delete(i)
            else:
                if self.right:
                    self.right = self.right.delete(i)
        return self
    def _findMin(self, parent):
        if self.left:
            return self.left._findMin(self)
        else:
            return[parent, self]

#Helper function to create a new node based on interval i
def newNode(i):
    return INode(i, None, None)

#Insert interval i into the tree
def insert(root, i):
    #Base case, we have either reached a leaf or are starting a new IST
    if root is None:
        return newNode(i)
    l = root.Interval.low
    if i.low < l:
        #Recurse to the left
        root.left = insert(root.left, i)
    else:
        #Recurse to the right
        root.right = insert(root.right, i)
    #Update the max value seen at this node if needed
    if root.max < i.high:
        root.max = i.high
    return root

#Search the tree to see if interval i overlaps
def overlapSearch(root, i):
    #Base case, overlap not found or tree is empty
    if root is None:
        return None

    #Check if interval overlaps with this node
    if doOverlap(root.Interval, i):
        return root
    
    #If left child of node exists and max of left child is greater than or equal to interva, then go left
    if (root.left is not None) and (root.left.max >= i.low):
        return overlapSearch(root.left, i)
    else:
        return overlapSearch(root.right, i)
  
#Perform an in-order traversal of the IST and pretty-print the result --- Only used for early testing purposes, in_order() method of INode works better
def inOrderTraversalPrint(root):
    if root is None:
        return
    inOrderTraversalPrint(root.left)
    print("[",root.Interval.low,", ",root.Interval.high,"]")
    inOrderTraversalPrint(root.right)

#Helper function to do a final pass and detect and combine adjacent port ranges
def minimize(result):
    finalAnswer = []
    trailingMin = None
    currentMax = None
    for idx, val in enumerate(result):
        if trailingMin is None:
            trailingMin = val[0]
            currentMax = val[1]
        else:
            if val[0] == currentMax + 1:
                currentMax = val[1]
            else:
                finalAnswer.append([trailingMin, currentMax])
                trailingMin = val[0]
                currentMax = val[1]
        if idx == len(result)-1:
            finalAnswer.append([trailingMin, currentMax])
    return finalAnswer

#Function to apply port exclusions. Builds a binary IST from included ports and then prunes/modifies it based on excluded ports.
def apply_port_exclusions(include_ports, exclude_ports):
    #build interval tree of include ports
    root = None
    if len(include_ports) == 0:
        return []
    for val in include_ports:
        interval = Interval(val[0], val[1])
        root = insert(root, interval)
    #print(list(root.in_order()))
    #check for overlaps with exclude_ports
    tree_changed = True
    while tree_changed:
        tree_changed = False
        for val in exclude_ports:
            exclInterval = Interval(val[0], val[1])
            collisionNode = overlapSearch(root, exclInterval)
            if not collisionNode is None:
                tree_changed = True
                #where collisions occur, handle by deleting node and creating 0, 1, or 2 new intervals as necessary
                #print('Collision detected at interval: ',collisionNode.Interval.low,collisionNode.Interval.high, sep=' ')
                exclLow = val[0]
                exclHigh = val[1]
                inclLow = collisionNode.Interval.low
                inclHigh = collisionNode.Interval.high
                if (inclLow < exclLow) and (inclHigh > exclHigh):
                    #split into two intervals
                    root = root.delete(collisionNode.Interval)
                    span1 = Interval(inclLow, exclLow-1)
                    span2 = Interval(exclHigh+1, inclHigh)
                    root = insert(root, span1)
                    root = insert(root, span2)
                elif (inclLow < exclLow) and (inclHigh <= exclHigh):
                    #shorten interval (bring down interval high)
                    root = root.delete(collisionNode.Interval)
                    span = Interval(inclLow, exclLow-1)
                    root = insert(root, span)
                elif (inclLow >= exclLow) and (inclHigh > exclHigh):
                    #shorten interval (bring up interval low)
                    root = root.delete(collisionNode.Interval)
                    span = Interval(exclHigh+1, inclHigh)
                    root = insert(root, span)
                elif (inclLow > exclLow) and (inclHigh < exclHigh):
                    #exclude entirely
                    root = root.delete(collisionNode.Interval)
    return minimize(list(root.in_order()))
    
#======================================Test Cases===================================================

#Test valid Interval creation
def testInterval():
    i = Interval(0, 40)
    assert i.low == 0
    assert i.high == 40
    x = Interval(8080, 8081)
    assert x.low == 8080
    assert x.high == 8081
    print("Interval creation test passed...")

#Test creation of 100000 intervals
def bigTestInterval():
    intervalList =[ Interval(x,x+100) for x in range(0, 100000)]
    for idx in range (0, 100000):
        interval = intervalList[idx]
        assert interval.low == idx
        assert interval.high == idx+100
    print("Big Interval creation test passed...")

#Test invalid Interval creation
def testInvalidInterval():
    #Invalid interval, should raise AssertionError()
    try:
        j = Interval(90000, 10)
    except AssertionError:
        print("Interval validity check passed...")    

#Test overlap function on a few cases
def overlapTest():
    x = Interval(20, 40)
    x1 = Interval(30, 50)
    x2 = Interval(10, 30)
    x3 = Interval(0, 60)
    x4 = Interval(20, 40)
    x5 = Interval(100, 500)
    assert doOverlap(x, x1)
    assert doOverlap(x, x2)
    assert doOverlap(x, x3)
    assert doOverlap(x, x4)
    assert not doOverlap(x, x5)
    assert not doOverlap(x1, x5)
    assert not doOverlap(x2, x5)
    assert not doOverlap(x3, x5)
    assert not doOverlap(x4, x5)
    print("Simple overlap test passed....")

#Test overlap function on large number of intervals
def bigOverlapTest():
    intervalList =[ Interval(x,x+100) for x in range(0, 100000)]
    for idx in range (0, 100000):
        if idx < 99999:
            assert doOverlap(intervalList[idx],intervalList[idx+1])
    print("Big overlap check passed...")
    
def runIntervalTests():
    print("Running interval tests...")
    testInterval()
    testInvalidInterval()
    bigTestInterval()

def runOverlapTests():
    print("Running overlap tests...")
    overlapTest()
    bigOverlapTest()

#class to test INode creation and left/right assignment
def testINode():
    i = Interval(0, 40)
    node = INode(i, None, None)
    assert node.max == i.high
    assert node.left is None
    assert node.right is None
    x = Interval(20, 8000)
    node2 = INode(x, node, node)
    assert node2.max == x.high
    assert node2.left == node
    assert node2.right == node
    print("Simple INode creation test passed...")

#Test creation of INodes, 
def bigINodeTest():
    nextLeft = None
    expectedLeft = None
    iNodes = []
    for x in range(0, 100000):
        i = Interval(x, x+100)
        iNode = INode(i, nextLeft, None)
        nextLeft = iNode
        if x > 0:
            iNodes[x-1].right = iNode
        iNodes.append(iNode)
    for x in range(0, 100000):
        iNode = iNodes[x]    
        if x > 0:
            assert iNode.left == iNodes[x-1]
        if x < 99999:
            assert iNode.right == iNodes[x+1]
    print("Big INode creation test passed...")

#Test creation of leaf nodes with helper function
def leafNodeTest():
    interval = Interval(600, 1200)
    leaf = newNode(interval)
    assert leaf.left is None
    assert leaf.right is None
    assert leaf.Interval.low == interval.low
    assert leaf.Interval.high == interval.high
    print("Leaf node creation test passed...")

def deletionTest():
    interval = Interval(600, 1200)
    interval2 = Interval(500, 800)
    root = newNode(interval)
    root = insert(root, interval2)
    root = root.delete(interval2)
    result = list(root.in_order())
    assert result == [[600, 1200]]
    print("Node deletion test passed...")

def runINodeTests():
    testINode()
    leafNodeTest()
    bigINodeTest()
    deletionTest()

def runAllTests():
    runIntervalTests()
    runOverlapTests()
    runINodeTests()
    apeTest1()
    apeTest2()
    apeTest3()
    apeTest4()
    apeTest5()
    
#input:
    #include_ports: [[80, 80], [22, 23], [8000, 9000]]
    #exclude_ports: [[1024, 1024], [8080, 8080]]
#output:
    #[[22, 23], [80, 80], [8000, 8079], [8081, 9000]]            
def apeTest1():
    include_ports = [[80, 80], [22, 23], [8000, 9000]]
    exclude_ports = [[1024, 1024], [8080, 8080]]
    result = (apply_port_exclusions(include_ports, exclude_ports))
    assert result == [[22, 23], [80, 80], [8000, 8079], [8081, 9000]]
    print('Provided test case 1 passed...')

#input:
    #include_ports: [[8000, 9000], [80, 80], [22, 23]]
    #exclude_ports: [[1024, 1024], [8080, 8080]]
#output:
    #[[22, 23], [80, 80], [8000, 8079], [8081, 9000]]
def apeTest2():
    include_ports = [[8000, 9000], [80, 80], [22, 23]]
    exclude_ports = [[1024, 1024], [8080, 8080]]
    result = (apply_port_exclusions(include_ports, exclude_ports))
    assert result == [[22, 23], [80, 80], [8000, 8079], [8081, 9000]]
    print('Provided test case 2 passed...')

#input:
    #include_ports: [[1,65535]]
    #exclude_ports: [[1000,2000], [500, 2500]]
#output:
    #[[1, 499], [2501, 65535]]
def apeTest3():
    include_ports = [[1,65535]]
    exclude_ports = [[1000,2000], [500, 2500]]
    result = (apply_port_exclusions(include_ports, exclude_ports))
    assert result == [[1, 499], [2501, 65535]]
    print('Provided test case 3 passed...')

#input:
    #include_ports: [[1,1], [3, 65535], [2, 2]]
    #exclude_ports: [[1000, 2000], [500, 2500]]
#output:
    #[[1, 499], [2501, 65535]]
def apeTest4():
    include_ports = [[1,1], [3, 65535], [2, 2]]
    exclude_ports = [[1000, 2000], [500, 2500]]
    result = (apply_port_exclusions(include_ports, exclude_ports))
    assert result == [[1, 499], [2501, 65535]]
    print('Provided test case 4 passed...')

#input:
    #include_ports: []
    #exclude_ports: [[8080, 8080]]
#output:
    #[]
def apeTest5():
    include_ports = []
    exclude_ports = [[8080, 8080]]
    result = (apply_port_exclusions(include_ports, exclude_ports))
    assert result == []
    print('Provided test case 5 passed...')
    
if __name__ == "__main__":
    runAllTests()

