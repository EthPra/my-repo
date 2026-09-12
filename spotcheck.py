import pandas as pd
p = r"C:\MCXRAY\Sim\Wrapper\Golden\outputs\GaAsBi_100nm_x010_ATW_rho534_XrayIntensities.csv"
d = pd.read_csv(p, sep=r",\s*", engine="python")
d.columns = [c.strip() for c in d.columns]
d["Line"] = d["Line"].astype(str).str.strip()
print(d[d["Atomic number"] == 83][["Line", "Line energy (keV)", "Detector efficiency"]].to_string())