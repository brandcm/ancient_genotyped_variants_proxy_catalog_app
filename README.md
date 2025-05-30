# 🧬 Ancient Genotyped Variants Proxy Catalog App

This repository features a tool that identifies ancient genotyped variants (AGVs) from the <a href="https://reich.hms.harvard.edu/allen-ancient-dna-resource-aadr-downloadable-genotypes-present-day-and-ancient-dna-data" target="_blank">Allen Ancient DNA Resource</a> or AADR that occur in linkage disequilibrium (LD) with a variant of interest using data from <a href="http://topld.genetics.unc.edu/" target="_blank">TopLD</a>. AGVs in LD with a variant of interest are displayed and the results can be downloaded. If a queried variant is an AGV itself, summary data are provided and users can also download the individual genotypes. Bulk data on variants in LD with AGVs can be downloaded <a href="https://ucsf.box.com/s/0fm9squ3qxofxnhn669jm2xm8w91qntg" target="_blank">here</a> and bulk data on ancient genotypes can be downloaded <a href="https://ucsf.box.com/s/9uhclcmqzyp9ftktkiaayi61n4lb3jxy" target="_blank">here</a>. Users can search for variants using genomic position per the GRCh38/hg38 reference assembly or rsID. Please note that each query may take one to two minutes. Questions or comments about this tool? Please email colin.brand@ucsf.edu or tony@capralab.org.
<br><br>

Notes:
- Two measures of LD are available per variant pair: r-squared and D'.
- LD metrics are available for up to four ancestry groups per variant pair: African, East Asian, European, and South Asian.
- Genomic position for AGV-LD variant pairs use the GRCh38/hg38 reference assembly, whereas ancient genotypes downloaded from the app or retrieved from the VCFs use the GRCh37/hg19 reference assembly.
<br><br>

## 🚀 Quick Start

You can run this app in **three ways**:

1. Docker  
2. Python virtual environment (pip)  
3. Conda environment
<br><br>

## 🐳 Docker

### Build the image

```bash
git clone https://github.com/brandcm/ancient_genotyped_variants_proxy_catalog_app.git
cd ancient_genotyped_variants_proxy_catalog_app
open -a "Docker" # start Docker
docker build -t agvs_dash_app . # build image
```

### Run the container

```bash
docker run -p 8050:80 agvs_dash_app
```

Then open your browser at <a href="http://127.0.0.1:8050" target="_blank">http://127.0.0.1:8050</a>.
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
gunicorn app:server --bind 0.0.0.0:8050 --timeout 120
```

Then open your browser at <a href="http://127.0.0.1:8050" target="_blank">http://127.0.0.1:8050</a>.
<br><br>

## 🧪 Conda Environment

### Create the environment

```bash
git clone https://github.com/brandcm/ancient_genotyped_variants_proxy_catalog_app.git
cd ancient_genotyped_variants_proxy_catalog_app
conda env create -f environment.yml
conda activate AGVs_dash_app
```

### Run the app

```bash
gunicorn app:server --bind 0.0.0.0:8050 --timeout 120
```

Then open your browser at <a href="http://127.0.0.1:8050" target="_blank">http://127.0.0.1:8050</a>.
