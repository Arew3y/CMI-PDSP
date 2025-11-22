class Node:
    def __init__(self, v=None):
        self.value = v
        self.left = None
        self.right = None
        self.tag = "L"

    def find(self, v: int):
        if self.value is None:
            return False
        elif self.tag == "I":
            if v < self.value:
                return self.left.find(v)
            else:
                return self.right.find(v)
        elif self.value == v and self.tag == "L":
            return True
        else:
            return False

    def insert(self, v: int):
        if self.value is None:
            self.value = v
            return None
        elif self.tag == "I":
            if v < self.value:
                return self.left.insert(v)
            else:
                return self.right.insert(v)
        elif self.tag == "L":
            if v < self.value:
                self.left = Node(v)
                self.right = Node(self.value)
                self.tag = "I"
                return None
            else:
                self.left = Node(self.value)
                self.right = Node(v)
                self.value = v
                self.tag = "I"
                return None
        else:
            raise ValueError(f"Invalid tag: {self.tag}.")

    def deletea(self, v, intnode = None, prev = None):
        if self.tag == "I":
            if v < self.value:
                return self.left.deletea(v, intnode, self)
            else:
                if v == self.value:
                    intnode = self
                return self.right.deletea(v, intnode, self)
        elif self.tag == "L":
            if v == self.value:
                if prev is None:
                    self.value = None
                    return None
                elif prev.value is not self.value:
                    prev.tag = prev.right.tag
                    prev.left = prev.right.left
                    prev.right = prev.right.right
                    if intnode is not None:
                        intnode.value = prev.value
                    return None
                elif prev.value is self.value:
                    prev.tag = prev.left.tag
                    prev.value = prev.left.value
                    prev.right = prev.left.right
                    prev.left = prev.left.left
                    return None
                else: return None
            else: return None
        else: return None

    def delete(self, v):
        return self.deletea(v)

    def strarr(self):
        if self.tag == "I":
            return self.left.strarr() + [(self.tag,self.value)] + self.right.strarr()
        else:
            return [(self.tag,self.value)]

    def __str__(self):
        return str(self.strarr())