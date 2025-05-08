import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import linregress
import os
from io import BytesIO

st.set_page_config(layout="wide")
st.title("Multi-Compound UV-Vis & Beer-Lambert Plotter")

# ✅ Ensure the data directory exists
os.makedirs("data", exist_ok=True)

st.markdown("""
Upload your `.txt` files (tab-separated: Wavelength and Absorbance).
Then manually enter the **concentration** and **wavelength range** for each file.
""")

# === File uploader ===
uploaded_files = st.file_uploader("Upload TXT Files", type="txt", accept_multiple_files=True)

file_entries = []

if uploaded_files:
    st.subheader("Input Settings Per File")
    for i, uploaded_file in enumerate(uploaded_files):
        with open(os.path.join("data", uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.markdown(f"**{uploaded_file.name}**")
        col1, col2, col3 = st.columns(3)
        with col1:
            conc = st.text_input(f"Concentration (mol dm⁻³) for {uploaded_file.name}", value="0.001", key=f"conc_{i}")
        with col2:
            wl_start = st.number_input(f"Wavelength Start (nm) for {uploaded_file.name}", value=185, step=1, key=f"start_{i}")
        with col3:
            wl_end = st.number_input(f"Wavelength End (nm) for {uploaded_file.name}", value=320, step=1, key=f"end_{i}")

        try:
            file_entries.append({
                "file": uploaded_file.name,
                "concentration": float(conc),
                "wl_start": wl_start,
                "wl_end": wl_end
            })
        except:
            st.error(f"Invalid concentration input for {uploaded_file.name}")

# === Plotting if data is present ===
if file_entries:
    st.header("Combined UV-Vis Spectrum")
    fig, ax = plt.subplots(figsize=(10, 5))
    max_abs = 0
    peak_data = []

    for entry in file_entries:
        df = pd.read_csv(os.path.join("data", entry["file"]), sep="\t", header=None, names=["Wavelength", "Absorbance"])
        df = df[(df["Wavelength"] >= entry["wl_start"]) & (df["Wavelength"] <= entry["wl_end"])]
        df = df[df["Absorbance"] > 0]

        sci_val = f"{entry['concentration']:.2e}".split("e")
        label = f"${sci_val[0]} \times 10^{{{int(sci_val[1])}}}$"
        ax.plot(df["Wavelength"], df["Absorbance"], label=label)

        if not df.empty:
            peak = df.loc[df["Absorbance"].idxmax()]
            peak_data.append({"Concentration": entry["concentration"], "Absorbance": peak["Absorbance"], "Lambda_max": peak["Wavelength"]})

            if df["Absorbance"].max() > max_abs:
                max_abs = df["Absorbance"].max()

    ax.set_xlabel("Wavelength / nm")
    ax.set_ylabel("Absorbance")
    ax.set_ylim(0, max_abs * 1.1)
    ax.legend(title="Concentration / mol dm⁻³")
    st.pyplot(fig)

    buf1 = BytesIO()
    fig.savefig(buf1, format="png")
    st.download_button("Download UV-Vis Plot", buf1.getvalue(), file_name="combined_uvvis.png", mime="image/png")

    # === Beer-Lambert ===
    st.subheader("Beer-Lambert Plot")
    df_peak = pd.DataFrame(peak_data).sort_values("Concentration")

    if len(df_peak) >= 2:
        slope, intercept, r_value, _, _ = linregress(df_peak["Concentration"], df_peak["Absorbance"])
        df_peak["Fitted"] = slope * df_peak["Concentration"] + intercept

        fig2, ax2 = plt.subplots(figsize=(8, 5))
        ax2.scatter(df_peak["Concentration"], df_peak["Absorbance"], color='blue')
        line, = ax2.plot(df_peak["Concentration"], df_peak["Fitted"], color='red', linestyle='--',
                         label=f"$\\varepsilon$ = {round(slope)} L mol⁻¹ cm⁻¹\n$R^2$ = {r_value**2:.4f}")

        ax2.set_xlabel("Concentration / mol dm⁻³")
        ax2.set_ylabel("Absorbance")
        ax2.set_title("Beer-Lambert Plot")
        ax2.legend(handles=[line])
        st.pyplot(fig2)

        buf2 = BytesIO()
        fig2.savefig(buf2, format="png")
        st.download_button("Download Beer-Lambert Plot", buf2.getvalue(), file_name="beer_lambert.png", mime="image/png")
    else:
        st.warning("At least two valid data points are required to compute the Beer-Lambert regression.")

    st.subheader("Peak Absorbance Table")
    st.dataframe(df_peak)

st.success("Done rendering all files.")
