📊 UV-Vis Spectrum & Beer-Lambert Plot Generator
This web app allows users to upload UV-Vis spectroscopy data in .txt format and automatically:

📈 Plot UV-Vis absorption spectra (190–320 nm, Absorbance > 0 only)

📊 Generate a Beer-Lambert calibration curve

⚙️ Calculate molar absorptivity (ε) and linearity (R²)

✅ Features:
Upload multiple .txt files (tab-delimited with wavelength and absorbance columns)

Input matching concentrations (in mol/dm³)

Spectra cropped and smoothed automatically

Real-time plotting with Matplotlib

Ideal for chemists, researchers, and lab analysts

🧪 Built With:
Python 3

Streamlit

Pandas, Matplotlib, SciPy

📁 File Requirements:
Each file must have two columns: Wavelength (nm) and Absorbance

No headers required (first line should contain data)
