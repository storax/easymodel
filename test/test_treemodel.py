from PySide import QtCore

from easymodel import treemodel

DR = QtCore.Qt.DisplayRole


class Test_ListItemData():

    @classmethod
    def setup_class(cls):
        cls.strlist = ['a', 'b', 'hallo']
        cls.intlist = [1, 2, 3, 4, 5, 6]
        cls.mixedlist = ['a', None, False, 1, [1, '2']]
        cls.slistdata = treemodel.ListItemData(cls.strlist)
        cls.ilistdata = treemodel.ListItemData(cls.intlist)
        cls.mixeddata = treemodel.ListItemData(cls.mixedlist)

    def test_column_count(self):
        assert self.slistdata.column_count() == 3
        assert self.ilistdata.column_count() == 6
        assert self.mixeddata.column_count() == 5

    def test_data(self):
        assert self.slistdata.data(0, DR) == 'a'
        assert self.slistdata.data(1, DR) == 'b'
        assert self.slistdata.data(2, DR) == 'hallo'
        assert self.ilistdata.data(0, DR) == '1'
        assert self.ilistdata.data(1, DR) == '2'
        assert self.ilistdata.data(2, DR) == '3'
        assert self.ilistdata.data(3, DR) == '4'
        assert self.mixeddata.data(0, DR) == 'a'
        assert self.mixeddata.data(1, DR) == 'None'
        assert self.mixeddata.data(2, DR) == 'False'
        assert self.mixeddata.data(3, DR) == '1'
        assert self.mixeddata.data(4, DR) == '[1, \'2\']'
        assert self.slistdata.data(-1, DR) is None
        assert self.slistdata.data(3, DR) is None
        assert self.slistdata.data(99, DR) is None
        assert self.slistdata.internal_data() is self.strlist


# stub test data
class StubItemData1(treemodel.ItemData):
    def data(self, column, role):
        if role == QtCore.Qt.DisplayRole:
            return "Data1"

    def column_count(self):
        return 1


class StubItemData2(treemodel.ItemData):
    def data(self, column, role):
        if role == QtCore.Qt.DisplayRole:
            if column == 0:
                return "Data2"
            elif column == 1:
                return "Data3"

    def column_count(self):
        return 2

    def flags(self, index):
        return 99


class Test_TreeItem():
    def setup(self):
        self.root = treemodel.TreeItem(None)
        self.itdata1 = StubItemData2()
        self.c1 = treemodel.TreeItem(self.itdata1, self.root)
        self.c2 = treemodel.TreeItem(StubItemData2(), self.root)
        self.c3 = treemodel.TreeItem(StubItemData1(), self.c2)

    def test_child(self):
        assert self.root.child(0) is self.c1
        assert self.root.child(1) is self.c2
        assert self.c2.child(0) is self.c3

    def test_child_count(self):
        assert self.root.child_count() == 2
        assert self.c1.child_count() == 0
        assert self.c2.child_count() == 1

    def test_row(self):
        assert self.root.row() == 0
        assert self.c1.row() == 0
        assert self.c2.row() == 1
        assert self.c3.row() == 0

    def test_column_count(self):
        assert self.root.column_count() == 2
        assert self.c1.column_count() == 2
        assert self.c2.column_count() == 1
        assert self.c3.column_count() == 1

    def test_data(self):
        assert self.root.data(0, DR) is None
        assert self.root.data(1, DR) is None
        assert self.c1.data(0, DR) == "Data2"
        assert self.c1.data(1, DR) == "Data3"
        assert self.c2.data(0, DR) == "Data2"
        assert self.c3.data(0, DR) == "Data1"

    def test_parent(self):
        assert self.root.parent() is None
        assert self.c1.parent() is self.root
        assert self.c2.parent() is self.root
        assert self.c3.parent() is self.c2

    def test_itemdata(self):
        assert self.c1.itemdata() is self.itdata1

    def test_internal_data(self):
        assert self.c1.internal_data() is None


class Test_TreeModel():

    @classmethod
    def setup_class(cls):
        cls.root = treemodel.TreeItem(None)
        cls.m = treemodel.TreeModel(cls.root)
        cls.c1 = treemodel.TreeItem(StubItemData2(), cls.root)
        cls.c2 = treemodel.TreeItem(StubItemData2(), cls.root)
        cls.c3 = treemodel.TreeItem(StubItemData1(), cls.c2)
        cls.c4 = treemodel.TreeItem(StubItemData1(), cls.c2)
        cls.c5 = treemodel.TreeItem(StubItemData1(), cls.c4)

    def test_index(self):
        c1i = self.m.index(0, 0, QtCore.QModelIndex())
        assert c1i.internalPointer() is self.c1
        assert self.m.index(0, 0).internalPointer() is self.c1
        c2i = self.m.index(1, 0, QtCore.QModelIndex())
        assert c2i.internalPointer() is self.c2
        c3i = self.m.index(0, 0, c2i)
        assert c3i.internalPointer() is self.c3
        assert self.m.index(-1, 0) == QtCore.QModelIndex()

    def test_parent(self):
        assert self.m.parent(QtCore.QModelIndex()) == QtCore.QModelIndex()
        c1i = self.m.index(0, 0)
        c2i = self.m.index(1, 0)
        c3i = self.m.index(0, 0, c2i)
        assert self.m.parent(c1i) == QtCore.QModelIndex()
        assert self.m.parent(c2i) == QtCore.QModelIndex()
        assert self.m.parent(c3i) == c2i

    def test_row_count(self):
        c1i = self.m.index(0, 0)
        c2i = self.m.index(1, 0)
        c3i = self.m.index(0, 0, c2i)
        assert self.m.rowCount(QtCore.QModelIndex()) == 2
        assert self.m.rowCount(c1i) == 0
        assert self.m.rowCount(c2i) == 2
        assert self.m.rowCount(c3i) == 0

    def test_column_count(self):
        c1i = self.m.index(0, 0)
        c2i = self.m.index(1, 0)
        c3i = self.m.index(0, 0, c2i)
        assert self.m.columnCount(QtCore.QModelIndex()) == 2
        assert self.m.columnCount(c1i) == 2
        assert self.m.columnCount(c2i) == 1
        assert self.m.columnCount(c3i) == 1

    def test_data(self):
        c1i = self.m.index(0, 0)
        c12i = self.m.index(0, 1)
        assert c12i.row() == 0
        assert c12i.column() == 1
        assert c12i.internalPointer() is self.c1
        c2i = self.m.index(1, 0)
        c22i = self.m.index(1, 1)
        c3i = self.m.index(0, 0, c2i)
        assert self.m.data(QtCore.QModelIndex(), DR) is None
        assert self.m.data(c1i, DR) == "Data2"
        assert self.m.data(c12i, DR) == "Data3"
        assert self.m.data(c2i, DR) == "Data2"
        assert self.m.data(c22i, DR) == "Data3"
        assert self.m.data(c3i, DR) == "Data1"

    def test_headerdata(self):
        assert self.m.headerData(0, QtCore.Qt.Horizontal, DR) == '1'
        assert self.m.headerData(1, QtCore.Qt.Horizontal, DR) == '2'
        assert self.m.headerData(2, QtCore.Qt.Horizontal, DR) == '3'
        assert self.m.headerData(0, QtCore.Qt.Vertical, DR) == '1'
        assert self.m.headerData(1, QtCore.Qt.Vertical, DR) == '2'
        assert self.m.headerData(2, QtCore.Qt.Vertical, DR) == '3'

        rootdata = treemodel.ListItemData(['Sec1', 'Head2', 'Chap3'])
        root = treemodel.TreeItem(rootdata)
        m = treemodel.TreeModel(root)
        assert m.headerData(0, QtCore.Qt.Horizontal, DR) == 'Sec1'
        assert m.headerData(1, QtCore.Qt.Horizontal, DR) == 'Head2'
        assert m.headerData(2, QtCore.Qt.Horizontal, DR) == 'Chap3'
        assert m.headerData(3, QtCore.Qt.Horizontal, DR) == '4'
        assert m.headerData(99, QtCore.Qt.Horizontal, DR) == '100'
        assert m.headerData(3, QtCore.Qt.Vertical, DR) == '4'
        assert m.headerData(99, QtCore.Qt.Vertical, DR) == '100'

    def test_insertRow(self):
        root = treemodel.TreeItem(None)
        i1 = treemodel.TreeItem(StubItemData2(), root)
        m = treemodel.TreeModel(root)
        newi1 = treemodel.TreeItem(treemodel.ListItemData(['1']))
        newi2 = treemodel.TreeItem(treemodel.ListItemData(['2']))
        newi3 = treemodel.TreeItem(treemodel.ListItemData(['3']))
        parent = m.index(0, 0)
        assert parent.internalPointer() is i1
        m.insertRow(0, newi1, parent)
        assert newi1._model is m
        assert newi1._parent is i1
        assert i1.childItems[0] is newi1
        assert m.index(0, 0, parent).internalPointer() is newi1
        m.insertRow(0, newi2, parent)
        assert newi2._model is m
        assert newi2._parent is i1
        assert i1.childItems[0] is newi2
        assert m.index(0, 0, parent).internalPointer() is newi2
        assert m.index(1, 0, parent).internalPointer() is newi1
        m.insertRow(2, newi3, parent)
        assert newi3._model is m
        assert newi3._parent is i1
        assert i1.childItems[2] is newi3
        assert m.index(0, 0, parent).internalPointer() is newi2
        assert m.index(1, 0, parent).internalPointer() is newi1
        assert m.index(2, 0, parent).internalPointer() is newi3

        newi4 = treemodel.TreeItem(treemodel.ListItemData(['4']))
        newi5 = treemodel.TreeItem(treemodel.ListItemData(['5']), newi4)
        newi3.add_child(newi4)
        assert newi4._model is m
        assert newi5._model is m
        assert newi4._parent is newi3
        assert newi5._parent is newi4
        assert newi3.childItems[0] is newi4
        assert newi4.childItems[0] is newi5
        newi3index = m.index(2, 0, parent)
        newi4index = m.index(0, 0, newi3index)
        newi5index = m.index(0, 0, newi4index)
        assert newi4index.internalPointer() is newi4
        assert newi5index.internalPointer() is newi5

    def test_removeRow(self):
        root = treemodel.TreeItem(None)
        i1 = treemodel.TreeItem(StubItemData2(), root)
        m = treemodel.TreeModel(root)
        newi1 = treemodel.TreeItem(treemodel.ListItemData(['1']), i1)
        newi2 = treemodel.TreeItem(treemodel.ListItemData(['2']), i1)
        newi3 = treemodel.TreeItem(treemodel.ListItemData(['3']), i1)
        newi4 = treemodel.TreeItem(treemodel.ListItemData(['4']), newi3)
        parent = m.index(0, 0)
        assert newi1._model is m
        assert newi1._parent is i1
        assert i1.childItems[0] is newi1
        i1.remove_child(newi1)
        assert i1.childItems[0] is newi2
        assert newi1._model is None
        assert newi1._parent is None
        m.removeRow(0, parent)
        assert i1.childItems[0] is newi3
        assert newi2._model is None
        assert newi2._parent is None
        m.removeRow(0, parent)
        assert len(i1.childItems) == 0
        assert newi3._model is None
        assert newi3._parent is None
        assert newi4._model is None
        assert newi4._parent is newi3
        assert m.index(0, 0, QtCore.QModelIndex()).isValid()
        m.removeRow(0, QtCore.QModelIndex())
        assert i1._model is None
        assert i1._parent is None
        assert not m.index(0, 0, QtCore.QModelIndex()).isValid()

    def test_index_of_item(self, ):
        assert self.root
        i1 = self.m.index_of_item(self.root)
        assert i1.row() == -1
        assert i1.column() == -1
        assert not i1.isValid()
        assert not i1.parent().isValid()
        i2 = self.m.index_of_item(self.c1)
        assert i2.row() == 0
        assert i2.column() == 0
        assert i2.parent() == i1
        i3 = self.m.index_of_item(self.c2)
        assert i3.row() == 1
        assert i3.column() == 0
        assert i3.parent() == i1
        i4 = self.m.index_of_item(self.c3)
        assert i4.row() == 0
        assert i4.column() == 0
        assert i4.parent() == i3
        i5 = self.m.index_of_item(self.c4)
        assert i5.row() == 1
        assert i5.column() == 0
        assert i5.parent() == i3
        i6 = self.m.index_of_item(self.c5)
        assert i6.row() == 0
        assert i6.column() == 0
        assert i6.parent() == i5
        invalidi = treemodel.TreeItem(treemodel.ListItemData(['1']))
        i7 = self.m.index_of_item(invalidi)
        assert i7.row() == -1
        assert i7.column() == -1
        assert not i7.isValid()
        assert not i7.parent().isValid()

    def test_flags(self):
        self.m.flags(QtCore.QModelIndex())
        assert self.m.flags(self.m.index(0,0,QtCore.QModelIndex())) == 99
