import matplotlib.pyplot as plt

data = {}
dataMedia = {}
f = open("boxplot_data.csv", "r")
lines = f.readlines()
counter = 0
#while counter + 1 < len(lines):
#    keyName = lines[counter].strip()
#    list = []
#    list.append(float(lines[counter + 1].strip()))
#    list.append(float(lines[counter + 2].strip()))
#    list.append(float(lines[counter + 3].strip()))
#    list.append(float(lines[counter + 4].strip()))
#    list.append(float(lines[counter + 5].strip()))
#    data[keyName] = list
#    counter += 6
#    #break

while counter < len(lines):
    splitList = lines[counter].split(";")
    keyName = splitList[0]
    list = []
    list.append(float(splitList[1]))
    list.append(float(splitList[2]))
    list.append(float(splitList[3]))
    list.append(float(splitList[4]))
    list.append(float(splitList[5]))
    data[keyName] = list
    counter += 1

#data = { 'first': [1, 2, 3, 4, 5], 'second': [1, 4, 5, 5, 5] }
#print(data)
fig, ax = plt.subplots()
ax.boxplot(data.values())
ax.set_xticklabels(data.keys())
plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right', fontsize='x-small')
plt.show()
