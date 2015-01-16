"""Module for having arbitrary widgets in views.

Delegate
--------

The :class:`WidgetDelegate` enables an easy way to put arbitrary widgets in views.
This is done by rendering the widget in the cells of the view. Ones the user edits the item,
the delegate will give him an editor widget. Combined with the special views below, this
will almost feel like real widgets. So if your widget has buttons, and you click on them,
the click actually gets propagated to the widget.

Views
-----

To make the widget delegates in the views behave like real widgets, we have to propagate click
events. A user might see a button in a view and will try to click it. This will
edit the item, so the delegate will give us a real editor widget and the click will be propagated
to given widget.
Mouse hovering etc is not supported at the moment and probably not good for performance.

You can either use the :class:`WidgetDelegateViewMixin` for your own views or use one
of the premade views: :class:`WD_AbstractItemView`, :class:`WD_ListView`, :class:`WD_TableView`
:class:`WD_TreeView`.
"""
from functools import partial

from PySide import QtCore, QtGui


class WidgetDelegate(QtGui.QStyledItemDelegate):
    """A delegate for drawing a arbitrary QWidget

    When subclassing, reimplement:

       * :meth:`WidgetDelegate.set_widget_index`
       * :meth:`WidgetDelegate.create_widget`
       * :meth:`WidgetDelegate.create_editor_widget`
       * :meth:`WidgetDelegate.setEditorData`
       * :meth:`WidgetDelegate.setModelData`

    .. Note:: Make sure that the model returns the ItemIsEditable flag!

    I recommend using one of the views in this module, because they issue click events, when
    an index is clicked.

    .. Note: If a section is small, the widget will get rendered partially,
             because it always has the minimum size of the size hint.
             The editor might look different, because he will get resized to the section width.
             To prevent that, set :data:`WidgetDelegate.keep_editor_size` to True.
             But then i would recommend to keep your sections in the view at least
             as big as the size hint. See :meth:`QtGui.HeaderView.resizeMode`.
    """

    def __init__(self, parent=None):
        """Create a new abstract widget delegate that draws the given widget.

        :param widget: the widget to draw. If None,
                       it behaves like a :class:`QtGui.QStyledItemDelegate`
        :type widget: :class:`QtGui.QWidget` | None
        :param parent: the parent object
        :type parent: :class:`QtCore.QObject`
        :raises: None
        """
        super(WidgetDelegate, self).__init__(parent)
        self._widget = self.create_widget(parent)
        self._widget.setVisible(False)
        self._widget.setAutoFillBackground(True)
        self._edit_widgets = {}
        self.keep_editor_size = True
        """If True, resize the editor at least to its size Hint size,
        or if the section allows is, bigger."""

    @property
    def widget(self):
        """Return the widget that is used by the delegate for drawing

        :returns: widget
        :rtype: :class:`QtGui.QWidget`
        :raises: None
        """
        return self._widget

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
        """Set the index for the widget. The widget should retrieve data from the index
        and display it.

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

        You might want to use this in :meth:`WidgetDelegate.create_editor_widget`

        :param parent: the parent widget
        :type parent: :class:`QtGui.QWidget` | None
        :returns: The created widget | None
        :rtype: :class:`QtGui.QWidget` | None
        :raises: None
        """
        return None

    def close_editors(self, ):
        """Close all current editors

        :returns: None
        :rtype: None
        :raises: None
        """
        for k in reversed(self._edit_widgets.keys()):
            self.commit_close_editor(k)

    def createEditor(self, parent, option, index):
        """Return the editor to be used for editing the data item with the given index.

        Note that the index contains information about the model being used.
        The editor's parent widget is specified by parent, and the item options by option.

        This will set auto fill background to True on the editor, because else, you would see
        The rendered delegate below.

        :param parent: the parent widget
        :type parent: QtGui.QWidget
        :param option: the options for painting
        :type option: QtGui.QStyleOptionViewItem
        :param index: the index to paint
        :type index: QtCore.QModelIndex
        :returns: The created widget | None
        :rtype: :class:`QtGui.QWidget` | None
        :raises: None
        """
        # close all editors
        self.close_editors()
        e = self.create_editor_widget(parent, option, index)
        if e:
            self._edit_widgets[index] = e
            e.setAutoFillBackground(True)
            e.destroyed.connect(partial(self.editor_destroyed, index=index))
        return e

    def create_editor_widget(self, parent, option, index):
        """Return a editor widget for the given index.

        :param parent: the parent widget
        :type parent: QtGui.QWidget
        :param option: the options for painting
        :type option: QtGui.QStyleOptionViewItem
        :param index: the index to paint
        :type index: QtCore.QModelIndex
        :returns: The created widget | None
        :rtype: :class:`QtGui.QWidget` | None
        :raises: None
        """
        return None

    def commit_close_editor(self, index, endedithint=QtGui.QAbstractItemDelegate.NoHint):
        """Commit and close the editor

        Call this method whenever the user finished editing.

        :param index: The index of the editor
        :type index: :class:`QtCore.QModelIndex`
        :param endedithint: Hints that the delegate can give the model
                            and view to make editing data comfortable for the user
        :type endedithint: :data:`QtGui.QAbstractItemDelegate.EndEditHint`
        :returns: None
        :rtype: None
        :raises: None
        """
        editor = self._edit_widgets[index]
        self.commitData.emit(editor)
        self.closeEditor.emit(editor, endedithint)
        del self._edit_widgets[index]

    def edit_widget(self, index):
        """Return the current edit widget at the givent index if there is one

        :param index: The index of the editor
        :type index: :class:`QtCore.QModelIndex`
        :returns: The editor widget | None
        :rtype: :class:`QtGui.QWidget` | None
        :raises: None
        """
        return self._edit_widgets.get(index)

    def editor_destroyed(self, index=None, *args):
        """Callback for when the editor widget gets destroyed. Set edit_widget to None.

        :returns: None
        :rtype: None
        :raises: None
        """
        if index:
            try:
                del self._edit_widgets[index]
            except KeyError:
                pass

    def updateEditorGeometry(self, editor, option, index):
        """Make sure the editor is the same size as the widget

        By default it can get smaller because does not expand over viewport size.
        This will make sure it will resize to the same size as the widget.

        :param editor: the editor to update
        :type editor: :class:`QtGui.QWidget`
        :param option: the options for painting
        :type option: QtGui.QStyleOptionViewItem
        :param index: the index to paint
        :type index: QtCore.QModelIndex
        :returns: None
        :rtype: None
        :raises: None
        """
        super(WidgetDelegate, self).updateEditorGeometry(editor, option, index)
        editor.setGeometry(option.rect)
        if self.keep_editor_size:
            esh = editor.sizeHint()
            osh = option.rect.size()
            w = osh.width() if osh.width() > esh.width() else esh.width()
            h = osh.height() if osh.height() > esh.height() else esh.height()
            editor.resize(w, h)


class WidgetDelegateViewMixin(object):
    """Mixin for views to allow editing with mouseclicks,
    if there is a widgetdelegate.

    On a mouse click event, try to edit the index at click position.
    Then take the editor widget and issue the same click on that widget.
    """
    def __init__(self, *args, **kwargs):
        super(WidgetDelegateViewMixin, self).__init__(*args, **kwargs)
        self.__recursing = False  # check if we are recursing if posting a click event

    def index_at_event(self, event):
        """Get the index under the position of the given MouseEvent

        :param event: the mouse event
        :type event: :class:`QtGui.QMouseEvent`
        :returns: the index
        :rtype: :class:`QtCore.QModelIndex`
        :raises: None
        """
        # find index at mouse position
        globalpos = event.globalPos()
        viewport = self.viewport()
        pos = viewport.mapFromGlobal(globalpos)
        return self.indexAt(pos)

    def get_pos_in_delegate(self, index, globalpos):
        """Map the global position to the position relative to the
        given index

        :param index: the index to map to
        :type index: :class:`QtCore.QModelIndex`
        :param globalpos: the global position
        :type globalpos: :class:`QtCore.QPoint`
        :returns: The position relative to the given index
        :rtype: :class:`QtCore.QPoint`
        :raises: None
        """
        rect = self.visualRect(index)  # rect of the index
        p = self.viewport().mapToGlobal(rect.topLeft())
        return globalpos - p

    def propagate_event_to_delegate(self, event, eventhandler):
        """Propagate the given Mouse event to the widgetdelegate

        Enter edit mode, get the editor widget and issue an event on that widget.

        :param event: the mouse event
        :type event: :class:`QtGui.QMouseEvent`
        :param eventhandler: the eventhandler to use. E.g. ``"mousePressEvent"``
        :type eventhandler: str
        :returns: None
        :rtype: None
        :raises: None
        """
        # find index at mouse position
        i = self.index_at_event(event)

        # if the index is not valid, we don't care
        # handle it the default way
        if not i.isValid():
            return getattr(super(WidgetDelegateViewMixin, self), eventhandler)(event)
        # get the widget delegate. if there is None, handle it the default way
        delegate = self.itemDelegate(i)
        if not isinstance(delegate, WidgetDelegate):
            return getattr(super(WidgetDelegateViewMixin, self), eventhandler)(event)

        # see if there is already a editor
        widget = delegate.edit_widget(i)
        if not widget:
            # close all editors, then start editing
            delegate.close_editors()
            # Force editing. If in editing state, view will refuse editing.
            if self.state() == self.EditingState:
                self.setState(self.NoState)
            self.edit(i)
            # get the editor widget. if there is None, there is nothing to do so return
            widget = delegate.edit_widget(i)
        if not widget:
            return getattr(super(WidgetDelegateViewMixin, self), eventhandler)(event)

        # try to find the relative position to the widget
        pid = self.get_pos_in_delegate(i, event.globalPos())
        widgetatpos = widget.childAt(pid)
        if widgetatpos:
            widgettoclick = widgetatpos
            g = widget.mapToGlobal(pid)
            clickpos = widgettoclick.mapFromGlobal(g)
        else:
            widgettoclick = widget
            clickpos = pid

        # create a new event for the editor widget.
        e = QtGui.QMouseEvent(event.type(),
                              clickpos,
                              event.button(),
                              event.buttons(),
                              event.modifiers())
        # before we send, make sure, we cannot recurse
        self.__recursing = True
        try:
            r = QtGui.QApplication.sendEvent(widgettoclick, e)
        finally:
            self.__recursing = False  # out of the recursion. now we can accept click events again
        return r

    def mouseDoubleClickEvent(self, event):
        """If a widgetdelegate is double clicked,
        enter edit mode and propagate the event to the editor widget.

        :param event: the mouse event
        :type event: :class:`QtGui.QMouseEvent`
        :returns: None
        :rtype: None
        :raises: None
        """
        return self.propagate_event_to_delegate(event, "mouseDoubleClickEvent")

    def mousePressEvent(self, event):
        """If the mouse is presses on a widgetdelegate,
        enter edit mode and propagate the event to the editor widget.

        :param event: the mouse event
        :type event: :class:`QtGui.QMouseEvent`
        :returns: None
        :rtype: None
        :raises: None
        """
        return self.propagate_event_to_delegate(event, "mousePressEvent")

    def mouseReleaseEvent(self, event):
        """If the mouse is released on a widgetdelegate,
        enter edit mode and propagate the event to the editor widget.

        :param event: the mouse event
        :type event: :class:`QtGui.QMouseEvent`
        :returns: None
        :rtype: None
        :raises: None
        """
        return self.propagate_event_to_delegate(event, "mouseReleaseEvent")


class WD_AbstractItemView(WidgetDelegateViewMixin, QtGui.QAbstractItemView):
    """A abstract item view that that when clicked, tries to issue
    a left click to the widget delegate.
    """
    pass


class WD_ListView(WidgetDelegateViewMixin, QtGui.QListView):
    """A list view that that when clicked, tries to issue
    a left click to the widget delegate.
    """
    pass


class WD_TableView(WidgetDelegateViewMixin, QtGui.QTableView):
    """A table view that that when clicked, tries to issue
    a left click to the widget delegate.
    """
    pass


class WD_TreeView(WidgetDelegateViewMixin, QtGui.QTreeView):
    """A tree view that that when clicked, tries to issue
    a left click to the widget delegate.

    By default the resize mode of the header will resize to contents.
    """

    def __init__(self, *args, **kwargs):
        """Initialize a new treeview

        :raises: None
        """
        super(WD_TreeView, self).__init__(*args, **kwargs)
        self.header().setResizeMode(self.header().ResizeToContents)

    def get_total_indentation(self, index):
        """Get the indentation for the given index

        :param index: the index to query
        :type index: :class:`QtCore.ModelIndex`
        :returns: the number of parents
        :rtype: int
        :raises: None
        """
        n = 0
        while index.isValid():
            n += 1
            index = index.parent()
        return n * self.indentation()

    def index_at_event(self, event):
        """Get the index under the position of the given MouseEvent

        This implementation takes the indentation into account.

        :param event: the mouse event
        :type event: :class:`QtGui.QMouseEvent`
        :returns: the index
        :rtype: :class:`QtCore.QModelIndex`
        :raises: None
        """
        # find index at mouse position
        globalpos = event.globalPos()
        viewport = self.viewport()
        pos = viewport.mapFromGlobal(globalpos)
        i = self.indexAt(pos)
        n = self.get_total_indentation(i)
        if pos.x() > n:
            return i
        else:
            return QtCore.QModelIndex()
