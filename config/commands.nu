
const proyect_root = path self ..

def py-install-deps [] {
	const deps = [pandas python-pptx pyinstaller python-docx openpyxl]
	pip install ...$deps
}

def py-build-exe [] {
	const path_script = $'($proyect_root)/src/pptx-comparador-gui.py'
	const name = 'ComparadorPPTX'
	pyinstaller --noconsole --onefile --name $name $path_script
}

def py-create-venv [] {
	python3 -m venv $'($proyect_root)/venv'
}

def --env py-source-venv [] {
	const path_python_venv = $'($proyect_root)/venv/bin'
	use std "path add"
	path add $path_python_venv
}
