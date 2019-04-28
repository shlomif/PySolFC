#pragma once
#include <QPixmap>
#include "KCardDeck"
#include "KCardTheme"
class KCardDeck_wrapper
{
    public:
    KCardDeck * d;
    KCardDeck_wrapper()
    {
    d = new KCardDeck( KCardTheme(), nullptr);
    }
QPixmap *get_card_pixmap(int i)
{
    auto ret = new QPixmap(d->cardPixmap(i, true));
    return ret;
}
};
