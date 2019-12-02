x = ['a']

y = ['a', 'b', 'c']


a = x or y

if a is y:
    print('a is y')

if a is x:
    print('a is x')

print(a)