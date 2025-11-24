#!/usr/bin/env python3
"""
Animation 3D de l'approche de Voyager 2 vers Neptune
"""

import numpy as np
import spiceypy as spice
import plotly.graph_objects as go
import urllib.request
import os

# === Téléchargement des kernels SPICE nécessaires ===
KERNELS = {
    'naif0012.tls': 'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/lsk/naif0012.tls',
    'pck00010.tpc': 'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/pck00010.tpc',
    'de440s.bsp': 'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de440s.bsp',
    'nep097.bsp': 'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/satellites/nep097.bsp',
}

def download_kernels():
    """Télécharge les kernels manquants"""
    for filename, url in KERNELS.items():
        if not os.path.exists(filename):
            print(f"Téléchargement de {filename}...")
            urllib.request.urlretrieve(url, filename)
            print(f"  ✓ {filename} téléchargé")
        else:
            print(f"  ✓ {filename} déjà présent")

# Changer vers le répertoire du script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=== Préparation des données SPICE ===")
download_kernels()

# Charger tous les kernels
print("\nChargement des kernels...")
spice.furnsh('naif0012.tls')
spice.furnsh('pck00010.tpc')
spice.furnsh('de440s.bsp')
spice.furnsh('nep097.bsp')
spice.furnsh('vgr2_nep097.bsp')
print("  ✓ Kernels chargés")

# Satellites de Neptune (NAIF IDs)
SATELLITES = {
    'Triton': 801,
    'Nereid': 802,
    'Naiad': 803,
    'Thalassa': 804,
    'Despina': 805,
    'Galatea': 806,
    'Larissa': 807,
    'Proteus': 808,
}

# Rayons des satellites (km)
SATELLITE_RADII = {
    'Triton': 1353,
    'Nereid': 170,
    'Naiad': 33,
    'Thalassa': 41,
    'Despina': 75,
    'Galatea': 88,
    'Larissa': 97,
    'Proteus': 210,
}

# === Calcul de la trajectoire ===
print("\nCalcul de la trajectoire...")

# Période d'approche (24-26 août 1989 - survol le 25 août)
et_start = spice.str2et('1989-08-24 00:00:00')
et_end = spice.str2et('1989-08-26 12:00:00')
n_points = 600
times = np.linspace(et_start, et_end, n_points)

# Positions de Voyager 2 par rapport à Neptune
positions = []
dates = []
distances = []

for t in times:
    pos, _ = spice.spkpos('VOYAGER 2', t, 'J2000', 'NONE', 'NEPTUNE BARYCENTER')
    positions.append(pos)
    distances.append(np.linalg.norm(pos))
    dates.append(spice.et2utc(t, 'C', 0))

positions = np.array(positions)
distances = np.array(distances)

print(f"  ✓ {n_points} points calculés")
print(f"  Distance min: {distances.min():.0f} km")
print(f"  Distance max: {distances.max():.0f} km")

# Calcul des positions des satellites
print("\nCalcul des orbites des satellites...")
satellite_positions = {}
satellite_colors = {
    'Triton': '#ff6b6b',
    'Nereid': '#feca57',
    'Naiad': '#48dbfb',
    'Thalassa': '#ff9ff3',
    'Despina': '#54a0ff',
    'Galatea': '#5f27cd',
    'Larissa': '#00d2d3',
    'Proteus': '#ff9f43',
}

for name, naif_id in SATELLITES.items():
    try:
        sat_pos = []
        for t in times:
            pos, _ = spice.spkpos(str(naif_id), t, 'J2000', 'NONE', 'NEPTUNE BARYCENTER')
            sat_pos.append(pos)
        satellite_positions[name] = np.array(sat_pos)
        print(f"  ✓ {name}")
    except Exception as e:
        print(f"  ✗ {name}: données non disponibles")

# === Création de la visualisation 3D ===
print("\nCréation de l'animation 3D...")

# Rayon de Neptune
R_NEPTUNE = 24764  # km

# Créer la sphère de Neptune
theta = np.linspace(0, 2*np.pi, 50)
phi = np.linspace(0, np.pi, 30)
x_sphere = R_NEPTUNE * np.outer(np.cos(theta), np.sin(phi))
y_sphere = R_NEPTUNE * np.outer(np.sin(theta), np.sin(phi))
z_sphere = R_NEPTUNE * np.outer(np.ones(50), np.cos(phi))

# Figure
fig = go.Figure()

# Neptune
fig.add_trace(go.Surface(
    x=x_sphere, y=y_sphere, z=z_sphere,
    colorscale=[[0, '#1a237e'], [0.5, '#3949ab'], [1, '#7986cb']],
    showscale=False,
    name='Neptune',
    opacity=0.9
))

# Trajectoire complète
fig.add_trace(go.Scatter3d(
    x=positions[:, 0],
    y=positions[:, 1],
    z=positions[:, 2],
    mode='lines',
    line=dict(color='white', width=3),
    name='Trajectoire Voyager 2'
))

# Point de départ
fig.add_trace(go.Scatter3d(
    x=[positions[0, 0]],
    y=[positions[0, 1]],
    z=[positions[0, 2]],
    mode='markers',
    marker=dict(size=6, color='green'),
    name='Début'
))

# Point d'arrivée
fig.add_trace(go.Scatter3d(
    x=[positions[-1, 0]],
    y=[positions[-1, 1]],
    z=[positions[-1, 2]],
    mode='markers',
    marker=dict(size=6, color='red'),
    name='Fin'
))

# Position animée de Voyager 2
fig.add_trace(go.Scatter3d(
    x=[positions[0, 0]],
    y=[positions[0, 1]],
    z=[positions[0, 2]],
    mode='markers',
    marker=dict(size=8, color='yellow', symbol='diamond'),
    name='Voyager 2'
))

# Ajouter les orbites et positions des satellites
for name, sat_pos in satellite_positions.items():
    color = satellite_colors.get(name, 'white')
    # Orbite du satellite
    fig.add_trace(go.Scatter3d(
        x=sat_pos[:, 0],
        y=sat_pos[:, 1],
        z=sat_pos[:, 2],
        mode='lines',
        line=dict(color=color, width=1),
        name=f'{name} (orbite)',
        opacity=0.5
    ))
    # Position actuelle du satellite
    fig.add_trace(go.Scatter3d(
        x=[sat_pos[0, 0]],
        y=[sat_pos[0, 1]],
        z=[sat_pos[0, 2]],
        mode='markers',
        marker=dict(size=5, color=color),
        name=name
    ))

# Créer les frames d'animation
frames = []
for k in range(0, n_points, 3):  # Sauter des frames pour fluidité
    frame_data = [
        go.Surface(x=x_sphere, y=y_sphere, z=z_sphere,
                  colorscale=[[0, '#1a237e'], [0.5, '#3949ab'], [1, '#7986cb']],
                  showscale=False, opacity=0.9),
        go.Scatter3d(x=positions[:, 0], y=positions[:, 1], z=positions[:, 2],
                    mode='lines', line=dict(color='white', width=3)),
        go.Scatter3d(x=[positions[0, 0]], y=[positions[0, 1]], z=[positions[0, 2]],
                    mode='markers', marker=dict(size=6, color='green')),
        go.Scatter3d(x=[positions[-1, 0]], y=[positions[-1, 1]], z=[positions[-1, 2]],
                    mode='markers', marker=dict(size=6, color='red')),
        go.Scatter3d(x=[positions[k, 0]], y=[positions[k, 1]], z=[positions[k, 2]],
                    mode='markers', marker=dict(size=8, color='yellow', symbol='diamond')),
    ]

    # Ajouter les satellites à chaque frame
    for name, sat_pos in satellite_positions.items():
        color = satellite_colors.get(name, 'white')
        # Orbite
        frame_data.append(go.Scatter3d(
            x=sat_pos[:, 0], y=sat_pos[:, 1], z=sat_pos[:, 2],
            mode='lines', line=dict(color=color, width=1), opacity=0.5
        ))
        # Position actuelle
        frame_data.append(go.Scatter3d(
            x=[sat_pos[k, 0]], y=[sat_pos[k, 1]], z=[sat_pos[k, 2]],
            mode='markers', marker=dict(size=5, color=color)
        ))

    frame = go.Frame(
        data=frame_data,
        name=str(k),
        layout=go.Layout(
            title=f"Voyager 2 - {dates[k]}<br>Distance: {distances[k]:.0f} km"
        )
    )
    frames.append(frame)

fig.frames = frames

# Configuration du layout
fig.update_layout(
    title=f"Approche de Voyager 2 vers Neptune<br>{dates[0]}",
    scene=dict(
        xaxis=dict(title='X (km)', backgroundcolor='black', gridcolor='gray'),
        yaxis=dict(title='Y (km)', backgroundcolor='black', gridcolor='gray'),
        zaxis=dict(title='Z (km)', backgroundcolor='black', gridcolor='gray'),
        aspectmode='data',
        bgcolor='black',
    ),
    paper_bgcolor='black',
    font=dict(color='white'),
    showlegend=True,
    legend=dict(x=0.02, y=0.98),
    updatemenus=[
        dict(
            type='buttons',
            showactive=False,
            y=0.1,
            x=0.1,
            xanchor='left',
            buttons=[
                dict(
                    label='▶ Play',
                    method='animate',
                    args=[None, dict(
                        frame=dict(duration=50, redraw=True),
                        fromcurrent=True,
                        mode='immediate'
                    )]
                ),
                dict(
                    label='⏸ Pause',
                    method='animate',
                    args=[[None], dict(
                        frame=dict(duration=0, redraw=False),
                        mode='immediate'
                    )]
                )
            ]
        )
    ],
    sliders=[dict(
        active=0,
        yanchor='top',
        xanchor='left',
        currentvalue=dict(
            font=dict(size=12),
            prefix='Frame: ',
            visible=True,
            xanchor='right'
        ),
        pad=dict(b=10, t=50),
        len=0.9,
        x=0.1,
        y=0,
        steps=[dict(
            args=[[str(k)], dict(
                frame=dict(duration=50, redraw=True),
                mode='immediate'
            )],
            label=str(k//3),
            method='animate'
        ) for k in range(0, n_points, 3)]
    )]
)

# Sauvegarder et afficher
output_file = 'voyager2_neptune.html'
fig.write_html(output_file)
print(f"\n✓ Animation sauvegardée: {output_file}")
print("  Ouvrez ce fichier dans votre navigateur")

# Afficher directement
fig.show()

# Nettoyer SPICE
spice.kclear()
