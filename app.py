import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import linregress
import os

st.set_page_config(layout="wide")
st.title("Multi-Compound UV-Vis & Beer-Lambert Plotter")

st.markdown("""
Upload your `.txt` spectral data files into the `data/` folder.
Each file must contain **two tab-separated columns**:
1. Wavelength (nm)
2. Absorbance

Below, enter the name, wavelength range, and associated files + concentrations for **each compound**.
""")

# === File loader ===
data_dir = "data"
all_files = sorted([f for f in os.listdir(data_dir) if f.endswith(".txt")])
if not all_files:
    st.warning("No data files found in the 'data/' folder.")
    st.stop()

# === Compound Input Section ===
st.sidebar.header("Define Compounds")
compound_count = st.sidebar.number_input("Number of Compounds", min_value=1, max_value=5, value=3, step=1)

compound_data = []
used_files = set()

for i in range(compound_count):
    st.sidebar.markdown(f"### Compound {i+1}")
    name = st.sidebar.text_input(f"Compound {i+1} Name", value=f"Compound {i+1}")
    wl_start = st.sidebar.number_input(f"Wavelength Start (nm) - {name}", value=185, step=1, key=f"start{i}")
    wl_end = st.sidebar.number_input(f"Wavelength End (nm) - {name}", value=320, step=1, key=f"end{i}")

    st.sidebar.markdown(f"**Assign files for {name}:**")
    selected = st.sidebar.multiselect(f"Files for {name}", [f for f in all_files if f not in used_files], key=f"files{i}")

    file_conc_map = {}
    for fname in selected:
        val = st.sidebar.text_input(f"Concentration (mol dm⁻³) for {fname}", value="0.001", key=f"conc_{i}_{fname}")
        try:
            file_conc_map[fname] = float(val)
        except:
            st.sidebar.error(f"Invalid concentration for {fname} in {name}")
            st.stop()

    used_files.update(selected)
    compound_data.append({
        "name": name,
        "files": file_conc_map,
        "xrange": (wl_start, wl_end)
    })

# === Plotting ===
for compound in compound_data:
    name = compound["name"]
    files = compound["files"]
    wl_start, wl_end = compound["xrange"]

    st.header(f"{name}")
    st.subheader("UV-Vis Spectrum")

    fig, ax = plt.subplots(figsize=(10, 5))
    max_abs = 0
    peak_data = []

    for fname, conc in files.items():
        df = pd.read_csv(os.path.join(data_dir, fname), sep="\t", header=None, names=["Wavelength", "Absorbance"])
        df = df[(df["Wavelength"] >= wl_start) & (df["Wavelength"] <= wl_end)]
        df = df[df["Absorbance"] > 0]

        sci_val = f"{conc:.2e}".split("e")
        label = f"${sci_val[0]} \\times 10^{{{int(sci_val[1])}}}$"
        ax.plot(df["Wavelength"], df["Absorbance"], label=label)

        peak = df.loc[df["Absorbance"].idxmax()]
        peak_data.append({"Concentration": conc, "Absorbance": peak["Absorbance"], "Lambda_max": peak["Wavelength"]})

        if df["Absorbance"].max() > max_abs:
            max_abs = df["Absorbance"].max()

    ax.set_xlabel("Wavelength / nm")
    ax.set_ylabel("Absorbance")
    ax.set_xlim(wl_start, wl_end)
    ax.set_ylim(0, max_abs * 1.1)
    ax.set_title(f"{name} - UV-Vis Spectrum")
    ax.legend(title="Concentration / mol dm⁻³")
    st.pyplot(fig)

    # === Beer-Lambert ===
    st.subheader("Beer-Lambert Plot")
    df_peak = pd.DataFrame(peak_data).sort_values("Concentration")
    slope, intercept, r_value, _, _ = linregress(df_peak["Concentration"], df_peak["Absorbance"])
    df_peak["Fitted"] = slope * df_peak["Concentration"] + intercept

    fig2, ax2 = plt.subplots(figsize=(8, 5))
    ax2.scatter(df_peak["Concentration"], df_peak["Absorbance"], color='blue')
    line, = ax2.plot(df_peak["Concentration"], df_peak["Fitted"], color='red', linestyle='--',
                     label=f"$\\varepsilon$ = {round(slope)} L mol⁻¹ cm⁻¹\n$R^2$ = {r_value**2:.4f}")

    ax2.set_xlabel("Concentration / mol dm⁻³")
    ax2.set_ylabel("Absorbance")
    ax2.set_title(f"{name} - Beer-Lambert Plot")
    ax2.legend(handles=[line])
    st.pyplot(fig2)

    st.subheader("Peak Absorbance Table")
    st.dataframe(df_peak)

st.success("Done rendering all compounds.")
