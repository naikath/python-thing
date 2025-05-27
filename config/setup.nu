# source ./config/setup.nu

const proyect_root = path self ..
const script_name = 'new-script.py'
const path_script = $'($proyect_root)/src/($script_name)'
const exe_name = 'ComparadorDeArchivos'

const python_dependencies = [
	pandas
	python-pptx
	pyinstaller
	python-docx
	openpyxl
	customtkinter
]

def --env py-setup [] {
	use std "path add"
	const os_name = $nu.os-info.name

	if $os_name == "linux" {
		const path_venv = $'($proyect_root)/venv'
		const path_venv_bin = $'($proyect_root)/venv/bin'
		
		# create venv if doesn't exists
		if not ($path_venv | path exists) {
			print $'Creating Python venv'
			python3 -m venv $path_venv
			print $'Python venv created'
		}
		
		# add venv bin directory to the path
		if ($path_venv_bin not-in $env.PATH) {
			path add $path_venv_bin
			print $"Added to PATH:\n\"($path_venv_bin)\""
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
				print $"Added to PATH:\n\"($path)\""
			}
		}

	}
}

py-setup
hide py-setup

source ./git-aliases-source.nu

alias py = python

# Run the script
def py-run [] {
	cd $proyect_root
	py $path_script
}

# Install python required dependencies
def py-install-deps [] {
	cd $proyect_root
	pip install ...$python_dependencies
}

# Create python executable
def py-build-exe [] {
	cd $proyect_root
	pyinstaller --noconsole --onefile --name $exe_name $path_script
}
