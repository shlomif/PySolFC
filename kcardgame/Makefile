# ---- Link ---------------------------
kcardgame.so: kcardgame.o Makefile
	gcc -shared -o kcardgame.so  kcardgame.o `pkg-config --libs python3`

# ---- gcc C compile ------------------
kcardgame.o:  kcardgame.cpp kcardgame.hpp Makefile
	gcc `pkg-config --cflags Qt5Gui` -I build-kpat/libkcardgame/ -I kpat/libkcardgame/include -I kpat/libkcardgame/ -g -fPIC -c kcardgame.cpp -I /usr/include/python3.7m/ -I /usr/lib64/python3.7/site-packages/numpy/core/include/numpy
