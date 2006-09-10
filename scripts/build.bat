rem simple script for building windows package

cd ..
rm -rf dist
mkdir dist
cp -r locale dist
cp fc-solve.exe dist
cp smpeg.dll ogg.dll vorbis.dll vorbisfile.dll dist
python setup.py py2exe
cp -r data\music dist\data
rem rm -rf dist\tcl\tcl8.4\encoding
rem rm -rf dist\tcl\tk8.4\demos dist\tcl\tk8.4\images
python scripts\create_iss.py
"d:\Program Files\Inno Setup 5\ISCC.exe" setup.iss
pause
