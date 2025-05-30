# === Load Packages ===
from dash import dash, dash_table, dcc, html
from dash.dependencies import Input, Output, State
from io import BytesIO
import dash_bootstrap_components as dbc
import gzip
import json
import pickle
import polars as pl
import requests

# === APP LAYOUT ===
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP])
server = app.server

app.layout = dbc.Container([
	html.H1('Ancient Genotyped Variants Proxy Catalog'),
	html.P([
		'This tool identifies ancient genotyped variants (AGVs) from the ',
		html.A('Allen Ancient DNA Resource', href='https://reich.hms.harvard.edu/allen-ancient-dna-resource-aadr-downloadable-genotypes-present-day-and-ancient-dna-data', target='_blank', style={'color': 'blue', 'textDecoration': 'underline'}),
		' that occur in linkage disequilibrium (LD) with a variant of interest using data from ',
		html.A('TopLD', href='http://topld.genetics.unc.edu/', target='_blank', style={'color': 'blue', 'textDecoration': 'underline'}),
		'. Individual variants can be queried below or bulk data can be downloaded ',
		html.A('here', href='https://ucsf.box.com/s/0fm9squ3qxofxnhn669jm2xm8w91qntg', target='_blank', style={'color': 'blue', 'textDecoration': 'underline'}),
		'. If a variant of interest is an AGV itself, summary data are displayed. Individual sample genotypes can also be downloaded and bulk AGV genotypes can be found ',
		html.A('here', href='https://ucsf.box.com/s/9uhclcmqzyp9ftktkiaayi61n4lb3jxy', target='_blank', style={'color': 'blue', 'textDecoration': 'underline'}),
		'. The summary function can also be used after the identification of one or more AGVs in LD with a variant of interest. Questions or comments about this tool? Please email colin.brand@ucsf.edu or tony@capralab.org.'
	]),
	dbc.Row([
		dbc.Col([
			html.H3('Variant Information'),
			html.P('Please enter either chromosome and position information in hg38 reference coordinates or the rsID for a variant of interest. Variants may have multiple rsIDs—those used here are from TopLD. We recommend searching via genomic position.'),
			dbc.Row([
				dbc.Col([
					html.H6('Chromosome'),
					dcc.Input(type='text', placeholder='chr11', id='input_chr', style={'width': '10rem'}),
				], width='auto', style={'margin-right': '15px'}),
				dbc.Col([
					html.H6('Position'),
					dcc.Input(type='number', placeholder='63290453', id='input_pos', style={'width': '10rem'}),
				], width='auto', style={'margin-right': '15px'}),
				dbc.Col([
					html.H6('OR', style={'textAlign': 'center', 'margin-top': '35px'})
				], width='auto', style={'margin-right': '15px'}),
				dbc.Col([
					html.H6('rsID'),
					dcc.Input(type='text', placeholder='rs1790218', id='input_rsID', style={'width': '10rem'}),
				], width='auto'),
				dbc.Col([
					dbc.Button(
						children=[html.I(className="bi bi-search"), " Submit"],
						id="submit-button",
						color="primary",
						size="sm",
						style={
							'alignSelf': 'center',
							'border-radius': '8px',
							'box-shadow': '2px 2px 5px rgba(0,0,0,0.2)',
							'display': 'inline-block',
							'font-size': '16px',
							'margin-left': '15px',
							'margin-top': '22px',
							'padding': '5px 10px',
							'width': '200px'
						}
					),
				], width='auto'),
				dbc.Col([
					html.Div(id='AGV_message', children='', style={'alignSelf': 'center', 'color': 'green', 'margin-top': '20px', 'textAlign': 'center'})
				], width='auto'),
			], style={'margin-bottom': '20px'})
		], width=12),
	], style={'margin-bottom': '20px'}),
	dbc.Row([
		dbc.Col([
			html.H3(id='AGV_summary_header', children='AGV Summary', style={'display': 'none'}),
			html.P(
				id='AGV_summary_description', children="The following tables present summary data on an AGV, including genotypes from four high-coverage archaic hominin genomes and allele frequencies of the AGV alternate allele across different regions over various time periods. Sample sizes for each region/time bin are provided next to the allele frequency in parentheses. Frequencies are calculated from a single sample per individual as some individuals in the AADR have multiple genotype calls from different sequencing approaches. Archaic hominins and reference sequences were excluded from allele frequency calculations. All genotype data, including hominins and reference sequences, are available when downloaded.",
				style={'display': 'none'}
			),
			dbc.Row([
				dbc.Col([
					dash_table.DataTable(
						id="AGV_information_results",
						columns=[
							{"name": "Chromosome", "id": "AGV_chr"},
							{"name": "Position", "id": "AGV_pos"},
							{"name": "rsID", "id": "AGV_rsID"},
							{"name": "Ref Allele", "id": "AGV_ref"},
							{"name": "Alt Allele", "id": "AGV_alt"}
						],
						data=[{
							"AGV_chr": "",
							"AGV_pos": "",
							"AGV_rsID": "",
							"AGV_ref": "",
							"AGV_alt": ""
						}],
						style_cell={
							'font-family': 'Arial, san-serif',
							'font-size': '14px',
							'padding': '8px',
							'textAlign': 'center',
							'width': '20%'
						},
						style_header={
							'backgroundColor': '#f8f9fa',
							'fontWeight': 'bold',
							'textAlign': 'center'
						},
						style_table={'display': 'none', 'margin-bottom': '45px', 'margin-top': '8px', 'width': '100%'},
					),
				], style={'margin-bottom': '45px', 'margin-top': '8px'}),
			]),
			dbc.Row([
				dbc.Col([
					html.H4(
						id='archaic_genotypes_table_header',
			 			children=['High-Coverage Archaic Hominin Genotypes', 
					], style={'display': 'none'}),
					html.Div(
						id='archaic_genotypes_table_container',
						children=[
							dash_table.DataTable(
								id='archaic_genotypes_table_results',
								columns = [
									{"name": "Altai", "id": "Altai"},
									{"name": "Chagyrskaya", "id": "Chagyrskaya"},
									{"name": "Denisovan", "id": "Denisovan"},
									{"name": "Vindija", "id": "Vindija"}
								],
								data=[
									{"Altai": "", "Chagyrskaya": "", "Denisovan": "", "Vindija": ""}
								],
								style_cell={
									'font-family': 'Arial, san-serif',
									'font-size': '14px',
									'padding': '8px',
									'textAlign': 'center',
									'width': '25%'
								},
								style_header={
									'backgroundColor': '#f8f9fa',
									'fontWeight': 'bold',
									'textAlign': 'center'
								},
								style_table={'display': 'block', 'margin-bottom': '45px', 'margin-top': '8px', 'width': '100%'},
								editable=False,
								tooltip_header={
									"Altai": "Lineage: Neanderthal, Specimen: Denisova 5",
									"Chagyrskaya": "Lineage: Neanderthal, Specimen: Chagyrskaya 5",
									"Denisovan": "Lineage: Denisovan, Specimen: Denisova 3",
									"Vindija": "Lineage: Neanderthal, Specimen: Vindija 33.19"
								},
								tooltip_delay=0,
								tooltip_duration=None
							)
						],
						style={'display': 'none'}
					),
				])
			]),
			html.H4(id='AGV_allele_frequencies_table_header', children='AGV Allele Frequencies through Time by Region', style={'display': 'none'}),
			html.Div(id='AGV_allele_frequencies_table_container', children=[
				dash_table.DataTable(
					id='AGV_allele_frequencies_table_results',
					columns=[
						{"name": "Region", "id": "Region"},
						{"name": "Present", "id": "Present"},
						{"name": "(0-1 ka]", "id": "1000"},
						{"name": "(1-2 ka]", "id": "2000"},
						{"name": "(2-3 ka]", "id": "3000"},
						{"name": "(3-4 ka]", "id": "4000"},
						{"name": "(4-5 ka]", "id": "5000"},
						{"name": "(5-10 ka]", "id": "10000"},
						{"name": "(10-15 ka]", "id": "15000"},
						{"name": "(15-20 ka]", "id": "20000"},
						{"name": "(20-30 ka]", "id": "30000"},
						{"name": "(30-40 ka]", "id": "40000"},
						{"name": "(40-50 ka]", "id": "50000"},
					],
					data=[
						{"Region": "Africa", "Present": "", "1000": "", "2000": "", "3000": "", "4000": "", "5000": "", "10000": "", "15000": "", "20000": "", "30000": "", "40000": "", "50000":""},
						{"Region": "Americas", "Present": "", "1000": "", "2000": "", "3000": "", "4000": "", "5000": "", "10000": "", "15000": "", "20000": "", "30000": "", "40000": "", "50000":""},
						{"Region": "East Asia", "Present": "", "1000": "", "2000": "", "3000": "", "4000": "", "5000": "", "10000": "", "15000": "", "20000": "", "30000": "", "40000": "", "50000":""},
						{"Region": "Europe", "Present": "", "1000": "", "2000": "", "3000": "", "4000": "", "5000": "", "10000": "", "15000": "", "20000": "", "30000": "", "40000": "", "50000":""},
						{"Region": "Oceania", "Present": "", "1000": "", "2000": "", "3000": "", "4000": "", "5000": "", "10000": "", "15000": "", "20000": "", "30000": "", "40000": "", "50000":""},
						{"Region": "South Asia", "Present": "", "1000": "", "2000": "", "3000": "", "4000": "", "5000": "", "10000": "", "15000": "", "20000": "", "30000": "", "40000": "", "50000":""},
						{"Region": "West Asia", "Present": "", "1000": "", "2000": "", "3000": "", "4000": "", "5000": "", "10000": "", "15000": "", "20000": "", "30000": "", "40000": "", "50000":""},
						{"Region": "Total", "Present": "", "1000": "", "2000": "", "3000": "", "4000": "", "5000": "", "10000": "", "15000": "", "20000": "", "30000": "", "40000": "", "50000":""}
					],
					style_cell={
						'font-family': 'Arial, san-serif',
						'font-size': '14px',
						'padding': '8px',
						'textAlign': 'center'
					},
					style_header={
						'backgroundColor': '#f8f9fa',
						'fontWeight': 'bold',
						'textAlign': 'center'
					},
					style_table={'display': 'block', 'margin-top': '10px', 'width': '100%'},
					editable=False
				)
			],
			style={'display': 'none'})
		])
	]),
	dcc.Store(id='all_genotypes_store', storage_type='session'),
	dbc.Row([
		dbc.Col([
			dbc.Button(
				children=[html.I(className="bi bi-download"), " Download AGV Genotypes"],
				id="download-genotypes-button",
				color="primary",
				size="lg",
				style={
					'font-size': '16px',
					'width': '600px',
					'display': 'none',
					'margin-top': '20px',
					'textAlign': 'center',
				}
			),
			dcc.Download(id="download-genotypes-csv")
		], width=12, style={'display': 'flex', 'justifyContent': 'flex-end'})
	], style={'margin-top': '10px', 'padding-bottom': '30px'}),
	dbc.Row([
		html.H3('AGVs in LD with Variant of Interest', style={'margin-bottom': '15px'}),
	]),
	dbc.Row([
		dbc.Col([
			dash_table.DataTable(
				id='AGVs_in_LD_table',
				columns=[
					{"name": ["Variant of Interest", "Chromosome"], "id": "chr"},
					{"name": ["Variant of Interest", "Position"], "id": "LDV_pos"},
					{"name": ["Variant of Interest", "Ref Allele"], "id": "LDV_ref"},
					{"name": ["Variant of Interest", "Alt Allele"], "id": "LDV_alt"},
					{"name": ["Variant of Interest", "rsID"], "id": "LDV_rsID"},
					{"name": ["Ancient Genotyped Variant", "Position"], "id": "AGV_pos"},
					{"name": ["Ancient Genotyped Variant", "Ref Allele"], "id": "AGV_ref"},
					{"name": ["Ancient Genotyped Variant", "Alt Allele"], "id": "AGV_alt"},
					{"name": ["Ancient Genotyped Variant", "rsID"], "id": "AGV_rsID"},
					{"name": ["LD Information ℹ️", "Ancestry Groups"], "id": "populations"},
					{"name": ["LD Information ℹ️", "r²"], "id": "r2"},
					{"name": ["LD Information ℹ️", "D'"], "id": "D'"},
					{"name": ["LD Information ℹ️", "Correlation"], "id": "corr"}
				],
				data=[],
				merge_duplicate_headers=True,
				page_size=10,
				sort_action="native",
				style_cell={
					'font-family': 'Arial, san-serif',
					'font-size': '14px',
					'padding': '10px',
					'textAlign': 'center'
				},
				style_data={
					'height': 'auto',
					'whiteSpace': 'normal'
				},
				style_header={
					'font-family': 'Arial, san-serif',
					'font-size': '16px',
					'fontWeight': 'bold',
					'textAlign': 'center'
				},
				style_header_conditional=[
					{'if': {'header_index': 1}, 'fontWeight': 'normal', 'font-size': '14px'}
				],
				style_table={'overflowX': 'auto'},
				tooltip_header={
					"populations": "LD metrics are displayed in the same order as ancestry groups",
					"r2": "LD metrics are displayed in the same order as ancestry groups",
					"D'": "LD metrics are displayed in the same order as ancestry groups",
					"corr": "LD metrics are displayed in the same order as ancestry groups"
				},
				tooltip_delay=0,
				tooltip_duration=None,
			)
		], width=12)
	]),
	dbc.Row([
		dbc.Col([
			dbc.Button(
				children=[html.I(className="bi bi-download"), " Download AGVs"],
				id="download-AGVs-button",
				color="primary",
				size="md",
				style={
					'font-size': '16px',
					'width': '200px',
					'display': 'none',
					'margin-top': '20px',
					'textAlign': 'center',
				}
			),
			dcc.Download(id="download-AGVs-csv")
		], width=12, style={'display': 'flex', 'justifyContent': 'flex-end'})
	], style={'margin-top': '10px', 'padding-bottom': '30px'})
])

# === MAIN CALLBACK ===
@app.callback(
	Output('AGV_message', 'children'),
	Output('AGV_summary_header', 'style'),
	Output('AGV_summary_description', 'style'),
	Output('AGV_information_results', 'data'),
	Output('AGV_information_results', 'style_table'),
	Output('archaic_genotypes_table_container', 'style'),
	Output('archaic_genotypes_table_header', 'style'),
	Output('archaic_genotypes_table_results', 'data'),
	Output('AGV_allele_frequencies_table_container', 'style'),
	Output('AGV_allele_frequencies_table_header', 'style'),
	Output('AGV_allele_frequencies_table_results', 'data'),
	Output('all_genotypes_store', 'data'),
	Output('AGVs_in_LD_table', 'data'),
	Input('submit-button', 'n_clicks'),
	State('input_chr', 'value'),
	State('input_pos', 'value'),
	State('input_rsID', 'value')
)

# === FUNCTION: Run App ===
def query_AGVs(n_clicks, input_chr, input_pos, input_rsID):
	if n_clicks:
		if (input_chr and input_pos and input_rsID) or (not input_chr and not input_pos and not input_rsID):
			return "Please enter either chromosome and position OR rsID, not both.", {'display': 'none'}, {'display': 'none'}, [], {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, [], {'display': 'none'}, {'display': 'none'}, [], [], []

		input_chr, error = process_chr(input_chr)
		if error:
			return error, {'display': 'none'}, {'display': 'none'}, [], {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, [], {'display': 'none'}, {'display': 'none'}, [], [], []

		variant_chr, variant_pos, variant_rsID, variant_ref, variant_alt, is_AGV = process_variant(input_chr, input_pos, input_rsID)

		AGV_data, archaic_GTs, AFs_summary, all_GTs = [], [], [], []
		sorted_AGV_LDVs = pl.DataFrame()

		if is_AGV:
			archaic_GTs_df, all_GTs_df, AFs_summary_df = retrieve_GTs_and_calculate_AFs(variant_chr, variant_rsID)
			if AFs_summary_df is not None:
				AGV_data = [{"AGV_chr": variant_chr, "AGV_pos": variant_pos, "AGV_rsID": variant_rsID, "AGV_ref": variant_ref, "AGV_alt": variant_alt}]
				archaic_GTs = [archaic_GTs_df]
				all_GTs = all_GTs_df.to_dicts()
				AFs_summary = AFs_summary_df.to_dicts()

		with open('files/AGVs_Box_URLs.json', 'r') as AGVs_URLs:
			AGVs_URLs_dict = json.load(AGVs_URLs)
		AGV_chr_URL = AGVs_URLs_dict.get(f'chr{variant_chr}')

		try:
			response = requests.get(f'https://ucsf.box.com/shared/static/{AGV_chr_URL}.gz', stream=True)
			response.raise_for_status()

			with BytesIO(response.content) as file:
				with gzip.GzipFile(fileobj=file) as gz_file:
					AGV_LDVs = pl.scan_csv(gz_file, separator='\t', has_header=True, low_memory=True)

					if input_rsID:
						filtered_AGV_LDVs = AGV_LDVs.filter(pl.col("LDV_rsID") == input_rsID)
					elif input_chr and input_pos:
						chr_int = int(input_chr)
						pos_int = int(input_pos)
						filtered_AGV_LDVs = AGV_LDVs.filter((pl.col("chr") == chr_int) & (pl.col("LDV_pos") == pos_int))
					else:
						return "Unexpected error with input validation.", {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, [], [], []

					sorted_AGV_LDVs = filtered_AGV_LDVs.sort("r2", descending=True).collect()
					del AGV_LDVs, filtered_AGV_LDVs

			if is_AGV:
				if sorted_AGV_LDVs.height > 0:
					message = (f"Variant {input_chr}:{input_pos} is an AGV and LD proxies were found. Both AGV summary results and LD proxies are displayed below." if input_chr and input_pos else f"Variant {input_rsID} is an AGV and LD proxies were found. Both AGV summary results and LD proxies are displayed below.")
					return (message, {'display': 'block'}, {'display': 'block'}, AGV_data, {'display': 'block'}, {'display': 'block'}, {'display': 'block'}, archaic_GTs, {'display': 'block'}, {'display': 'block'}, AFs_summary, all_GTs, sorted_AGV_LDVs.to_dicts())
				else:
					message = (f"Variant {input_chr}:{input_pos} is an AGV and summary results are displayed below. However, no LD proxies found." if input_chr and input_pos else f"Variant {input_rsID} is an AGV and summary results are displayed below. However, no LD proxies found.")
					return (message, {'display': 'block'}, {'display': 'block'}, AGV_data, {'display': 'block'}, {'display': 'block'}, {'display': 'block'}, archaic_GTs, {'display': 'block'}, {'display': 'block'}, AFs_summary, all_GTs, [])

			else:
				if sorted_AGV_LDVs.height > 0:
					message = (f"Variant {input_chr}:{input_pos} is not an AGV, but LD proxies were found and are displayed below." if input_chr and input_pos else f"Variant {input_rsID} is not an AGV, but LD proxies were found and are displayed below.")
					return (message, {'display': 'none'}, {'display': 'none'}, [], {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, [], {'display': 'none'}, {'display': 'none'}, [], [], sorted_AGV_LDVs.to_dicts())

		except Exception as e:
			return (f"An error occurred: {str(e)}", {'display': 'none'}, {'display': 'none'}, [], {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, [], {'display': 'none'}, {'display': 'block'}, [], [], [])

	else:
		return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

# === UTILS ===
def download_button_display(visible: bool) -> dict:
	return {
		'display': 'inline-block' if visible else 'none',
		'font-size': '16px',
		'margin-top': '20px',
		'textAlign': 'center',
		'width': '200px'
	}

# === CALLBACK: Show/hide download buttons ===
@app.callback(
	Output('download-AGVs-button', 'style'),
	Output('download-genotypes-button', 'style'),
	Input('AGVs_in_LD_table', 'data'),
	Input('AGV_allele_frequencies_table_results', 'data')
)

def toggle_download_buttons(ld_table_data, genotype_table_data):
	return download_button_display(bool(ld_table_data)), download_button_display(bool(genotype_table_data))

# === CALLBACK: Download AGV genotypes ===
@app.callback(
	Output('download-genotypes-csv', 'data'),
	Input('download-genotypes-button', 'n_clicks'),
	State('all_genotypes_store', 'data'),
	prevent_initial_call=True
)

def download_AGV_genotypes(n_clicks, genotype_data):
	if n_clicks and genotype_data:
		df = pl.DataFrame(genotype_data)
		return dcc.send_string(df.write_csv(), filename="AGV_genotypes.csv")
	return dash.no_update

# === CALLBACK: Download AGV Proxies ===
@app.callback(
	Output('download-AGVs-csv', 'data'),
	Input('download-AGVs-button', 'n_clicks'),
	State('AGVs_in_LD_table', 'data'),
	prevent_initial_call=True
)

def download_AGVs(n_clicks, AGVs_data):
	if n_clicks and AGVs_data:
		df = pl.DataFrame(AGVs_data)
		return dcc.send_string(df.write_csv(), filename="AGVs_in_LD.csv")
	return dash.no_update

# === FUNCTION: Process Chromosome ===
def process_chr(input_chr):
	if input_chr:
		if input_chr.lower().startswith('chr'):
			input_chr = input_chr[3:]

		if input_chr not in map(str, range(1, 23)) and input_chr != 'X':
			return None, f"Invalid chromosome: {input_chr}. Chromosome must be between 1-22 or X."

	return input_chr, None

# === FUNCTION: Process Variant ===
def load_AGVs():
	with gzip.open('files/AGVs_hg38.txt.gz', 'rt') as f:
		df = pl.read_csv(f, separator='\t', has_header=False, schema_overrides={'column_1': pl.Utf8})
	df.columns = ['chr', 'pos', 'rsID', 'ref', 'alt']
	return df

def lookup_AGV_by_chr_pos(df, chr, pos):
	pos_int = int(pos)
	filtered = df.filter((pl.col("chr") == chr) & (pl.col("pos") == pos_int))
	if filtered.height > 0:
		return filtered.row(0, named=True)
	return None

def lookup_AGV_by_rsID(df, rsID):
	filtered = df.filter(pl.col("rsID") == rsID)
	if filtered.height > 0:
		return filtered.row(0, named=True)
	return None

def lookup_chr_for_rsID_external(rsID):
	pickle_url = 'https://ucsf.box.com/shared/static/qlx2f1ncqgx7kug6kem3p93vbb4ljg8e.pkl'
	try:
		response = requests.get(pickle_url, stream=True)
		response.raise_for_status()
		with BytesIO(response.content) as compressed_file:
			with gzip.GzipFile(fileobj=compressed_file) as gz_file:
				rsID_chr_map = pickle.load(gz_file)
		return str(rsID_chr_map.get(rsID))
	except Exception as e:
		print(f"Error loading rsID to chr lookup: {e}")
		return None

def process_variant(input_chr=None, input_pos=None, input_rsID=None):
	df = load_AGVs()

	variant_chr = variant_pos = variant_rsID = variant_ref = variant_alt = None
	is_AGV = False

	if input_chr and input_pos:
		row = lookup_AGV_by_chr_pos(df, input_chr, input_pos)
		if row:
			variant_chr = row['chr']
			variant_pos = row['pos']
			variant_rsID = row['rsID']
			variant_ref = row['ref']
			variant_alt = row['alt']
			is_AGV = True
		else:
			variant_chr = input_chr
			variant_pos = input_pos

	elif input_rsID:
		row = lookup_AGV_by_rsID(df, input_rsID)
		if row:
			variant_chr = row['chr']
			variant_pos = row['pos']
			variant_rsID = row['rsID']
			variant_ref = row['ref']
			variant_alt = row['alt']
			is_AGV = True
		else:
			variant_chr = lookup_chr_for_rsID_external(input_rsID)
			variant_rsID = input_rsID

	return variant_chr, variant_pos, variant_rsID, variant_ref, variant_alt, is_AGV

# === FUNCTION: Retrieve Genotypes and Calculate Allele Frequencies ===
def retrieve_GTs_and_calculate_AFs(variant_chr, variant_rsID):
	try:
		with open('files/VCFs_Box_URLs.json', 'r') as VCFs_URLs:
			VCFs_URLs_dict = json.load(VCFs_URLs)
		VCFs_chr_URL = VCFs_URLs_dict.get(f'chr{variant_chr}')

		response = requests.get(f'https://ucsf.box.com/shared/static/{VCFs_chr_URL}.gz', stream=True)
		response.raise_for_status()

		with BytesIO(response.content) as file:
			with gzip.GzipFile(fileobj=file) as gz_file:
				sample_names = []
				GTs = None

				for raw_line in gz_file:
					line = raw_line.decode('utf-8').strip()
					if line.startswith("#CHROM"):
						header_fields = line.split("\t")
						sample_names = header_fields[9:]
					elif not line.startswith("#"):
						fields = line.split("\t")
						if fields[2] == variant_rsID:
							GTs = fields[9:]
							GTs_df = pl.DataFrame({
								'Genetic_ID': sample_names,
								'Genotype': GTs
							})
							break
					

		if GTs_df is not None:
			sample_annotation = pl.read_csv('files/AADR_sample_annotation_basic.txt.gz', separator='\t', has_header=True, low_memory=True)
			GTs_df = GTs_df.join(sample_annotation, on='Genetic_ID', how='left')
			del sample_annotation

			archaic_sample_ID_mapping = {"AltaiNeanderthal_snpAD.DG": "Altai", "Chagyrskaya_noUDG.SG": "Chagyrskaya", "Denisova3_snpAD.DG": "Denisovan", "Vindija_snpAD.DG": "Vindija"}
			archaic_GTs_dict = {}
			for row in GTs_df.iter_rows(named=True):
				archaic_name = archaic_sample_ID_mapping.get(row["Genetic_ID"])
				if archaic_name:
					archaic_GTs_dict[archaic_name] = row["Genotype"]

			filtered_GTs_df = GTs_df.filter(~pl.col("Location").str.contains("Denisova|Neanderthal|REF"))
			filtered_GTs_df = (filtered_GTs_df.with_columns((pl.col("Data_source") == "Shotgun.diploid").cast(pl.Int32()).alias("priority")).sort(["Specimen_ID", "priority"], descending=[False, True]).group_by("Specimen_ID").head(1))

			date_bins = [
				(0, 0, "Present"),
				(0, 1_000, "1000"),
				(1_000, 2_000, "2000"),
				(2_000, 3_000, "3000"),
				(3_000, 4_000, "4000"),
				(4_000, 5_000, "5000"),
				(5_000, 10_000, "10000"),
				(10_000, 15_000, "15000"),
				(15_000, 20_000, "20000"),
				(20_000, 30_000, "30000"),
				(30_000, 40_000, "40000"),
				(40_000, 50_000, "50000")
			]

			regions = ["Africa", "Americas", "East Asia", "Europe", "Oceania", "South Asia", "West Asia"]

			output = []

			for region in regions:
				row = {"Region": region}
				for lower, upper, label in date_bins:
					subset = filtered_GTs_df.filter(
						(pl.col('Region') == region) &
						((pl.col('Date_mean') <= upper) & (pl.col('Date_mean') > lower) if label != "Present" else (pl.col('Date_mean') == 0))
						)

					if subset.shape[0] == 0:
						row[label] = ""
						continue

					GT_counts = [GT for GT in subset["Genotype"].to_list() if GT != "./."]
					alt_count = sum(GT.count('1') for GT in GT_counts)
					total_alleles = 2 * len(GT_counts)
					AF = alt_count / total_alleles if total_alleles else None
					row[label] = f"{round(AF, 4) if AF is not None else ''} ({len(GT_counts)})"

				output.append(row)
			
			total_row = {"Region": "Total"}

			for lower, upper, label in date_bins:
				subset = filtered_GTs_df.filter(
					((pl.col('Date_mean') <= upper) & (pl.col('Date_mean') > lower) if label != "Present" else (pl.col('Date_mean') == 0))
				)

				if subset.shape[0] == 0:
					total_row[label] = ""
					continue

				AF, count = compute_AF(subset)
				total_row[label] = f"{round(AF, 4) if AF is not None else ''} ({count})"

			output.append(total_row)

			summary_AFs_df = pl.DataFrame(output)

			return archaic_GTs_dict, GTs_df, summary_AFs_df

		else:
			print(f"Variant with rsID {variant_rsID} not found.")

	except requests.exceptions.RequestException as e:
		print(f"Error fetching VCF file: {str(e)}")
	except Exception as e:
		print(f"Error processing VCF file: {str(e)}")

# === FUNCTION: Compute Allele Frequencies ===
def compute_AF(df):
	non_missing_GTs = df.filter(pl.col("Genotype") != "./.")
	if non_missing_GTs.height == 0:
		return None, 0

	alt_count = non_missing_GTs.select(
		pl.col('Genotype').str.count_matches('1').alias('alt_count')
	)['alt_count'].sum()

	total_alleles = 2 * non_missing_GTs.height
	AF = alt_count / total_alleles if total_alleles else None
	return AF, non_missing_GTs.height

if __name__ == "__main__":
	app.run(debug=False)