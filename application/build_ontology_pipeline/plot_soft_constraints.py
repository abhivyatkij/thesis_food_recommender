import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os 
# -------- load CSV -------------------------------------------------------

build_ontology_out_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'out_build_ontology_pipeline')
csv_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "in", "soft_constraint_plot.csv")

# 1) Load your CSV  ────────────────────────────────────────────────
df = pd.read_csv(csv_file_path)
# -------- columns to plot -----------------------------------------------
diff_cols = [
    "free_sugar_diff", "fibre_diff", "sat_fat_diff",
    "sodium_diff", "potassium_diff", "total_fat_diff"
]
diff_cols = [c for c in diff_cols if c in df.columns]
heat_df   = df.set_index("Scenario name")[diff_cols]

# -------- styling --------------------------------------------------------
plt.rcParams.update({
    "font.family": "Times New Roman",   # switch to Georgia if Times isn’t available
    "font.size": 10,
    "axes.edgecolor": "#444444",
    "axes.linewidth": 0.7,
})

fig, ax = plt.subplots(figsize=(10, 5), dpi=120)

# diverging palette: positive → blue, negative → red
lim  = np.nanmax(np.abs(heat_df.values))
cmap = plt.get_cmap("RdBu_r")          # _r reverses → + blue, – red
im   = ax.imshow(heat_df, cmap=cmap, vmin=-lim, vmax=lim)

# annotations (small, no plus sign if you prefer)
for i in range(heat_df.shape[0]):
    for j in range(heat_df.shape[1]):
        val = heat_df.iat[i, j]
        ax.text(j, i, f"{val:+}".replace("+",""),  # remove explicit + sign if desired
                va='center', ha='center',
                fontsize=7, 
                color="black" if abs(val) < lim*0.25 else "white")

# ticks / labels
ax.set_xticks(range(len(heat_df.columns)))
ax.set_xticklabels([c.replace("_diff","").replace("_"," ").title() for c in heat_df.columns],
                   rotation=45, ha="right")
ax.set_yticks(range(len(heat_df.index)))
ax.set_yticklabels(heat_df.index)

ax.set_title("Signed Nutrient Gaps  (Blue = above / under‑cap,  Red = excess / deficit)",
             pad=12, fontsize=12)

cbar = plt.colorbar(im, ax=ax, shrink=0.8, pad=0.02)
cbar.set_label("mg or g  (Positive = good, Negative = bad)")

plt.tight_layout()

plt.show()