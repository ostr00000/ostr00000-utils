class BaseWidget:
    """This class call setupUi and retranslateUi method.
     These method are generated from qt ui forms.

     Example:

         class MyWidget(UI_MyWidget, BaseWidget, QWidget):
            def __pre_setup__(self, *args, **kwargs):
                super().__pre_setup__(*args, **kwargs):
                self.specialWidget = SpecialWidget(self)

            def __post_init__(self, *args, **kwargs):
                super().__post_init__(*args, **kwargs):
                self.specialWidget.triggered.connect(self.onSpecialWidgetTriggered)

            ...

    """

    def __init__(self, parent=None, *args, **kwargs):
        self.__forceSuperCall(self.__pre_init__, *args, **kwargs)
        super().__init__(parent)
        self.__forceSuperCall(self.__pre_setup__, *args, **kwargs)
        self.setupUi(self)
        self.retranslateUi(self)
        self.__forceSuperCall(self.__post_init__, *args, **kwargs)

    def __forceSuperCall(self, method, *args, **kwargs):
        method(*args, **kwargs)
        assert getattr(self, method.__name__ + 'executed__', False), \
            f'Need to call super().{method.__name__}(*args, **kwargs)\n' \
            f'in overridden method: "{method.__name__}" ' \
            f'in class: "{type(self).__qualname__}"'

    def __pre_init__(self, *args, **kwargs):
        self.__pre_init__executed__ = True

    def __pre_setup__(self, *args, **kwargs):
        """Initialize qt objects as attributes, self may be passed as parent."""
        self.__pre_setup__executed__ = True

    def setupUi(self, uiObj):
        pass

    def retranslateUi(self, uiObj):
        pass

    def __post_init__(self, *args, **kwargs):
        """Connect signals, create advanced objects that use element from ui."""
        self.__post_init__executed__ = True
