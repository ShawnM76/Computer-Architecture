dic = {
    "cat": "bob",
    "dog": 23,
    19: 18,
    90: "fish"
}

# add just the values of integers
# to first check if the value is a string or an integer
# take that integer and add it to a list /additonial
# Then add all the integers together and return the sum


def add(dictionary):
    list = []
    for k in dictionary:
        value = dictionary.get(k)
        if value == '':
            return
        if isinstance(value, int):
            list.append(value)
    print(sum(list))


add(dic)
