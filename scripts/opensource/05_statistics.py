"""
05_statistics.py  -  Step 6a (docs/06_statistics_and_maps.md)

Cell-level relationships between land-specific carbon emission (LSCE) and
land surface temperature (LST) for every year, plus two figures.

Run:  python 05_statistics.py
Out:  04_outputs/RCC_LSCE_LST_statistics.csv
      05_figures/Fig_LSCE_vs_LST_scatter.png, Fig_correlation_and_dLST.png
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

import config as C

C.ensure_dirs()
df = pd.read_csv(C.OUT_DIR / "grid" / "RCC_grid_values.csv").replace(-9999, np.nan)
years = [y for y in C.YEARS if f"LSCE_{y}" in df.columns]

rows = []
for y in years:
    d = df[[f"LSCE_{y}", f"LST_{y}", f"NDVI_{y}", f"NDBI_{y}"]].dropna()
    L, Cc, V, B = d[f"LST_{y}"], d[f"LSCE_{y}"], d[f"NDVI_{y}"], d[f"NDBI_{y}"]
    X = np.column_stack([np.ones(len(d)), V, B])
    beta = np.linalg.lstsq(X, L, rcond=None)[0]
    r2_vb = 1 - ((L - X @ beta) ** 2).sum() / ((L - L.mean()) ** 2).sum()
    r = stats.pearsonr(Cc, L)[0]
    rows.append(dict(
        Year=y, r_LSCE_LST=r, R2_LSCE=r ** 2, rho_LSCE_LST=stats.spearmanr(Cc, L)[0],
        r_NDVI_LST=stats.pearsonr(V, L)[0], r_NDBI_LST=stats.pearsonr(B, L)[0], R2_NDVI_NDBI=r2_vb,
        r_LSCE_NDVI=stats.pearsonr(Cc, V)[0], r_LSCE_NDBI=stats.pearsonr(Cc, B)[0],
        LST_source=L[Cc > 0].mean(), LST_sink=L[Cc < 0].mean(),
        dLST=L[Cc > 0].mean() - L[Cc < 0].mean(),
        n_source=int((Cc > 0).sum()), share_source_pct=(Cc > 0).mean() * 100, meanLSCE=Cc.mean()))
s = pd.DataFrame(rows).round(3)
s.to_csv(C.OUT_DIR / "RCC_LSCE_LST_statistics.csv", index=False)
print(s[["Year", "r_LSCE_LST", "r_NDBI_LST", "dLST", "share_source_pct"]].to_string(index=False))
print("Note: neighbouring cells are spatially autocorrelated; report r, R2 and dLST as effect sizes.")

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})

# Scatter plots
ncol = 3
nrow = int(np.ceil(len(years) / ncol))
fig, axs = plt.subplots(nrow, ncol, figsize=(10, 3 * nrow), sharex=True, squeeze=False)
for ax in axs.flat[len(years):]:
    ax.axis("off")
for ax, y in zip(axs.flat, years):
    d = df[[f"LSCE_{y}", f"LST_{y}"]].dropna()
    x, l = d[f"LSCE_{y}"], d[f"LST_{y}"]
    ax.scatter(x, l, s=6, c=np.where(x > 0, "#c0392b", "#2e7d32"), alpha=0.45, edgecolors="none")
    lr = stats.linregress(x, l)
    xx = np.linspace(x.min(), x.max(), 50)
    ax.plot(xx, lr.intercept + lr.slope * xx, "k-", lw=1.2)
    ax.axvline(0, color="grey", lw=0.6, ls="--")
    ax.set_title(f"{y}   r = {lr.rvalue:.2f}, R² = {lr.rvalue ** 2:.2f}", fontsize=9, fontweight="bold")
    ax.grid(alpha=0.25)
for ax in axs[-1]:
    ax.set_xlabel("LSCE (t CO$_2$ km$^{-2}$ yr$^{-1}$)")
for ax in axs[:, 0]:
    ax.set_ylabel("Mean LST (°C)")
fig.tight_layout()
fig.savefig(C.FIG_DIR / "Fig_LSCE_vs_LST_scatter.png", dpi=300)
plt.close(fig)

# Correlation trend and source-sink temperature gap
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.8))
a1.plot(years, s.r_NDBI_LST, "o-", color="#6d4c41", label="NDBI")
a1.plot(years, s.r_LSCE_LST, "s-", color="#c0392b", label="LSCE")
a1.plot(years, s.r_NDVI_LST, "^-", color="#2e7d32", label="NDVI")
a1.axhline(0, color="grey", lw=0.6)
a1.set_ylabel("Pearson r with LST")
a1.set_title("(a) Correlation with LST")
a1.legend(frameon=False)
a1.grid(alpha=0.25)
a1.set_xticks(years)
a2.bar(years, s.dLST, width=3, color="#e67e22")
for x, v in zip(years, s.dLST):
    a2.text(x, v + 0.03, f"{v:.2f}", ha="center", fontsize=8)
a2.set_ylabel("ΔLST source − sink cells (°C)")
a2.set_title("(b) Thermal gap between carbon-source and sink cells")
a2.set_xticks(years)
a2.grid(alpha=0.25, axis="y")
fig.tight_layout()
fig.savefig(C.FIG_DIR / "Fig_correlation_and_dLST.png", dpi=300)
plt.close(fig)
print("DONE! Statistics and figures saved.")
