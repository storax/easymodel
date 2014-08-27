from PySide import QtCore, QtGui


class WidgetDelegate(QtGui.QStyledItemDelegate):
    """A delegate for drawing a arbitrary QWidget

    When subclassing, reimplement set_widget_index, create_widget, createEditor, setEditorData, setModelData
    to your liking.
    Make sure that the model returns the ItemIsEditable flag!
    """

    def __init__(self, parent=None):
        """Create a new abstract widget delegate that draws the given widget.

        This delegate only works ListViews that are not in IconMode. Maybe also in other views.

        :param widget: the widget to draw. If None, it behaves like a :class:`QtGui.QStyledItemDelegate`
        :type widget: :class:`QtGui.QWidget` | None
        :param parent: the parent object
        :type parent: :class:`QtCore.QObject`
        :raises: None
        """
        super(WidgetDelegate, self).__init__(parent)
        self._widget = self.create_widget()

    @property
    def widget(self):
        """Return the widget that is used by the delegate for drawing

        :returns: widget
        :rtype: :class:`QtGui.QWidget`
        :raises: None
        """
        return self._widget

    @widget.setter
    def widget(self, widget):
        """Set the widget

        :param widget: The widget to set
        :type widget: :class:`QtGui.QWidget`
        :raises: None
        """
        if self._widget:
            self._lay.removeWidget(self._widget)
        self._widget = widget
        if widget:
            self._lay.insertWidget(0, widget)

    def paint(self, painter, option, index):
        """Use the painter and style option to render the item specified by the item index.

        :param painter: the painter to paint
        :type painter: :class:`QtGui.QPainter`
        :param option: the options for painting
        :type option: :class:`QtGui.QStyleOptionViewItem`
        :param index: the index to paint
        :type index: :class:`QtCore.QModelIndex`
        :returns: None
        :rtype: None
        :raises: None
        """
        if self._widget is None:
            return super(WidgetDelegate, self).paint(painter, option, index)

        self.set_widget_index(index)
        painter.save()
        painter.translate(option.rect.topLeft())
        self._widget.resize(option.rect.size())
        self._widget.render(painter, QtCore.QPoint())
        painter.restore()

    def sizeHint(self, option, index):
        """Return the appropriate amount for the size of the widget

        The widget will always be expanded to at least the size of the viewport.

        :param option: the options for painting
        :type option: :class:`QtGui.QStyleOptionViewItem`
        :param index: the index to paint
        :type index: :class:`QtCore.QModelIndex`
        :returns: None
        :rtype: None
        :raises: None
        """
        if self._widget is None:
            return super(WidgetDelegate, self).sizeHint(option, index)

        self.set_widget_index(index)
        self._widget.resize(option.rect.size())
        sh = self._widget.sizeHint()
        return sh

    def set_widget_index(self, index):
        """Set the index for the widget. The widget should retrieve data from the index and display it.

        You might want use the same function as for :meth:`WidgetDelegate.setEditorData`.

        :param index: the index to paint
        :type index: :class:`QtCore.QModelIndex`
        :returns: None
        :rtype: None
        :raises: None
        """
        pass

    def create_widget(self, parent=None):
        """Return a widget that should get painted by the delegate

        You might want to use this in :meth:`WidgetDelegate.createEditor`

        :param parent: the parent widget
        :type parent: :class:`QtGui.QWidget` | None
        :returns: The created widget | None
        :rtype: :class:`QtGui.QWidget` | None
        :raises: None
        """
        return None

    def commit_close_editor(self, editor, endedithint=QtGui.QAbstractItemDelegate.NoHint):
        """Commit and close the editor

        Call this method whenever the user finished editing.

        :param editor: The editor to close
        :type editor: :class:`QtGui.QWidget`
        :param endedithint: Hints that the delegate can give the model and view to make editing data comfortable for the user
        :type endedithint: :data:`QtGui.QAbstractItemDelegate.EndEditHint`
        :returns: None
        :rtype: None
        :raises: None
        """
        self.commitData.emit(editor)
        self.closeEditor.emit(editor, endedithint)
