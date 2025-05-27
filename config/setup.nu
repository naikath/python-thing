# source ./config/setup.nu
use std "path add"
const proyect_root = path self ..
const os_name = $nu.os-info.name

if $os_name == "linux" {
	const path_venv = $'($proyect_root)/venv'
	const path_venv_bin = $'($proyect_root)/venv/bin'
	
	# create venv if doesn't exists
	if not ($path_venv | path exists) {
		python3 -m venv $path_venv
		print $'python venv created'
	}
	
	# add venv bin directory to the path
	if ($path_venv_bin not-in $env.PATH) {
		path add $path_venv_bin
		print $'Added to PATH: "($path_venv_bin)"'
	}

} else if $os_name == "windows" {
	# root folder for local bins
	const path_local_bin = 'C:\Users\liedr\Desktop\temp_thing'
	# winpython
	const path_winpython = $'($path_local_bin)\Winpython64-3.13.2.0dot\WPy64-31320'
	const path_python = $'($path_winpython)\python'
	const path_pip = $'($path_winpython)\python\Scripts'
	# portable git
	const path_git = $'($path_local_bin)\PortableGit\bin'
	
	const paths = [
		$path_python
		$path_pip
		$path_git
	]

	# add each path if not already
	$paths | each {
		|path|
		if ($path not-in $env.PATH) {
			path add $path
			print $'Added to PATH: "($path)"'
		}
	}

}

source ./git-aliases-source.nu

alias py = python

# Install python required dependencies
def py-install-deps [] {
	const deps = [pandas python-pptx pyinstaller python-docx openpyxl customtkinter]
	pip install ...$deps
}

# Create python executable
def py-build-exe [] {
	const script_name = 'pptx-comparador-gui.py'
	const path_script = $'($proyect_root)/src/($script_name)'
	const exe_name = 'ComparadorPPTX'
	cd $proyect_root
	pyinstaller --noconsole --onefile --name $exe_name $path_script
}
