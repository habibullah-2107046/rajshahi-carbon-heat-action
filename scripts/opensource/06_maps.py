"""
06_maps.py  -  Step 6b (docs/06_statistics_and_maps.md)

Six-panel publication maps (one panel per year) with a north arrow and
scale bar in every panel, coordinates on all four sides and a legend or
colour bar. Reads the grid created by 03_grid.py and 04_hotspot.py.

Run:  python 06_maps.py
Out:  05_figures/Map1_Carbon_Heat_Zones.png ... Map5_Normalized_LST.png
"""
import numpy as np
import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Rectangle, Polygon
from matplotlib.ticker import MultipleLocator, FuncFormatter
from matplotlib.colors import TwoSlopeNorm, Normalize

import config as C

C.ensure_dirs()
g = gpd.read_file(C.OUT_DIR / "grid" / f"RCC_grid_{C.CELL}m.shp").to_crs(4326)
outline = g.dissolve()
yrs = [y for y in C.YEARS if f"LSCE_{y}" in g.columns]
OUT = str(C.FIG_DIR) + "/"
CITY = C.CITY_NAME
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8})

xmin, ymin, xmax, ymax = g.total_bounds
px, py = 0.012, 0.010
X0, X1, Y0, Y1 = xmin - px, xmax + px, ymin - py, ymax + py
LAT0 = (ymin + ymax) / 2
KM_LON = 1.0 / (111.32 * np.cos(np.radians(LAT0)))   # degrees per km (longitude)

def dms(v, hemi):
    d = int(np.floor(v)); m = int(round((v - d) * 60))
    if m == 60: d += 1; m = 0
    return u"%d\u00b0%02d'%s" % (d, m, hemi)

def decorate(ax, year):
    outline.boundary.plot(ax=ax, color='black', lw=0.9)
    ax.set_xlim(X0, X1); ax.set_ylim(Y0, Y1)
    ax.set_aspect(1 / np.cos(np.radians(LAT0)))
    ax.set_xlabel(''); ax.set_ylabel('')
    # coordinates on all four sides
    ax.xaxis.set_major_locator(MultipleLocator(2 / 60.0))
    ax.yaxis.set_major_locator(MultipleLocator(2 / 60.0))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, p: dms(v, 'E')))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: dms(v, 'N')))
    ax.tick_params(axis='both', which='both', direction='in', length=3, width=0.6,
                   top=True, bottom=True, left=True, right=True,
                   labeltop=True, labelbottom=True, labelleft=True, labelright=True,
                   labelsize=6.5, pad=2)
    ax.tick_params(axis='y', labelrotation=90)
    for t in ax.yaxis.get_major_ticks():
        t.label1.set_verticalalignment('center'); t.label2.set_verticalalignment('center')
    for s in ax.spines.values(): s.set_linewidth(1.0)
    ax.grid(False)
    # year label inside frame
    ax.text(0.02, 0.96, str(year), transform=ax.transAxes, fontsize=10, fontweight='bold',
            va='top', ha='left')
    # north arrow (ArcMap style, half black / half white)
    cx, cy, h, w = 0.93, 0.74, 0.16, 0.045
    ax.add_patch(Polygon([[cx, cy + h], [cx - w, cy], [cx, cy + h * 0.28]], closed=True,
                         transform=ax.transAxes, fc='black', ec='black', lw=0.6))
    ax.add_patch(Polygon([[cx, cy + h], [cx + w, cy], [cx, cy + h * 0.28]], closed=True,
                         transform=ax.transAxes, fc='white', ec='black', lw=0.6))
    ax.text(cx, cy + h + 0.025, 'N', transform=ax.transAxes, ha='center', va='bottom',
            fontsize=9, fontweight='bold')
    # scale bar 0 - 0.5 - 1 - 2 km
    sx = X0 + (X1 - X0) * 0.05; sy = Y0 + (Y1 - Y0) * 0.07; hgt = (Y1 - Y0) * 0.022
    segs = [(0, 0.5, 'black'), (0.5, 1, 'white'), (1, 2, 'black')]
    for a, b, c in segs:
        ax.add_patch(Rectangle((sx + a * KM_LON, sy), (b - a) * KM_LON, hgt, fc=c, ec='black', lw=0.5))
    for v in (0, 0.5, 1, 2):
        ax.text(sx + v * KM_LON, sy + hgt * 1.8, ('%g' % v), ha='center', va='bottom', fontsize=6)
    ax.text(sx + 2 * KM_LON + 0.1 * KM_LON, sy + hgt / 2, 'Kilometers', ha='left', va='center', fontsize=6)

def make_fig(plotfn, title, fname, handles=None, cmap=None, norm=None, cblabel=None):
    fig, axs = plt.subplots(2, 3, figsize=(13, 6.8))
    fig.subplots_adjust(left=0.035, right=0.975, top=0.91, bottom=0.13, wspace=0.16, hspace=0.20)
    for ax, y in zip(axs.flat, yrs):
        plotfn(ax, y)
        decorate(ax, y)
    if C.SHOW_TITLE:
        fig.suptitle(title, fontsize=12, fontweight='bold', y=0.975)
    if handles:
        leg = fig.legend(handles=handles, loc='lower center', ncol=len(handles), frameon=True,
                         fontsize=8.5, title='Legend', title_fontproperties={'weight': 'bold', 'size': 9},
                         edgecolor='black', fancybox=False, bbox_to_anchor=(0.5, 0.01))
        leg.get_frame().set_linewidth(0.8)
    else:
        cax = fig.add_axes([0.30, 0.035, 0.40, 0.02])
        cb = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=cax, orientation='horizontal')
        cb.set_label(cblabel, fontsize=9, fontweight='bold'); cb.ax.xaxis.set_label_position('top'); cb.ax.tick_params(labelsize=8)
    fig.savefig(OUT + fname, dpi=300); plt.close(fig)

# 1. Zones
zcol = {1: '#a50026', 2: '#8c6bb1', 3: '#fdae61', 4: '#1a9850', 0: '#f2f2f2'}
zlab = {1: 'Dual stress (carbon + heat hotspot)', 2: 'Carbon hotspot only', 3: 'Heat hotspot only',
        4: 'Cool sink (carbon + heat coldspot)', 0: 'Not significant'}
make_fig(lambda ax, y: g.plot(ax=ax, color=g[f'ZONE_{y}'].map(zcol), edgecolor='white', linewidth=0.1),
         'Carbon–Heat Stress Zones in ' + CITY + ', 2000–2025',
         'Map1_Carbon_Heat_Zones.png',
         handles=[Patch(fc=zcol[k], ec='grey', lw=0.4, label=zlab[k]) for k in (1, 2, 3, 4, 0)])

# 2-3. Hotspots
bcol = {3: '#b2182b', 2: '#ef8a62', 1: '#fddbc7', 0: '#f7f7f7', -1: '#d1e5f0', -2: '#67a9cf', -3: '#2166ac'}
blab = {3: 'Hot spot (99%)', 2: 'Hot spot (95%)', 1: 'Hot spot (90%)', 0: 'Not significant',
        -1: 'Cold spot (90%)', -2: 'Cold spot (95%)', -3: 'Cold spot (99%)'}
bh = [Patch(fc=bcol[k], ec='grey', lw=0.4, label=blab[k]) for k in (3, 2, 1, 0, -1, -2, -3)]
for pre, name, fn in [('HSC', 'Land-Specific Carbon Emission (LSCE)', 'Map2_LSCE_Hotspots.png'),
                      ('HSH', 'Land Surface Temperature (LST)', 'Map3_LST_Hotspots.png')]:
    make_fig(lambda ax, y, pre=pre: g.plot(ax=ax, color=g[f'{pre}_{y}'].map(bcol), edgecolor='white', linewidth=0.1),
             f'Hot and Cold Spots of {name} in ' + CITY + ', 2000–2025', fn, handles=bh)

# 4. LSCE density
n1 = TwoSlopeNorm(vmin=-240, vcenter=0, vmax=275)
make_fig(lambda ax, y: g.plot(ax=ax, column=f'LSCE_{y}', cmap='RdYlGn_r', norm=n1, edgecolor='none'),
         'Land-Specific Carbon Emission Density in ' + CITY + ', 2000–2025',
         'Map4_LSCE_Density.png', cmap='RdYlGn_r', norm=n1,
         cblabel='LSCE (t CO$_2$ km$^{-2}$ yr$^{-1}$)   [negative = net sink]')

# 5. Normalized LST
n2 = Normalize(0, 1)
make_fig(lambda ax, y: g.plot(ax=ax, column=f'NLST_{y}', cmap='RdYlBu_r', norm=n2, edgecolor='none'),
         'Normalized Pre-monsoon Land Surface Temperature in ' + CITY + ', 2000–2025',
         'Map5_Normalized_LST.png', cmap='RdYlBu_r', norm=n2,
         cblabel='Normalized LST   (0 = coolest, 1 = hottest)')
print('DONE! Maps saved in', C.FIG_DIR)
