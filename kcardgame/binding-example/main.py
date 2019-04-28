from Shiboken2QtExample import QObjectWithEnum

a = QObjectWithEnum()
a.someSignal.connect(lambda x: print("Signal emitted: %s" % x))
a.aSlot()
print("int(QObjectWithEnum.MyEnum.Values) =",
      int(QObjectWithEnum.MyEnum.Values))
a.nonSlotFunction(QObjectWithEnum.MyEnum.Some)
