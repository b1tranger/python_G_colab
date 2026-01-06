# 1st try

# n = input()
# n = int(n)
# ans = (n * (n + 1) / 2)
# ans = int(ans)
# print(ans)
# Doesn't round up

# 2nd try

# n = input()
# n = int(n)
# ans = 0
# for tin in range(1,n+1):
#     ans += tin 
# print(ans)
# Takes too long

# 3rd try

n = input()
n = int(n)
ans = (n * (n + 1) // 2)
ans = int(ans)
print(ans)
# Works "//" makes it so that the division occurs in a way such that only the integers are accounted for and the floats are ignored in the same way how women ignore me