"""This module provides a generic interface for tree models

It centers around the TreeModel, which is used for all kinds of trees.
The tree gets customized by the TreeItems. Each TreeItem holds
a specific ItemData subclass. The ItemData is responsible for
delivering the data. Make sure that all TreeItems in one hierarchy have the same ItemData subclasses or at least the same column_count.
If not, make sure the data method can handle columns outside their column count.
If you want to create a tree, create the needed itemdata classes,
create a root tree item that is parent for all top-level items.
The root item does not have to provide data, so the data might be None.
It is advides to use :class:`jukebox.core.gui.treemodel.ListItemData` because the data in the list
will be used for the headers.
Then create the tree items with their appropriate data instances.
Finally create a tree model instance with the root tree item.
"""

import abc

from PySide import QtCore


class ItemData(object):  # pragma: no cover
    """An abstract class that holds data and is used as an interface for TreeItems

    When subclassing implement :meth:`ItemData.data` and :meth:`ItemData.column_count`.
    It is advised to reimplement :meth:`ItemData.internal_data` too.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def data(self, column, role):
        """Return the data for the specified column and role

        The column addresses one attribute of the data.
        When used in a root item, the data should return the horizontal header
        data. When returning None, the section Number is used (starting at 1) by the treemodel.
        So if you want an empty header, return an empty string!

        :param column: the data column
        :type column: int
        :param role: the data role
        :type role: QtCore.Qt.ItemDataRole
        :returns: data depending on the role
        :rtype:
        :raises: None
        """
        pass

    @abc.abstractmethod
    def column_count(self, ):
        """Return the number of columns that can be queried for data

        :returns: the number of columns
        :rtype: int
        :raises: None
        """
        pass

    def internal_data(self, ):
        """Return the internal data of the ItemData

        E.g. a ListItemData could return the list it uses, a
        ProjectItemData could return the Project etc.

        :returns: the data the itemdata uses as information
        :rtype: None|arbitrary data
        :raises: None
        """
        return None

    def flags(self, ):
        """Return the item flags for the item

        Default is QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

        :returns: the item flags
        :rtype: QtCore.Qt.ItemFlags
        :raises: None
        """
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable


class ListItemData(ItemData):
    """Item data for generic lists

    Initialize it with a list of objects. Each element corresponds to a column.
    For DisplayRole the objects are converted to strings with ``str()``.
    """

    def __init__(self, liste):
        """ Constructs a new StringItemData with the given list

        :param list: a list of objects, one for each column
        :type list: list of objects
        :raises: None
        """
        super(ListItemData, self).__init__()
        self._list = liste

    def data(self, column, role):
        """Return the data for the specified column and role

        For DisplayRole the element in the list will be converted to a sting and returned.

        :param column: the data column
        :type column: int
        :param role: the data role
        :type role: QtCore.Qt.ItemDataRole
        :returns: data depending on the role, or None if the column is out of range
        :rtype: depending on the role or None
        :raises: None
        """
        if role == QtCore.Qt.DisplayRole:
            if column >= 0 and column < len(self._list):
                return str(self._list[column])

    def column_count(self, ):
        """Return the number of columns that can be queried for data

        :returns: the number of columns
        :rtype: int
        :raises: None
        """
        return len(self._list)

    def internal_data(self, ):
        """Return the list

        :returns: the internal list
        :rtype: :class:`list`
        :raises: None
        """
        return self._list


class TreeItem(object):
    """General TreeItem

    You can represent a tree structure with these tree items. Each item
    should contain some data that it can give to the model.
    Note that each tree always has one root item.
    Even if you have multiple top level items, they are all grouped under one
    root. The data for the root item can be None but it is advised to use
    a ListItemData so you can provide horizontal headers.
    """

    def __init__(self, data, parent=None):
        """Constructs a new TreeItem that holds some data and might be parented under parent

        :param data: the data item. if the tree item is the root, the data will be used for horizontal headers!
                     It is recommended to use :class:`jukebox.core.gui.treeitem.ListItemData` in that case.
        :type data: :class:`jukebox.core.gui.treemodel.ItemData`
        :param parent: the parent treeitem
        :type parent: :class:`jukebox.core.gui.treemodel.TreeItem`
        :raises: None
        """
        self._data = data
        self._parent = parent
        if self._parent is not None:
            self._parent.childItems.append(self)
        self.childItems = []

    def child(self, row):
        """Return the child at the specified row

        :param row: the row number
        :type row: int
        :returns: the child
        :rtype: :class:`jukebox.core.gui.treemodel.TreeItem`
        :raises: IndexError
        """
        return self.childItems[row]

    def child_count(self, ):
        """Return the number of children

        :returns: child coun
        :rtype: int
        :raises: None
        """
        return len(self.childItems)

    def row(self, ):
        """Return the index of this tree item in the parent rows

        :returns: the row of this TreeItem in the parent
        :rtype: int
        :raises: None
        """
        if self._parent is None:
            return 0
        return self._parent.childItems.index(self)

    def column_count(self, ):
        """Return the number of columns that the children have

        :returns: the column count of the children data
        :rtype: int
        :raises: None
        """
        if self.child_count():
            return self.childItems[0]._data.column_count()
        else:
            return 0

    def data(self, column, role):
        """Return the data for the column and role

        :param column: the data column
        :type column: int
        :param role: the data role
        :type role: QtCore.Qt.ItemDataRole
        :returns: data depending on the role
        :rtype:
        :raises: None
        """
        if self._data is not None and (column >= 0 or column < self._data.column_count()):
            return self._data.data(column, role)

    def parent(self, ):
        """Return the parent tree item

        :returns: the parent or None if there is no parent
        :rtype: :class:`jukebox.core.gui.treemodel.TreeItem`
        :raises: None
        """
        return self._parent

    def itemdata(self, ):
        """Return the internal :class:`ItemData`

        :returns: the internal ItemData
        :rtype: :class:`ItemData`
        :raises: None
        """
        return self._data

    def internal_data(self, ):
        """Return the internal data of the item data

        E.g. a ListItemData could return the list it uses, a
        ProjectItemData could return the Project etc.

        :returns: the data the itemdata uses as information
        :rtype: None|arbitrary data
        :raises: None
        """
        return self._data.internal_data()

    def flags(self, ):
        """Return the flags for the item

        :returns: the flags
        :rtype: QtCore.Qt.ItemFlags
        :raises: None
        """
        return self._data.flags()


class TreeModel(QtCore.QAbstractItemModel):
    """A tree model that uses the :class:`jukebox.core.gui.treemodel.TreeItem` to represent a general tree.

    """

    def __init__(self, root, parent=None):
        """Constructs a new tree model with the given root treeitem

        :param root:
        :type root:
        :param parent:
        :type parent:
        :raises: None
        """
        super(TreeModel, self).__init__(parent)
        self._root = root

    def index(self, row, column, parent=None):
        """Returns the index of the item in the model specified by the given row, column and parent index.

        :param row: the row of the item
        :type row: int
        :param column: the column for the item
        :type column: int
        :param parent: the parent index
        :type parent: :class:`QtCore.QModelIndex`:
        :returns: the index of the item
        :rtype: :class:`QtCore.QModelIndex`
        :raises: None
        """
        if parent is None:
            parent = QtCore.QModelIndex()
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        if parent.isValid():
            parentItem = parent.internalPointer()
        else:
            parentItem = self._root

        try:
            childItem = parentItem.child(row)
            return self.createIndex(row, column, childItem)
        except IndexError:
            return QtCore.QModelIndex()

    def parent(self, index):
        """Returns the parent of the model item with the given index. If the item has no parent, an invalid QModelIndex is returned.

        :param index: the index that you want to know the parent of
        :type index: :class:`QtCore.QModelIndex`
        :returns: parent index
        :rtype: :class:`QtCore.QModelIndex`
        :raises: None
        """
        if not index.isValid():
            return QtCore.QModelIndex()
        childItem = index.internalPointer()
        parentItem = childItem.parent()
        if parentItem is self._root:
            return QtCore.QModelIndex()
        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent):
        """Returns the number of rows under the given parent.
        When the parent is valid it means that rowCount is returning the number
        of children of parent.

        :param parent: the parent index
        :type parent: :class:`QtCore.QModelIndex`:
        :returns: the row count
        :rtype: int
        :raises: None
        """
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            parentItem = self._root
        else:
            parentItem = parent.internalPointer()
        return parentItem.child_count()

    def columnCount(self, parent):
        """Returns the number of columns for the children of the given parent.

        :param parent: the parent index
        :type parent: :class:`QtCore.QModelIndex`:
        :returns: the column count
        :rtype: int
        :raises: None
        """
        if parent.isValid():
            return parent.internalPointer().column_count()
        else:
            return self._root.column_count()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        """Returns the data stored under the given role for the item referred to by the index.

        :param index: the index
        :type index: QModelIndex
        :param role: the data role
        :type role: QtCore.Qt.ItemDataRole
        :returns: some data depending on the role
        :raises: None
        """
        if not index.isValid():
            return
        item = index.internalPointer()
        return item.data(index.column(), role)

    def headerData(self, section, orientation, role):
        """

        :param section:
        :type section:
        :param orientation:
        :type orientation:
        :param role:
        :type role:
        :returns: None
        :rtype: None
        :raises: None
        """
        if orientation == QtCore.Qt.Horizontal:
            d = self._root.data(section, role)
            if d is None and role == QtCore.Qt.DisplayRole:
                return str(section+1)
            return d
        if orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            return str(section+1)

    def insertRow(self, row, item, parent):
        """Inserts a single item before the given row in the child items of the parent specified.

        :param row: the index where the rows get inserted
        :type row: int
        :param item: the item to insert. When creating the item, make sure it's parent is None.
                     If not it will defeat the purpose of this function.
        :type item: :class:`TreeItem`
        :param parent: the parent
        :type parent: class:`QtCore.QModelIndex`
        :returns: Returns true if the row is inserted; otherwise returns false.
        :rtype: bool
        :raises: None
        """
        parentitem = parent.internalPointer()
        self.beginInsertRows(parent, row, row)
        item._parent = parentitem
        parentitem.childItems.insert(row, item)
        self.endInsertRows()
        # self.insertRows(len(parentitem.childItems), 1, parent)
        return True

    @property
    def root(self, ):
        """Return the root tree item

        :returns: the root item
        :rtype: :class:`TreeItem`
        :raises: None
        """
        return self._root

    def flags(self, index):
        """

        :param index:
        :type index:
        :returns: None
        :rtype: None
        :raises: None
        """
        if index.isValid():
            item = index.internalPointer()
            return item.flags()
        else:
            super(TreeModel, self).flags(index)
