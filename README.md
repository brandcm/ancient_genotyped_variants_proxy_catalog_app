# 🧬 Ancient Genotyped Variants Proxy Catalog App

This is a Dash web application for identifying ancient genotyped variants (AGVs) from the Allen Ancient DNA Resource (AADR) that occur in linkage disequilibrium (LD) with a variant of interest using data from TopLD.

## 🚀 Quick Start

You can run this app in **three ways**:

1. Docker  
2. Python virtual environment (pip)  
3. Conda environment  

## 🐳 Docker

### Build the image

```bash
docker build -t agv-dash-app .
```

### Run the container

```bash
docker run -p 8050:8050 agv-dash-app
```

Then open your browser at [http://127.0.0.1:8050](http://127.0.0.1:8050).

## 🐍 Python Virtual Environment (pip)

### Create the environment

```bash
python -m venv venv
source venv/bin/activate	# On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Run the app

```bash
python app.py
```

Then open your browser at [http://127.0.0.1:8050](http://127.0.0.1:8050).

## 🧪 Conda Environment

### Create the environment

```bash
conda env create -f environment.yml
conda activate agv-dash-app
```

### Run the app

```bash
python app.py
```

Then open your browser at [http://127.0.0.1:8050](http://127.0.0.1:8050).