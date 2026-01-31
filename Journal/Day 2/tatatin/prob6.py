numb = input()
a,b = numb.split()
l_a = len(a)
l_b = len(b)
ld_a = a[l_a - 1]
ld_b = b[l_b - 1]
a = int(ld_a)
b = int(ld_b)
print(a+b)