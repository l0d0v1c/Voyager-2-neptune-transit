# Voyager 2 - Approche de Neptune (Août 1989)

Animation 3D interactive de la trajectoire de la sonde Voyager 2 lors de son survol historique de Neptune le 25 août 1989.

## Contenu

- `voyager2_neptune_3d.py` - Script principal de visualisation
- `vgr2_nep097.bsp` - Données SPICE de la trajectoire Voyager 2

## Prérequis

```bash
pip install spiceypy plotly numpy
```

## Utilisation

```bash
cd /chemin/vers/neptune
python voyager2_neptune_3d.py
```

Le script télécharge automatiquement les kernels SPICE nécessaires (~15 MB au total) depuis le serveur NASA NAIF.

## Visualisation

L'animation affiche :

- **Neptune** - Sphère bleue (rayon 24 764 km)
- **Voyager 2** - Diamant jaune suivant la trajectoire
- **Trajectoire** - Ligne blanche du 24 au 26 août 1989

### Satellites de Neptune

| Satellite | Couleur | Rayon (km) |
|-----------|---------|------------|
| Triton | Rouge | 1 353 |
| Proteus | Orange | 210 |
| Nereid | Jaune | 170 |
| Larissa | Cyan | 97 |
| Galatea | Violet | 88 |
| Despina | Bleu | 75 |
| Thalassa | Rose | 41 |
| Naiad | Bleu clair | 33 |

## Contrôles

- **Play/Pause** - Boutons en bas à gauche
- **Slider** - Navigation temporelle
- **Souris** - Rotation, zoom, déplacement de la vue 3D
- **Légende** - Cliquez pour masquer/afficher des éléments

## Fichier de sortie

Le script génère `voyager2_neptune.html` - fichier autonome ouvrable dans n'importe quel navigateur.

## Données SPICE

Les kernels utilisés proviennent de [NASA NAIF](https://naif.jpl.nasa.gov/):

- `naif0012.tls` - Secondes intercalaires
- `pck00010.tpc` - Constantes planétaires
- `de440s.bsp` - Éphémérides planétaires
- `nep097.bsp` - Éphémérides des satellites de Neptune

## Contexte historique

Voyager 2 est la seule sonde à avoir survolé Neptune. Le 25 août 1989, elle est passée à environ 4 800 km au-dessus des nuages de Neptune, découvrant 6 nouvelles lunes et le système d'anneaux de la planète.
