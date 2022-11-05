Luminos
===========
# Installation

## Windows

1. Download Python 3.10 installer (https://www.python.org/downloads/release/python-3108/) [Windows installer at the bottom]
2. Run the setup (Ensure you've checked 'Add Python to PATH')
3. Ensure python has been installed correctly:
4. Press the windows key
5. Type 'cmd' and open a command line prompt
6. Type 'python' and press enter. It should display the python version.
7. Type exit() to quit python.
8. Type 'pip -V' to ensure pip has been installed correctly.
9. Type 'pip install virtualenv' to install the virtual environment package.
10. Open File Explorer and navigate to the luminos folder.
11. Select the address bar at the top and type 'cmd' and press enter to open a command line prompt in the luminos folder.
12. Type 'python3.10 -m venv env' to create a virtual environment for the project.
13. Type 'source env/bin/activate' to activate the virtual environment.
14. Type 'python3.10 -m pip install -e .' to install the project.
15. Launch the client with 'python3.10 client/client.py --ip <server_ip> --name <your_character_name>'