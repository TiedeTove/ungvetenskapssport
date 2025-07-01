import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pyproj import Transformer
import geopandas as gpd
import matplotlib.animation as animation

months = ['Januari', 'Februari', 'Mars', 'April', 'Maj', 'Juni', 'Juli', 'Augusti', 'September', 'Oktober', 'November', 'December']

##################
# Stapeldiagram
##################
ebas = pd.read_csv(r"C:\Users\Tove Tiedemann\Documents\Bachelor - UU\ebas-juni.csv", delimiter=";") #skriv lämplig filsökväg
ebas['Inskriven'] = pd.to_datetime(ebas['Inskriven'])
ebas.sort_values(by='Inskriven')

target_föreningar = ['Kodsport Sverige', 'Lingolympiaden', 'Ung Vetenskapssports Astronomer', 'Ung Vetenskapssports Biologer', 'UVS Kemister', 'Ung Vetenskapssports Fysiker', 'Ung Vetenskapssports Ingenjörer', 'Ung Vetenskapssports Matematiker']
i = 0
target_month = 1 
#Choose a month by changing month variable
month = 6 #juni
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

##################
# Kartanimation
##################

# Get map of Sweden
world = gpd.read_file(r"C:\Users\Tove Tiedemann\Documents\Bachelor - UU\ne_10m_admin_0_countries.shp")
sweden = world[world['NAME_SV'] == 'Sverige']

ebas = pd.read_csv(r"C:\Users\Tove Tiedemann\Desktop\ebas-juni.csv", delimiter=";") #skriv lämplig filsökväg
referens = pd.read_csv(r"C:\Users\Tove Tiedemann\Documents\Bachelor - UU\data-koordinater.csv", delimiter=";", encoding="ISO-8859-1", on_bad_lines="skip", encoding_errors="replace")
x = referens['x']
y = referens['y']

# Transform Sweref 99TM (EPSG:3006) to WGS84 (EPSG:4326)
transformer = Transformer.from_crs("EPSG:3006", "EPSG:4326", always_xy=True)
lon, lat = transformer.transform(x.values, y.values)

# Merge ebas with referens to assign coordinates to each stad
stad_counts = ebas['Stad/Ort'].value_counts()
referens = referens.rename(columns={'Kommunnamn': 'Stad/Ort'}) 
ebas_with_coords = pd.merge(ebas, referens[['Stad/Ort', 'x', 'y']], on='Stad/Ort', how='left')

# Count occurrences for each Stad/Ort in the merged DataFrame
valid_coords = ebas_with_coords.dropna(subset=['x', 'y'])
counts = valid_coords['Stad/Ort'].map(stad_counts)

plt.rcParams['font.family'] = 'DejaVu Sans'  # or another font with åäö support

forening_list = [
    "Kodsport Sverige",
    "Lingolympiaden",
    "Ung Vetenskapssports Astronomer",
    "Ung Vetenskapssports Biologer",
    "UVS Kemister",
    "Ung Vetenskapssports Fysiker",
    "Ung Vetenskapssports Ingenjörer",
    "Ung Vetenskapssports Matematiker"
]

forening_colors = {
    "Kodsport Sverige": "#0077CC",      # Stronger blue
    "Lingolympiaden": "#444444",        # Stronger dark gray
    "Ung Vetenskapssports Astronomer": "#FFC300",  # Stronger yellow
    "Ung Vetenskapssports Biologer": "#009944",    # Stronger green
    "UVS Kemister": "#D7263D",          # Stronger red
    "Ung Vetenskapssports Fysiker": "#111111",     # Stronger black
    "Ung Vetenskapssports Ingenjörer": "#005B99",  # Stronger blue for contrast
    "Ung Vetenskapssports Matematiker": "#FF9900"  # Stronger orange
}

forening_titles = {
    "Kodsport Sverige": "Kodsport",
    "Lingolympiaden": "Lingolympiaden",
    "Ung Vetenskapssports Astronomer": "UVS Astronomer",
    "Ung Vetenskapssports Biologer": "UVS Biologer",
    "UVS Kemister": "UVS Kemister",
    "Ung Vetenskapssports Fysiker": "UVS Fysiker",
    "Ung Vetenskapssports Ingenjörer": "UVS Ingenjörer",
    "Ung Vetenskapssports Matematiker": "UVS Matematiker"
}

month_range = range(1, 7)  # January to June

for target_forening in forening_list:
    ebas_with_coords_f = ebas_with_coords[ebas_with_coords['Förening'] == target_forening].copy()
    ebas_with_coords_f['Inskriven'] = pd.to_datetime(ebas_with_coords_f['Inskriven'])
    valid_coords = ebas_with_coords_f.dropna(subset=['x', 'y', 'Inskriven'])

    unique_stads = valid_coords.drop_duplicates(subset=['Stad/Ort'])
    stad_x = unique_stads['x'].values
    stad_y = unique_stads['y'].values
    stad_names = unique_stads['Stad/Ort'].values

    stad_lon, stad_lat = transformer.transform(stad_x, stad_y)

    fig, ax = plt.subplots(figsize=(8, 8))
    sweden.to_crs(epsg=3006).plot(ax=ax, color='white', edgecolor='black')

    custom_color = forening_colors.get(target_forening, "blue")
    scat = ax.scatter(stad_x, stad_y, s=0, c=custom_color, alpha=0.75, edgecolors='none')
    ax.axes.get_xaxis().set_ticks([])
    ax.axes.get_yaxis().set_ticks([])
    ax.grid(False)

    def get_sizes(month):
        counts = []
        for stad in stad_names:
            count = valid_coords[(valid_coords['Stad/Ort'] == stad) & (valid_coords['Inskriven'].dt.month <= month)].shape[0]
            counts.append(count)
        sizes = 20 * np.log10(np.array(counts) + 1)
        return sizes

    def update(frame):
        sizes = get_sizes(frame+1)
        scat.set_sizes(sizes)
        pretty_name = forening_titles.get(target_forening, target_forening)
        ax.set_title(f'Medlemmar i {pretty_name}: {months[frame]}')
        return scat,

    ani = animation.FuncAnimation(fig, update, frames=len(month_range), interval=1500, blit=False, repeat=True)
    plt.subplots_adjust(bottom=0.15)
    gif_name = f"medlemmar_{forening_titles.get(target_forening, target_forening).replace(' ', '_').lower()}.gif"
    ani.save(rf"C:\Users\Tove Tiedemann\Desktop\{gif_name}", writer="pillow")
    plt.close(fig)

# Create GIF for all data (not split by förening)
ebas_with_coords_all = ebas_with_coords.copy()
ebas_with_coords_all['Inskriven'] = pd.to_datetime(ebas_with_coords_all['Inskriven'])
valid_coords_all = ebas_with_coords_all.dropna(subset=['x', 'y', 'Inskriven'])

unique_stads_all = valid_coords_all.drop_duplicates(subset=['Stad/Ort'])
stad_x_all = unique_stads_all['x'].values
stad_y_all = unique_stads_all['y'].values
stad_names_all = unique_stads_all['Stad/Ort'].values

stad_lon_all, stad_lat_all = transformer.transform(stad_x_all, stad_y_all)

fig, ax = plt.subplots(figsize=(8, 8))
sweden.to_crs(epsg=3006).plot(ax=ax, color='white', edgecolor='black')

scat = ax.scatter(stad_x_all, stad_y_all, s=0, c='blue', alpha=0.5, edgecolors='none')
ax.axes.get_xaxis().set_ticks([])
ax.axes.get_yaxis().set_ticks([])
ax.grid(False)

def get_sizes_all(month):
    counts = []
    for stad in stad_names_all:
        count = valid_coords_all[(valid_coords_all['Stad/Ort'] == stad) & (valid_coords_all['Inskriven'].dt.month <= month)].shape[0]
        counts.append(count)
    sizes = 20 * np.log10(np.array(counts) + 1)
    return sizes

def update_all(frame):
    sizes = get_sizes_all(frame+1)
    scat.set_sizes(sizes)
    ax.set_title(f"Medlemmar i Sverige: {months[frame]}")
    return scat,

ani_all = animation.FuncAnimation(fig, update_all, frames=len(month_range), interval=1500, blit=False, repeat=True)
plt.subplots_adjust(bottom=0.15)
ani_all.save(r"C:\Users\Tove Tiedemann\Desktop\medlemmar_sverige_alla.gif", writer="pillow")
plt.close(fig)

"""
# Plot map for the last month (Maj) with constant marker size
fig2, ax2 = plt.subplots(figsize=(8, 8))
sweden.to_crs(epsg=4326).plot(ax=ax2, color='white', edgecolor='black')

# Use a constant size for all cities with members
constant_size = 30
ax2.scatter(stad_lon, stad_lat, s=constant_size, c='blue', alpha=0.5, edgecolors='none')
plt.subplots_adjust(bottom=0.15)
ax2.set_xlabel('Longitud')
ax2.set_ylabel('Latitud')
ax2.set_title(f'Medlemmar i Sverige: {months[4]}')
ax2.grid(False)
plt.show()
"""