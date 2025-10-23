class List:
    def __init__(self,initlist = []):
        self.value = None
        self.next = None
        for x in initlist:
            self.append(x)
        return

    def isempty(self):
        return(self.value == None)
    
    def appendi(self,v):   # append, iterative
        if self.isempty():
            self.value = v
            return
        
        temp = self
        while temp.next != None:
            temp = temp.next

        temp.next = List()
        temp.next.value = v 
        return

    def appendr(self,v):   # append, recursive
        if self.isempty():
            self.value = v
        elif self.next == None:
            self.next = List([v])
        else:
            self.next.appendr(v)
        return

    def append(self,v):
        self.appendr(v)
        return

    def insert(self,v):
        if self.isempty():
            self.value = v
            return

        newnode = List()
        newnode.value = v
        
        # Exchange values in self and newnode
        (self.value, newnode.value) = (newnode.value, self.value)

        # Switch links
        (self.next, newnode.next) = (newnode, self.next)

        return

    def delete(self,v):   # delete, recursive
        if self.isempty():
            return

        if self.value == v:
            if self.next != None:
                self.value = self.next.value
                self.next = self.next.next
            else:
                self.value = None
            return
        else:
            if self.next != None:
                self.next.delete(v)
                # Ensure that there is no empty node at the end of the list
                if self.next.value == None:
                    self.next = None
        return
    
    def __str__(self):
        # Iteratively create a Python list from linked list
        # and convert that to a string
        selflist = []
        if self.isempty():
            return(str(selflist))

        temp = self
        selflist.append(temp.value)
        
        while temp.next != None:
          temp = temp.next
          selflist.append(temp.value)

        return(str(selflist))

