from PyQt5.QtCore import Qt


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

    def __init__(self, parent=None, flags=Qt.WindowFlags(), *args, **kwargs):
        self.__ensure_pre_init_call = False
        self.__pre_init__(*args, **kwargs)
        assert self.__ensure_pre_init_call, \
            'Need to call super in overridden __pre_init__ method'

        super().__init__(parent, flags)

        self.__ensure_pre_setup_call = False
        self.__pre_setup__(*args, **kwargs)
        assert self.__ensure_pre_init_call, \
            'Need to call super in overridden __pre_setup__ method'

        self.setupUi(self)
        self.retranslateUi(self)

        self.__ensure_post_init_call = False
        self.__post_init__(*args, **kwargs)
        assert self.__ensure_post_init_call, \
            'Need to call super in overridden __post_init__ method'

    def __pre_init__(self, *args, **kwargs):
        self.__ensure_pre_init_call = True

    def __pre_setup__(self, *args, **kwargs):
        """Initialize qt objects as attributes, self may be passed as parent."""
        self.__ensure_pre_setup_call = True

    def setupUi(self, uiObj):
        pass

    def retranslateUi(self, uiObj):
        pass

    def __post_init__(self, *args, **kwargs):
        """Connect signals, create advanced objects that use element from ui."""
        self.__ensure_post_init_call = True
