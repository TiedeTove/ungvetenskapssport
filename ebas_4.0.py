### Namge dina filer ebas-month.csv

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pyproj import Transformer
import geopandas as gpd
import matplotlib.animation as animation
import os

# Ask user for month
months = ['januari', 'februari', 'mars', 'april', 'maj', 'juni', 'juli', 'augusti', 'september', 'oktober', 'november', 'december']
month_input = input("Vilken månad vill du visa? (t.ex. juni): ").strip().lower()
if month_input not in months:
    raise ValueError("Ogiltig månad. Skriv t.ex. juni.")

month_idx = months.index(month_input) + 1
filename = f"ebas-{month_input}.csv"
filepath = os.path.join(r"C:\Users\Tove Tiedemann\Documents\Bachelor - UU", filename)

# Load data for selected month
ebas = pd.read_csv(filepath, delimiter=";")
ebas['Inskriven'] = pd.to_datetime(ebas['Inskriven'])
referens = pd.read_csv(r"C:\Users\Tove Tiedemann\Documents\Bachelor - UU\data-koordinater.csv", delimiter=";", encoding="ISO-8859-1", on_bad_lines="skip", encoding_errors="replace")
referens = referens.rename(columns={'Kommunnamn': 'Stad/Ort'})
ebas_with_coords = pd.merge(ebas, referens[['Stad/Ort', 'x', 'y']], on='Stad/Ort', how='left')
ebas_with_coords['Month'] = ebas_with_coords['Inskriven'].dt.month

# Now use month_idx for all plots
month = month_idx

# Sweden map
world = gpd.read_file(r"C:\Users\Tove Tiedemann\Documents\Bachelor - UU\ne_10m_admin_0_countries.shp")
sweden = world[world['NAME_SV'] == 'Sverige']

# Organisation info
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
    "Kodsport Sverige": "#0077CC",
    "Lingolympiaden": "#444444",
    "Ung Vetenskapssports Astronomer": "#FFC300",
    "Ung Vetenskapssports Biologer": "#009944",
    "UVS Kemister": "#D7263D",
    "Ung Vetenskapssports Fysiker": "#111111",
    "Ung Vetenskapssports Ingenjörer": "#005B99",
    "Ung Vetenskapssports Matematiker": "#FF9900"
}
forening_titles = {
    "Kodsport Sverige": "Kodsport",
    "Lingolympiaden": "Lingo",
    "Ung Vetenskapssports Astronomer": "Astronomi",
    "Ung Vetenskapssports Biologer": "Biologi",
    "UVS Kemister": "Kemi",
    "Ung Vetenskapssports Fysiker": "Fysik",
    "Ung Vetenskapssports Ingenjörer": "Ingenjörer",
    "Ung Vetenskapssports Matematiker": "Matematik"
}
month_range = range(1, month+1)

##################
# Stapeldiagram
##################
ebas = pd.read_csv(r"C:\Users\Tove Tiedemann\Documents\Bachelor - UU\ebas-juni.csv", delimiter=";")
ebas['Inskriven'] = pd.to_datetime(ebas['Inskriven'])
ebas.sort_values(by='Inskriven')

target_föreningar = [
    'Kodsport Sverige', 'Lingolympiaden', 'Ung Vetenskapssports Astronomer',
    'Ung Vetenskapssports Biologer', 'UVS Kemister', 'Ung Vetenskapssports Fysiker',
    'Ung Vetenskapssports Ingenjörer', 'Ung Vetenskapssports Matematiker'
]
föreningar = ['KS', 'Lingo', 'Astro', 'Biologi', 'Kemi', 'Fysik', 'Ingenjör', 'Matte']
colors = ['#7fd3ff', 'lightgray', '#fff4bc', '#81c1a0', '#ec7485', 'dimgrey', '#64a7cb', '#ffd084']
newcolors = ['#00A6FD', 'dimgray', '#FFD500', '#01A852', '#ED344F', 'black', '#0082C8', '#FEB132']

data = np.zeros((8, month))

for target_month in range(1, month+1):
    for i, target_förening in enumerate(target_föreningar):
        count = ((ebas['Förening'] == target_förening) & (ebas['Inskriven'].dt.month == target_month)).sum()
        if target_month == 1:
            data[i][target_month-1] = count
        else:
            data[i][target_month-1] = data[i][target_month-2] + count

bars = plt.bar(föreningar, data[:,month-1], color=newcolors)
plt.bar(föreningar, data[:,month-2], color=colors)
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x()+0.15, yval + 5, int(yval))

plt.ylabel('Medlemmar')
plt.ylim(0, 1.1 * max(data[:,month-1]))
plt.text(-0.5, 0.99 * max(data[:,month-2]), f'Totalt {int(sum(data[:,month-1]))} medlemmar', fontsize='large')
plt.title(f'{months[month-1].capitalize()}', fontsize='xx-large')
plt.tight_layout()
plt.show()

# Precompute member counts per city, month, and organisation
valid_coords = ebas_with_coords.dropna(subset=['x', 'y', 'Inskriven'])
grouped = (
    valid_coords
    .groupby(['Förening', 'Stad/Ort', 'Month'])
    .size()
    .unstack(fill_value=0)
)
cumsum_grouped = grouped.cumsum(axis=1)

# Static grid for latest month
n_orgs = len(forening_list)
ncols = 4
nrows = 2
fig_all_static, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(16, 4 * nrows))
latest_month = max(month_range)
fig_all_static.suptitle(f"{months[latest_month-1].capitalize()}", fontsize=18, y=0.98)
axes = axes.flatten()

for idx, target_forening in enumerate(forening_list):
    ax_static = axes[idx]
    custom_color = forening_colors.get(target_forening, "blue")
    # Get cities for this organisation
    org_cities = cumsum_grouped.loc[target_forening]
    stad_names = org_cities.index.values
    # Get coordinates for these cities
    unique_stads = valid_coords[(valid_coords['Förening'] == target_forening)].drop_duplicates(subset=['Stad/Ort'])
    stad_x = unique_stads['x'].values
    stad_y = unique_stads['y'].values

    # Marker sizes from precomputed cumulative counts
    sizes = 20 * np.log10(org_cities[latest_month].values + 1)

    # Infobox: top 3 cities and 3 new cities for latest month
    df_latest = valid_coords[(valid_coords['Förening'] == target_forening) & (valid_coords['Inskriven'].dt.month <= latest_month)]
    top_cities = df_latest['Stad/Ort'].value_counts().head(3)
    top_text = "Topp 3 städer:\n" + "\n".join([f"- {city}: {count}" for city, count in top_cities.items()])    
    new_df = valid_coords[(valid_coords['Förening'] == target_forening) & (valid_coords['Inskriven'].dt.month == latest_month)]
    prev_df = valid_coords[(valid_coords['Förening'] == target_forening) & (valid_coords['Inskriven'].dt.month < latest_month)]
    prev_cities = set(prev_df['Stad/Ort'].unique())
    truly_new_cities = [city for city in new_df['Stad/Ort'].unique() if city not in prev_cities]
    new_text = "Nya städer:\n" + "\n".join([f"- {city}" for city in truly_new_cities])
    infobox_text = f"{top_text}\n\n{new_text}"

    sweden.to_crs(epsg=3006).plot(ax=ax_static, color='white', edgecolor='black')
    ax_static.scatter(stad_x, stad_y, s=sizes, c=custom_color, alpha=0.75, edgecolors='none', label=forening_titles.get(target_forening, target_forening))
    ax_static.axes.get_xaxis().set_ticks([])
    ax_static.axes.get_yaxis().set_ticks([])
    ax_static.grid(False)
    # Place legend above the infobox
    ax_static.legend(loc='upper left', fontsize=10, bbox_to_anchor=(0.98, 1.02))
    ax_static.text(1.06, 0.88, infobox_text, transform=ax_static.transAxes, fontsize=10,
                verticalalignment='top', horizontalalignment='left',
                bbox=dict(boxstyle="round", facecolor=custom_color, alpha=0.25))

# Hide unused axes if any
for ax in axes[n_orgs:]:
    ax.axis('off')

plt.tight_layout()
plt.savefig(r"C:\Users\Tove Tiedemann\Desktop\medlemmar_alla_static.png", bbox_inches='tight')
plt.show()

# Animation for all data (not split by förening)
unique_stads_all = valid_coords.drop_duplicates(subset=['Stad/Ort'])
stad_x_all = unique_stads_all['x'].values
stad_y_all = unique_stads_all['y'].values
stad_names_all = unique_stads_all['Stad/Ort'].values

# Precompute cumulative counts for all cities
grouped_all = (
    valid_coords
    .groupby(['Stad/Ort', 'Month'])
    .size()
    .unstack(fill_value=0)
)
cumsum_grouped_all = grouped_all.cumsum(axis=1)

fig, ax = plt.subplots(figsize=(8, 8))
sweden.to_crs(epsg=3006).plot(ax=ax, color='white', edgecolor='black')
scat = ax.scatter(stad_x_all, stad_y_all, s=0, c='blue', alpha=0.5, edgecolors='none')
ax.axes.get_xaxis().set_ticks([])
ax.axes.get_yaxis().set_ticks([])
ax.grid(False)

def get_sizes_all(month):
    sizes = 20 * np.log10(cumsum_grouped_all[month].reindex(stad_names_all, fill_value=0).values + 1)
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