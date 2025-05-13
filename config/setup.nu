
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

	path add $path_python
	path add $path_pip
	path add $path_git

}

source ./git-aliases-source.nu

source ./commands.nu
