/* A file to test imorting C modules for handling arrays to Python */

#include "kcardgame.hpp"
MyKCardDeck::MyKCardDeck()
    {
        int argc = 1;
        char * argv[2]={"pysol",NULL};
        app = new QGuiApplication(argc, argv);
    d = new KCardDeck( KCardTheme(), nullptr);
    }
QPixmap *MyKCardDeck::get_card_pixmap(int i)
{
    auto ret = new QPixmap(d->cardPixmap(i, true));
    return ret;
};
