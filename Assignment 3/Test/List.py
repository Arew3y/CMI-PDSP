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

    def insertold(self,v): # Renamed the function to use later
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
        #
    def member(self, v):
        # Iteratively we will check if the element exists or not till we reach the end
        temp = self

        if temp.isempty(): return False # Raincheck for empty list
        if temp.value == v: return True # Checking first value

        while temp.next != None:
            temp = temp.next
            if temp.value == v: return True
        else: return False
        #
    def __len__(self): # Defining a length function
        temp = self
        if temp.isempty(): return 0
        i = 1
        while temp.next != None:
            i = i + 1
            temp = temp.next
        return i
        #
    def valueat(self,i):
        length = len(self)
        temp = self
        # Running value validation on received input
        if i >= length or i < -length:
            raise IndexError(f"Index {i} is out of range")

        if i < 0: # Balancing the negative indices
            i = length + i

        while i != 0: # Iteratively going through the list till we reach the i^th element
            temp = temp.next
            i = i - 1

        return temp.value
        #
    def insert(self,v,i=0):
        length = len(self)
        temp = self
        # Running value validation on received input
        if i > length or i < 0:
            raise IndexError(f"Index {i} is out of range")

        if i == length:
            self.append(v)
            return

        while i != 0: # Iteratively going through the list till we reach the i^th element
            temp = temp.next
            i = i - 1

        temp.insertold(v)
        return
        #
    def deletelast(self,v):
        length = len(self)

        temp = self
        lastNode = None

        for i in range(length):
            if temp.value == v:
                lastNode = temp
            temp = temp.next

        if lastNode == None:
            raise ValueError(f"Value {v} doesn't exist")
        else:
            lastNode.delete(v)

        return
        #
    def slice(self,i,j):
        length = len(self)
        temp = self

        def cleanindex(i,n):
            if i < 0:
                if i >= - n: i = n + i
                else: i = 0
            if i > n: i = n
            return(i)

        i , j = cleanindex(i,length), cleanindex(j,length)
        print(i,j)
        if j < i: return List()
        for a in range(i): temp = temp.next

        newList = List()
        for a in range(j-i):
            newList.append(temp.value)
            temp = temp.next

        return newList
        #
    def rotate(self,k):
        length = len(self)
        temp = self

        def rot_one(lst, n):
            temp1 = lst
            temp2 = lst.value
            temp3 = None

            for i in range(n-1):
                # lst.next.value, temp1 = temp1.value, lst.next
                lst = lst.next
                temp3 = lst.value
                lst.value = temp2
                temp2 = temp3

            temp1.value = temp2
            return

        for i in range(k): rot_one(temp, length)

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