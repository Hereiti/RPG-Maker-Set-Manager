#!/usr/bin/env python
import os
from PyInstaller.__main__ import run

# I won't go into much details about this file.
# This will compile the whole code into an executable file.
# Don't modify unless you know what you are doing.
# Also make sure that you have all files.
#
# You can contact me via discord if you need any help
# Discord: hereiti
# or via mail at: costantinhereiti.jeu@gmail.com

if __name__ == '__main__':
	options = [
		'--onefile',
		'--noconsole',
		f'--add-data={os.path.abspath("./res")};.\\res',
		f'--add-data={os.path.abspath("./requirements.txt")};.',
		f'--add-data={os.path.abspath("./changelog.md")};.',
		f'--add-data={os.path.abspath("./license.md)};.',
		f'--add-data={os.path.abspath("./.env")};.',
		'--name=RPG Maker - Set Manager',
		os.path.abspath('./src/main.py')
	]

	run(options)