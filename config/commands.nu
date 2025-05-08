
def install-deps [] {
	const deps = [pandas python-pptx pyinstaller python-docx openpyxl]
	pip install ...$deps
}

def create-py-exe [] {
	const path_script = './src/pptx-comparador-gui.py'
	const name = 'ComparadorPPTX'
	pyinstaller --noconsole --onefile --name $name $path_script
}

def create-py-venv [] {
	python3 -m venv ./venv
}

def --env source-py-venv [] {
	use std "path add"
	path add './venv/bin'
}
