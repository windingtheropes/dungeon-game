# get and return highest number in array
def get_highest_of_arr(arr=[]):
    highest = arr[0]
    for i in arr:
        if i > highest:
            highest = i
    return highest
# get and return lowest number in array
def get_lowest_of_arr(arr=[]):
    lowest = arr[0]
    for i in arr:
        if i < lowest:
            lowest = i
    return lowest
def arr_ascending(arr=[]):
    sorted = []
    while len(arr) > 0:
        highest = get_highest_of_arr(arr)
        sorted.append(highest)
        arr.remove(highest)
    return sorted
def arr_descending(arr=[]):
    sorted = []
    while len(arr) > 0:
        lowest = get_lowest_of_arr(arr)
        sorted.append(lowest)
        arr.remove(lowest)
    return sorted