# 🌌 QAstro

**QAstro** is a web-based application designed to facilitate the gathering and visualization of astronomical data. 
Built with [Streamlit](https://streamlit.io) and hosted on **Streamlit Cloud**. QAstro provides a simple, elegant interface to query multiple astronomical databases **simultaneously**.

---

## 🚀 Overview

QAstro was born out of a common challenge in the astronomy community — the tedious process of collecting data from various astronomical databases. Researchers often spend a significant amount of time switching between platforms to compile data for a single celestial object.

**QAstro unifies this process** by allowing users to retrieve and view data from multiple sources in one go.

---

## 🔍 Presently Supported Databases

- [SIMBAD](http://simbad.u-strasbg.fr/simbad/)
- [SDSS (Sloan Digital Sky Survey)](https://www.sdss.org/)
- [GAIA Archive](https://gea.esac.esa.int/archive/)
- [IRAS](https://irsa.ipac.caltech.edu/Missions/iras.html)

---

## 💡 Best Use Cases

- Researchers compiling data on a specific astronomical object.
- Educators showcasing how data differs across major databases.
- Astronomy enthusiasts exploring celestial object info without needing to jump across platforms.

---

## 🛠️ Tech Stack

- **Frontend / App**: [Streamlit](https://streamlit.io)
- **Backend**: Python ≥ 3.12
- **Hosting**: Streamlit Cloud
- **Data Sources**: Various public astronomical databases

---

## 📦 Setup Instructions

> **Note**: Requires Python **3.12 or higher**

```bash
git clone git@github-personal:vanshaj18/qastro.git
cd qastro
<python version> -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
---

## 📄 License

This project is licensed under the [Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).  
You are free to use, copy, modify, and distribute the software and associated documentation, provided that the original author (Vanshaj) is credited.

