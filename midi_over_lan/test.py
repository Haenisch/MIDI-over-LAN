from dataclasses import dataclass, field
from typing import ClassVar

@dataclass
class A:
    counter: ClassVar[int] = 0
    id: int = field(init=False)

    def __init__(self):
        self.id = A.counter
        A.counter += 1

a1 = A()
print(a1.id)

a2 = A()
print(a2.id)

a2 = A()
print(a2.id)

print(a2.counter)
a2.counter = 0
print(a2.counter)
a2 = A()
print(a2.id)

A.counter = 0
print(A.counter)
a2 = A()
print(a2.id)
