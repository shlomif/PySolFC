#pragma once
#include <QObject>

class QObjectWithEnum : public QObject
{
    Q_OBJECT
public:

    enum class MyEnum {
        Some,
        Values,
        For,
        The,
        Enum,
    };
    Q_ENUM(MyEnum)

    explicit QObjectWithEnum(QObject *parent = nullptr);

    QString nonSlotFunction(const MyEnum value) const;


signals:
    void someSignal(QString stringArg);

public slots:
    void aSlot();
};
