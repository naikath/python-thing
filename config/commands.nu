
def py-install-deps [] {
	const deps = [pandas python-pptx pyinstaller python-docx openpyxl]
	pip install ...$deps
}

def py-build-exe [] {
	const path_script = './src/pptx-comparador-gui.py'
	const name = 'ComparadorPPTX'
	pyinstaller --noconsole --onefile --name $name $path_script
}

def py-create-venv [] {
	python3 -m venv ./venv
}

def --env py-source-venv [] {
	use std "path add"
	path add './venv/bin'
}
