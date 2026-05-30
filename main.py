from Process import process
from Safety import safety
from System import system

p0 = process("P0", [7, 5, 3], [0, 1, 0])
p1 = process("P1", [3, 2, 2], [2, 0, 0])
p2 = process("P2", [9, 0, 2], [3, 0, 2])

available = [3, 3, 2]

system = system(available, [p0, p1, p2])
system.display_state()
print(system.request("P1", [1, 0, 2]))