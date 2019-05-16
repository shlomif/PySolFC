#include "kcardgame.hpp"
MyKCardDeck::MyKCardDeck(QString theme_name)
{
    int argc = 1;
    char *argv[2] = {"pysol", NULL};
    app = new QGuiApplication(argc, argv);
    d = new KCardDeck(KCardTheme(theme_name), nullptr);
    unsigned int number = 0;
    QList<quint32> ids;
    for (int i = 0; i < 1; ++i)
        foreach (const KCardDeck::Rank &r, KCardDeck::standardRanks())
            foreach (const KCardDeck::Suit &s, KCardDeck::standardSuits())
                ids << KCardDeck::getId(s, r, number++);

    d->setDeckContents(ids);
    d->setCardWidth(150);
}
void MyKCardDeck::set_card_height(int i)
{
    d->setCardHeight(i);
}
void MyKCardDeck::set_card_width(int i)
{
    d->setCardWidth(i);
}

QPixmap *MyKCardDeck::get_card_pixmap(int i)
{
    auto ret = new QPixmap(d->cardPixmap(i, true));
    return ret;
};
