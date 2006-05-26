rem simple script for building windows package

cd ..
rm -rf dist
mkdir dist
cp -r locale dist
cp freecell-solver\freecell-solver-2.8.6-bin\fc-solve.exe dist
python setup.py py2exe
python scripts\create_iss.py
"d:\Program Files\Inno Setup 5\ISCC.exe" setup.iss
pause
