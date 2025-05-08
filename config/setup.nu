
use std "path add"
const proyect_root = path self ..

if ($nu.os-info | get name) == "linux" {
	# for linux
	const path_venv = $'($proyect_root)/venv'
	const path_venv_bin = $'($proyect_root)/venv/bin'
	
	# create venv if doesn't exists
	if not ($path_venv | path exists) {
		python3 -m venv $path_venv
	}
	
	# add venv bin directory to the path
	if ($path_venv_bin not-in $env.PATH) {
		path add $path_venv_bin
	}

} else {
	# for windows

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
		}
	}
}

source ./git-aliases-source.nu

source ./commands.nu
