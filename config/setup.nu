
use std "path add"
const proyect_root = path self ..
const os_name = $nu.os-info.name

if $os_name == "windows" {
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
