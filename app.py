import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import linregress
from io import BytesIO

st.set_page_config(page_title="UV-Vis & Beer-Lambert Analyzer", layout="wide")
st.title("UV-Vis Spectrum & Beer-Lambert Plot Generator")

st.markdown("""
Upload your UV-Vis `.txt` files (tab-delimited, two columns: wavelength and absorbance),
and enter corresponding concentrations (in mol/dm³) below.

**Note**: Data will be trimmed to 190–320 nm and only positive absorbance values will be plotted.
""")

uploaded_files = st.file_uploader("Upload your .txt data files", type="txt", accept_multiple_files=True)
concentrations_input = st.text_input("Enter concentrations (mol/dm³) in order, comma-separated")

if uploaded_files and concentrations_input:
    try:
        concentrations = [float(x.strip()) for x in concentrations_input.split(",")]
        if len(concentrations) != len(uploaded_files):
            st.error("Number of concentrations must match number of files.")
        else:
            peak_data = []
            fig_uvvis, ax_uvvis = plt.subplots(figsize=(10, 5))

            for file, conc in zip(uploaded_files, concentrations):
                df = pd.read_csv(file, sep="\t", header=None, names=["Wavelength", "Absorbance"])
                df = df[(df["Wavelength"] >= 190) & (df["Wavelength"] <= 320) & (df["Absorbance"] > 0)]
                ax_uvvis.plot(df["Wavelength"], df["Absorbance"], label=f"{conc:.6f} mol/L")
                peak = df.loc[df["Absorbance"].idxmax()]
                peak_data.append({"Concentration": conc, "Absorbance": peak["Absorbance"], "Lambda_max": peak["Wavelength"]})

            ax_uvvis.set_title("UV-Vis Spectra")
            ax_uvvis.set_xlabel("Wavelength (nm)")
            ax_uvvis.set_ylabel("Absorbance")
            ax_uvvis.legend(title="Concentration")
            ax_uvvis.grid(True)
            st.pyplot(fig_uvvis)

            buf_uvvis = BytesIO()
            fig_uvvis.savefig(buf_uvvis, format="png")
            st.download_button("📥 Download UV-Vis Plot", buf_uvvis.getvalue(), "uvvis_plot.png", "image/png")

            df_peaks = pd.DataFrame(peak_data).sort_values("Concentration")
            slope, intercept, r_value, _, _ = linregress(df_peaks["Concentration"], df_peaks["Absorbance"])
            df_peaks["Fitted"] = slope * df_peaks["Concentration"] + intercept

            fig_beer, ax_beer = plt.subplots(figsize=(7, 5))
            ax_beer.scatter(df_peaks["Concentration"], df_peaks["Absorbance"], color='blue', label='Measured')
            ax_beer.plot(df_peaks["Concentration"], df_peaks["Fitted"], color='red', linestyle='--',
                         label=f"Fit: ε = {slope:.2f} L·mol⁻¹·cm⁻¹\n$R^2$ = {r_value**2:.4f}")
            ax_beer.set_title("Beer-Lambert Plot")
            ax_beer.set_xlabel("Concentration (mol/dm³)")
            ax_beer.set_ylabel("Absorbance")
            ax_beer.legend()
            ax_beer.grid(True)
            st.pyplot(fig_beer)

            buf_beer = BytesIO()
            fig_beer.savefig(buf_beer, format="png")
            st.download_button("📥 Download Beer-Lambert Plot", buf_beer.getvalue(), "beerlambert_plot.png", "image/png")

            st.success("Analysis complete.")

    except Exception as e:
        st.error(f"An error occurred: {e}")
else:
    st.info("Upload your files and enter concentrations to begin.")
