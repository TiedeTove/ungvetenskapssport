import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ebas = pd.read_csv("ebas.mars.csv", delimiter=";", encoding="latin1") #skriv lämplig filsökväg
ebas.head()

ebas['Inskriven'] = pd.to_datetime(ebas['Inskriven'])
ebas.sort_values(by='Inskriven')

target_föreningar = ['Kodsport Sverige', 'Lingolympiaden', 'Ung Vetenskapssports Astronomer', 'Ung Vetenskapssports Biologer', 'UVS Kemister', 'Ung Vetenskapssports Fysiker', 'Ung Vetenskapssports Ingenjörer', 'Ung Vetenskapssports Matematiker']
i = 0
target_month = 1  

data = np.zeros((8, 3))

while target_month <=3:
    for target_förening in target_föreningar:
        if i < 8:
            count = ((ebas['Förening'] == target_förening) & (ebas['Inskriven'].dt.month == target_month)).sum()
            data[i][target_month-1] = data[i][target_month-2]+count
            i += 1
    i = 0
    target_month += 1

föreningar = ['KS', 'Lingo', 'Astro', 'Biologi', 'Kemi', 'Fysik', 'Ingenjör', 'Matte']
colors = ['#7fd3ff', 'lightgray', '#fff4bc', '#81c1a0', '#ec7485', 'dimgrey', '#64a7cb', '#ffd084']
newcolors = ['#00A6FD', 'dimgray', '#FFD500', '#01A852', '#ED344F', 'black', '#0082C8', '#FEB132']


months = ['Januari', 'Februari', 'Mars', 'April', 'Maj', 'Juni', 'Juli', 'Augusti', 'September', 'Oktober', 'November', 'December']
"""
Choose a month by changing month variable
"""
month = 3 #mars
# Plot histogram
bars = plt.bar(föreningar, data[:,month-1], color = newcolors)
plt.bar(föreningar, data[:,month-2], color = colors)
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x()+0.15, yval + 5, int(yval))

# Labels and title
plt.ylabel('Medlemmar')
plt.ylim(0,1.1*max(data[:,month-1]))
plt.text(-0.5, 0.99*max(data[:,month-2]), f'Totalt {int(sum(data[:,month-1]))} medlemmar', fontsize='large')
plt.title(f'{months[month-1]}', fontsize='xx-large')
plt.show()