rem simple script for building windows package

cd ..
rm -rf dist
mkdir dist
cp -r locale dist
cp fc-solve.exe dist
cp smpeg.dll ogg.dll vorbis.dll vorbisfile.dll dist
python setup.py py2exe
cp -r d:\Python\tcl\tile0.7.8 dist\tcl
cp -r data\music dist\data
python scripts\create_iss.py
"d:\Program Files\Inno Setup 5\ISCC.exe" setup.iss
pause
