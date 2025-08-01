import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pyproj import Transformer
import geopandas as gpd
import matplotlib.animation as animation
from calendar import monthrange
import os

# Ask user for month
months = ['januari', 'februari', 'mars', 'april', 'maj', 'juni', 'juli', 'augusti', 'september', 'oktober', 'november', 'december']
month_input = input("Vilken månad vill du visa? (t.ex. juni): ").strip().lower()
if month_input not in months:
    raise ValueError("Ogiltig månad. Skriv t.ex. juni.")

month_idx = months.index(month_input) + 1
filename = f"ebas-{month_input}.csv"
filepath = os.path.join(r"C:\Users\Tove Tiedemann\Documents\Bachelor - UU", filename)

##################
# Stapeldiagram
##################
ebas = pd.read_csv(filepath, delimiter=";")
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

month=month_idx
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

# Read data
ebas = pd.read_csv(r"C:\Users\Tove Tiedemann\Documents\Bachelor - UU\ebas-juli.csv", delimiter=";")
ebas['Inskriven'] = pd.to_datetime(ebas['Inskriven'], errors='coerce')
referens = pd.read_csv(r"C:\Users\Tove Tiedemann\Documents\Bachelor - UU\data-koordinater.csv", delimiter=";", encoding="ISO-8859-1", on_bad_lines="skip", encoding_errors="replace")
referens = referens.rename(columns={'Kommunnamn': 'Stad/Ort'})
referens = referens.drop_duplicates(subset=['Stad/Ort'])  # Ensure unique cities

# Merge coordinates
ebas_with_coords = pd.merge(ebas, referens[['Stad/Ort', 'x', 'y']], on='Stad/Ort', how='left')
ebas_with_coords['Inskriven'] = pd.to_datetime(ebas_with_coords['Inskriven'], errors='coerce')
valid_coords = ebas_with_coords.dropna(subset=['x', 'y', 'Inskriven'])

# Organisation lists and colors
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
    "Lingolympiaden": "Lingolympiaden",
    "Ung Vetenskapssports Astronomer": "UVS Astronomer",
    "Ung Vetenskapssports Biologer": "UVS Biologer",
    "UVS Kemister": "UVS Kemister",
    "Ung Vetenskapssports Fysiker": "UVS Fysiker",
    "Ung Vetenskapssports Ingenjörer": "UVS Ingenjörer",
    "Ung Vetenskapssports Matematiker": "UVS Matematiker"
}

# Sweden map
world = gpd.read_file(r"C:\Users\Tove Tiedemann\Documents\Bachelor - UU\ne_10m_admin_0_countries.shp")
sweden = world[world['NAME_SV'] == 'Sverige']

# Static grid plot for latest month
latest_month = 7  # Juli
year = ebas_with_coords['Inskriven'].dt.year.min()
last_day = monthrange(year, latest_month)[1]
end_date = pd.Timestamp(year=year, month=latest_month, day=last_day)

n_orgs = len(forening_list)
ncols = 4
nrows = 2
fig_all_static, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(16, 4 * nrows))
fig_all_static.suptitle(f"{months[latest_month-1]}", fontsize=18, y=0.98)
axes = axes.flatten()

for idx, target_forening in enumerate(forening_list):
    ax_static = axes[idx]
    custom_color = forening_colors.get(target_forening, "blue")
    # Filter members up to last day in selected month
    org_cities = ebas_with_coords[
        (ebas_with_coords['Förening'] == target_forening) &
        (ebas_with_coords['Inskriven'] <= end_date)
    ]
    # Get city counts
    city_counts = org_cities['Stad/Ort'].value_counts()
    stad_names = city_counts.index.values
    # Get coordinates for these cities
    unique_stads = org_cities.drop_duplicates(subset=['Stad/Ort'])
    stad_x = []
    stad_y = []
    for stad in stad_names:
        coords = unique_stads[unique_stads['Stad/Ort'] == stad]
        if not coords.empty:
            stad_x.append(coords['x'].values[0])
            stad_y.append(coords['y'].values[0])
        else:
            stad_x.append(np.nan)
            stad_y.append(np.nan)
    sizes = 20 * np.log10(city_counts.values + 1)

    sweden.to_crs(epsg=3006).plot(ax=ax_static, color='white', edgecolor='black')
    ax_static.scatter(stad_x, stad_y, s=sizes, c=custom_color, alpha=0.75, edgecolors='none', label=forening_titles.get(target_forening, target_forening))
    ax_static.set_title(forening_titles.get(target_forening, target_forening), fontsize=14)
    ax_static.set_xticks([])
    ax_static.set_yticks([])
    ax_static.grid(False)

    # Infobox: top 3 cities and 3 new cities for latest month
    df_latest = valid_coords[
        (valid_coords['Förening'] == target_forening) &
        (valid_coords['Inskriven'].dt.month <= latest_month)
    ]
    top_cities = df_latest['Stad/Ort'].value_counts().head(3)
    top_text = "Topp 3 städer:\n" + "\n".join([f"- {city}: {count}" for city, count in top_cities.items()])

    new_df = valid_coords[
        (valid_coords['Förening'] == target_forening) &
        (valid_coords['Inskriven'].dt.month == latest_month)
    ]
    prev_df = valid_coords[
        (valid_coords['Förening'] == target_forening) &
        (valid_coords['Inskriven'].dt.month < latest_month)
    ]
    prev_cities = set(prev_df['Stad/Ort'].unique())
    truly_new_cities = [city for city in new_df['Stad/Ort'].unique() if city not in prev_cities]
    new_text = "Nya städer:\n" + "\n".join([f"- {city}" for city in truly_new_cities])

    infobox_text = f"{top_text}\n\n{new_text}"

    ax_static.text(1.06, 0.98, infobox_text, transform=ax_static.transAxes, fontsize=10,
               verticalalignment='top', horizontalalignment='left',
               bbox=dict(boxstyle="round", facecolor=custom_color, alpha=0.25))

# Hide unused axes if any
for ax in axes[n_orgs:]:
    ax.axis('off')

plt.tight_layout()
plt.savefig(r"C:\Users\Tove Tiedemann\Desktop\medlemmar_alla_static_test.png", bbox_inches='tight')
plt.show()

# Animated GIFs for each organisation
month_range = range(1, 8)  # January to July

for target_forening in forening_list:
    ebas_with_coords_f = ebas_with_coords[ebas_with_coords['Förening'] == target_forening].copy()
    ebas_with_coords_f['Inskriven'] = pd.to_datetime(ebas_with_coords_f['Inskriven'], errors='coerce')
    valid_coords = ebas_with_coords_f.dropna(subset=['x', 'y', 'Inskriven'])

    unique_stads = valid_coords.drop_duplicates(subset=['Stad/Ort'])
    stad_x = unique_stads['x'].values
    stad_y = unique_stads['y'].values
    stad_names = unique_stads['Stad/Ort'].values

    fig, ax = plt.subplots(figsize=(8, 8))
    sweden.to_crs(epsg=3006).plot(ax=ax, color='white', edgecolor='black')

    custom_color = forening_colors.get(target_forening, "blue")
    scat = ax.scatter(stad_x, stad_y, s=0, c=custom_color, alpha=0.75, edgecolors='none')
    ax.set_xticks([])
    ax.set_yticks([])
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

# Animated GIF for all organisations combined
ebas_with_coords_all = ebas_with_coords.copy()
ebas_with_coords_all['Inskriven'] = pd.to_datetime(ebas_with_coords_all['Inskriven'], errors='coerce')
valid_coords_all = ebas_with_coords_all.dropna(subset=['x', 'y', 'Inskriven'])

unique_stads_all = valid_coords_all.drop_duplicates(subset=['Stad/Ort'])
stad_x_all = unique_stads_all['x'].values
stad_y_all = unique_stads_all['y'].values
stad_names_all = unique_stads_all['Stad/Ort'].values

fig, ax = plt.subplots(figsize=(8, 8))
sweden.to_crs(epsg=3006).plot(ax=ax, color='white', edgecolor='black')

scat = ax.scatter(stad_x_all, stad_y_all, s=0, c='blue', alpha=0.5, edgecolors='none')
ax.set_xticks([])
ax.set_yticks([])
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
