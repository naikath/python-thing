
const proyect_root = path self ..

def install-deps [] {
	const deps = [pandas python-pptx pyinstaller python-docx openpyxl]
	pip install ...$deps
}

def create-py-exe [] {
	const path_script = $'($proyect_root)/src/pptx-comparador-gui.py'
	const name = 'ComparadorPPTX'
	pyinstaller --noconsole --onefile --name $name $path_script
}

def create-py-venv [] {
	python3 -m venv $'($proyect_root)/venv'
}

def --env source-py-venv [] {
	const path_python_venv = $'($proyect_root)/venv/bin'
	use std "path add"
	path add $path_python_venv
}
