#!/usr/bin/env python3
"""
Vue vers l'avant depuis Voyager 2 pendant le survol de Neptune
"""

import numpy as np
import spiceypy as spice
import plotly.graph_objects as go
import os

# Changer vers le répertoire du script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=== Vue depuis Voyager 2 ===")

# Charger les kernels
print("\nChargement des kernels...")
spice.furnsh('naif0012.tls')
spice.furnsh('pck00010.tpc')
spice.furnsh('de440s.bsp')
spice.furnsh('nep097.bsp')
spice.furnsh('vgr2_nep097.bsp')
print("  ✓ Kernels chargés")

# Satellites de Neptune
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

SATELLITE_COLORS = {
    'Triton': '#ff6b6b',
    'Nereid': '#feca57',
    'Naiad': '#48dbfb',
    'Thalassa': '#ff9ff3',
    'Despina': '#54a0ff',
    'Galatea': '#5f27cd',
    'Larissa': '#00d2d3',
    'Proteus': '#ff9f43',
}

# Rayon de Neptune
R_NEPTUNE = 24764  # km

# === Calcul des positions ===
print("\nCalcul des positions...")

# Période d'approche
et_start = spice.str2et('1989-08-24 12:00:00')
et_end = spice.str2et('1989-08-26 00:00:00')
n_frames = 200
times = np.linspace(et_start, et_end, n_frames)

# Stocker les données pour chaque frame
frames_data = []

for i, t in enumerate(times):
    # Position de Voyager 2
    v2_pos, _ = spice.spkpos('VOYAGER 2', t, 'J2000', 'NONE', 'NEPTUNE BARYCENTER')

    # Direction avant = vers Neptune (centre de la vue)
    forward = -v2_pos / np.linalg.norm(v2_pos)

    # Construire un repère local (forward, right, up)
    # Up approximatif (axe Z du J2000)
    up_ref = np.array([0, 0, 1])
    right = np.cross(forward, up_ref)
    right = right / np.linalg.norm(right)
    up = np.cross(right, forward)

    # Matrice de rotation (monde -> caméra)
    rot_matrix = np.array([right, up, forward])

    # Position de Neptune dans le repère caméra
    neptune_rel = -v2_pos  # Neptune vu depuis V2
    neptune_cam = rot_matrix @ neptune_rel

    # Positions des satellites
    sat_positions_cam = {}
    for name, naif_id in SATELLITES.items():
        try:
            sat_pos, _ = spice.spkpos(str(naif_id), t, 'J2000', 'NONE', 'NEPTUNE BARYCENTER')
            sat_rel = sat_pos - v2_pos
            sat_cam = rot_matrix @ sat_rel
            sat_positions_cam[name] = sat_cam
        except:
            pass

    date_str = spice.et2utc(t, 'C', 0)
    distance = np.linalg.norm(v2_pos)

    frames_data.append({
        'neptune': neptune_cam,
        'satellites': sat_positions_cam,
        'date': date_str,
        'distance': distance,
        'rot_matrix': rot_matrix
    })

print(f"  ✓ {n_frames} frames calculées")

# === Création de la visualisation ===
print("\nCréation de la visualisation...")

fig = go.Figure()

# Fonction pour créer une sphère dans le repère caméra
def create_sphere_cam(center, radius, color_scale, n_points=30):
    theta = np.linspace(0, 2*np.pi, n_points)
    phi = np.linspace(0, np.pi, n_points//2)
    x = center[0] + radius * np.outer(np.cos(theta), np.sin(phi))
    y = center[1] + radius * np.outer(np.sin(theta), np.sin(phi))
    z = center[2] + radius * np.outer(np.ones(n_points), np.cos(phi))
    return x, y, z

# Frame initiale
frame0 = frames_data[0]

# Neptune
x, y, z = create_sphere_cam(frame0['neptune'], R_NEPTUNE, None)
fig.add_trace(go.Surface(
    x=x, y=y, z=z,
    colorscale=[[0, '#1a237e'], [0.5, '#3949ab'], [1, '#7986cb']],
    showscale=False,
    name='Neptune',
    opacity=0.95
))

# Satellites
for name, pos in frame0['satellites'].items():
    color = SATELLITE_COLORS.get(name, 'white')
    fig.add_trace(go.Scatter3d(
        x=[pos[0]], y=[pos[1]], z=[pos[2]],
        mode='markers+text',
        marker=dict(size=6, color=color),
        text=[name],
        textposition='top center',
        textfont=dict(size=10, color=color),
        name=name
    ))

# Point de visée (crosshair au centre)
fig.add_trace(go.Scatter3d(
    x=[0], y=[0], z=[100000],
    mode='markers',
    marker=dict(size=3, color='yellow', symbol='cross'),
    name='Direction avant',
    showlegend=False
))

# Créer les frames d'animation
frames = []
for k, fd in enumerate(frames_data):
    frame_traces = []

    # Neptune
    x, y, z = create_sphere_cam(fd['neptune'], R_NEPTUNE, None)
    frame_traces.append(go.Surface(
        x=x, y=y, z=z,
        colorscale=[[0, '#1a237e'], [0.5, '#3949ab'], [1, '#7986cb']],
        showscale=False, opacity=0.95
    ))

    # Satellites
    for name in frame0['satellites'].keys():
        if name in fd['satellites']:
            pos = fd['satellites'][name]
            color = SATELLITE_COLORS.get(name, 'white')
            frame_traces.append(go.Scatter3d(
                x=[pos[0]], y=[pos[1]], z=[pos[2]],
                mode='markers+text',
                marker=dict(size=6, color=color),
                text=[name],
                textposition='top center',
                textfont=dict(size=10, color=color)
            ))
        else:
            frame_traces.append(go.Scatter3d(x=[], y=[], z=[]))

    # Crosshair
    frame_traces.append(go.Scatter3d(
        x=[0], y=[0], z=[100000],
        mode='markers',
        marker=dict(size=3, color='yellow', symbol='cross')
    ))

    frames.append(go.Frame(
        data=frame_traces,
        name=str(k),
        layout=go.Layout(
            title=f"Vue depuis Voyager 2 - {fd['date']}<br>Distance à Neptune: {fd['distance']:.0f} km"
        )
    ))

fig.frames = frames

# Configuration du layout - vue perspective depuis la caméra
fig.update_layout(
    title=f"Vue depuis Voyager 2 - {frame0['date']}<br>Distance à Neptune: {frame0['distance']:.0f} km",
    scene=dict(
        xaxis=dict(title='Droite (km)', backgroundcolor='black', gridcolor='gray', showgrid=False),
        yaxis=dict(title='Haut (km)', backgroundcolor='black', gridcolor='gray', showgrid=False),
        zaxis=dict(title='Avant (km)', backgroundcolor='black', gridcolor='gray', showgrid=False),
        aspectmode='data',
        bgcolor='black',
        camera=dict(
            eye=dict(x=0, y=0, z=-0.15),  # Vue grand angle (plus proche)
            up=dict(x=0, y=1, z=0),
            center=dict(x=0, y=0, z=0),
            projection=dict(type='perspective')
        )
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
                        frame=dict(duration=100, redraw=True),
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
                frame=dict(duration=100, redraw=True),
                mode='immediate'
            )],
            label=str(k),
            method='animate'
        ) for k in range(n_frames)]
    )]
)

# Sauvegarder
output_file = 'voyager2_forward_view.html'
fig.write_html(output_file)
print(f"\n✓ Visualisation sauvegardée: {output_file}")
print("  Ouvrez ce fichier dans votre navigateur")

# Afficher
fig.show()

# Nettoyer
spice.kclear()
