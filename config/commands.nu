
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
