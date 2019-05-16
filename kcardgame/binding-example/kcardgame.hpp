#pragma once
#include <QPixmap>
#include <QObject>
#include <QGuiApplication>
#include "KCardDeck"
#include "KCardTheme"
class Q_DECL_EXPORT MyKCardDeck : public QObject
{
    Q_OBJECT
  public:
    QGuiApplication *app;
    KCardDeck *d;
    explicit MyKCardDeck(QString);
  public slots:
    Q_DECL_EXPORT QPixmap *get_card_pixmap(int i);
    Q_DECL_EXPORT void set_card_height(int i);
    Q_DECL_EXPORT void set_card_width(int i);
};
