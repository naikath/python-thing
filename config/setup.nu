
const root_folder = 'C:\Users\liedr\Desktop\temp_thing'
const path_winpython = $'($root_folder)\Winpython64-3.13.2.0dot\WPy64-31320'
const path_python = $'($path_winpython)\python'
const path_pip = $'($path_winpython)\python\Scripts'
const path_git = $'($root_folder)\PortableGit\bin'

use std "path add"
path add $path_python
path add $path_pip
path add $path_git
