import math
n1,n2 = map(int, input().split())
n= n1/n2
rounded = math.floor(n + 0.5)
floored = math.floor(n)
ceiling = math.ceil(n)

print(f"floor {n1} / {n2} = {floored}\nceil {n1} / {n2} = {ceiling}\nround {n1} / {n2} = {rounded}")