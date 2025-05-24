import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pyproj import Transformer
import geopandas as gpd
import matplotlib.animation as animation

# Get map of Sweden
world = gpd.read_file(r"C:\Users\Tove Tiedemann\Documents\Bachelor - UU\ne_10m_admin_0_countries.shp")
#pd.set_option('display.max_columns', None)  # Show all columns
#print(world.head())
sweden = world[world['NAME_SV'] == 'Sverige']

ebas = pd.read_csv(r"C:\Users\Tove Tiedemann\Documents\Bachelor - UU\ebas-april.csv", delimiter=";") #skriv lämplig filsökväg
ebas.head()
referens = pd.read_csv(r"C:\Users\Tove Tiedemann\Documents\Bachelor - UU\data-koordinater.csv", delimiter=";", encoding="ISO-8859-1", on_bad_lines="skip", encoding_errors="replace")
x = referens['x']
y = referens['y']
# Transform Sweref 99TM (EPSG:3006) to WGS84 (EPSG:4326)
transformer = Transformer.from_crs("EPSG:3006", "EPSG:4326", always_xy=True)
lon, lat = transformer.transform(x.values, y.values)

stad_counts = ebas['Stad/Ort'].value_counts()
referens = referens.rename(columns={'Kommunnamn': 'Stad/Ort'})  # Only if needed

# Merge ebas with referens to assign coordinates to each stad
ebas_with_coords = pd.merge(ebas, referens[['Stad/Ort', 'x', 'y']], on='Stad/Ort', how='left')

# Count occurrences for each Stad/Ort in the merged DataFrame
valid_coords = ebas_with_coords.dropna(subset=['x', 'y'])
counts = valid_coords['Stad/Ort'].map(stad_counts)

ebas['Inskriven'] = pd.to_datetime(ebas['Inskriven'])
ebas.sort_values(by='Inskriven')

target_föreningar = ['Kodsport Sverige', 'Lingolympiaden', 'Ung Vetenskapssports Astronomer', 'Ung Vetenskapssports Biologer', 'UVS Kemister', 'Ung Vetenskapssports Fysiker', 'Ung Vetenskapssports Ingenjörer', 'Ung Vetenskapssports Matematiker']
i = 0
target_month = 1  
"""
Choose a month by changing month variable
"""
month = 4 #april
data = np.zeros((8, month))

while target_month <=month:
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
"""

# Prepare data
ebas_with_coords['Inskriven'] = pd.to_datetime(ebas_with_coords['Inskriven'])
valid_coords = ebas_with_coords.dropna(subset=['x', 'y', 'Inskriven'])

month_range = range(1, 5)  # January to December

# Get unique Stad/Ort and their coordinates
unique_stads = valid_coords.drop_duplicates(subset=['Stad/Ort'])
stad_x = unique_stads['x'].values
stad_y = unique_stads['y'].values
stad_names = unique_stads['Stad/Ort'].values

# Transform all coordinates once
stad_lon, stad_lat = transformer.transform(stad_x, stad_y)

fig, ax = plt.subplots(figsize=(8, 8))
sweden.to_crs(epsg=4326).plot(ax=ax, color='white', edgecolor='black')

scat = ax.scatter(stad_lon, stad_lat, s=0, c='blue', alpha=0.5, edgecolors='none')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.set_title('Medlemmar i Sverige')
ax.grid(False)

def get_sizes(month):
    # Count cumulative members per Stad/Ort up to this month
    counts = []
    for stad in stad_names:
        count = valid_coords[(valid_coords['Stad/Ort'] == stad) & (valid_coords['Inskriven'].dt.month <= month)].shape[0]
        counts.append(count)
    # Use log scale for size, avoid log(0)
    sizes = 20*np.log10(counts)
    return sizes

def update(frame):
    sizes = get_sizes(frame+1)
    scat.set_sizes(sizes)
    ax.set_title(f'Medlemmar i Sverige: {months[frame]}')
    return scat,

ani = animation.FuncAnimation(fig, update, frames=len(month_range), interval=1500, blit=False, repeat=True)
plt.subplots_adjust(bottom=0.15)
ani.save("medlemmar_sverige.gif", writer="pillow")
import os
print(os.getcwd())
plt.show()