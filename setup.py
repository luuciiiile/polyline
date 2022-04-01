from cx_Freeze import setup, Executable

base = None

executables = [Executable("main.py", base=base)]
packages = ["idna"]
options = {
    'build.exe': dict(packages=packages),
}
setup(
    name='Polyline',
    options=options,
    version="1.0",
    description='simple python script who look for the .csv and create a directory with all the polylines of the csv',
    executables=executables
)
