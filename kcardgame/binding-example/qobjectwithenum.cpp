#include "qobjectwithenum.h"

#include <QDebug>
#include <QMetaEnum>

QObjectWithEnum::QObjectWithEnum(QObject *parent) : QObject(parent)
{
}

QString QObjectWithEnum::nonSlotFunction(const QObjectWithEnum::MyEnum value) const {
    const auto ret = metaObject()->enumerator(0).valueToKey(int(value));
    qDebug() << __FUNCTION__ << "returning:" << ret;
    return ret;
}

void QObjectWithEnum::aSlot() {
    qDebug() << __FUNCTION__ << "slot called";
    emit someSignal("from aSlot");
}
