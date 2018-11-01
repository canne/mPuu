#!/home/makijarv/usr/bin/python

class crawl:
    def __init__( self, depth=1, node=1 ):
        print "crawl.__init__(), depth =", depth, ", node =", node
        self.depth = depth
        self.node = node
        self.newInstances = []
        branchOffset = 0
        if self.depth < 4:
                for i in range(1,self.depth+1):
                    print "crawl.__init__(), depth =", depth, ", node =", node, ": i =",i
                    self.newInstances.append( crawl( depth+1, node+i+branchOffset) )
                    branchOffset = self.newInstances[i-1].branchNodes()
                    print "crawl.__init__(), depth =", depth, ", node =", node,\
                          ": child branch nodes  =", branchOffset
        print "crawl.__init__(), depth =", depth, ", node =", node, ": - done: branch depth: ",\
              self.branchMaxDepth() - self.depth

    def branchNodes( self ):
        retval = 0;
        for i in range(0,len(self.newInstances)):
            retval += self.newInstances[0].branchNodes()
        retval += len(self.newInstances)
        return retval

    def branchMaxDepth( self ):
        retval = self.depth;
        for i in range(0,len(self.newInstances)):
            newDepth = self.newInstances[0].branchMaxDepth()
            if newDepth > retval: retval = newDepth
        return retval        

test = crawl()

