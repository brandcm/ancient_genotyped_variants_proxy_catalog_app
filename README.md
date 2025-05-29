# 🧬 Ancient Genotyped Variants Proxy Catalog App

This is a Dash web application for identifying ancient genotyped variants (AGVs) from the Allen Ancient DNA Resource (AADR) that occur in linkage disequilibrium (LD) with a variant of interest using data from TopLD.
<br><br>

## 🚀 Quick Start

You can run this app in **three ways**:

1. Docker  
2. Python virtual environment (pip)  
3. Conda environment

Just clone this repo `git clone https://github.com/brandcm/ancient_genotyped_variants_proxy_catalog_app.git` and navigate to the repo on the command line.
<br><br>

## 🐳 Docker

### Build the image

```bash
open -a "Docker" # start Docker
cd ancient_genotyped_variants_proxy_catalog_app # navigate into app directory
docker build -t agvs_dash_app . # build image
```

### Run the container

```bash
docker run -p 8050:80 agvs_dash_app
```

Then open your browser at [http://127.0.0.1:8050](http://127.0.0.1:8050).
<br><br>

## 🐍 Python Virtual Environment (pip)

### Create the environment

```bash
python -m venv {virtual_environment_name}
source {virtual_environment_name}/bin/activate	# On Windows: {virtual_environment_name}\Scripts\activate
pip install -r requirements.txt
```

### Run the app

```bash
python app.py
```

Then open your browser at [http://127.0.0.1:8050](http://127.0.0.1:8050).
<br><br>

## 🧪 Conda Environment

### Create the environment

```bash
conda env create -f environment.yml
conda activate AGV_dash_app
```

### Run the app

```bash
python app.py
```

Then open your browser at [http://127.0.0.1:8050](http://127.0.0.1:8050).