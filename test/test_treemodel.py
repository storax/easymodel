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


class Test_TreeItem():
    def setup(self):
        self.root = treemodel.TreeItem(None)
        self.c1 = treemodel.TreeItem(StubItemData2(), self.root)
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
        assert self.c1.column_count() == 0
        assert self.c2.column_count() == 1
        assert self.c3.column_count() == 0

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


class Test_TreeModel():

    @classmethod
    def setup_class(cls):
        cls.root = treemodel.TreeItem(None)
        cls.c1 = treemodel.TreeItem(StubItemData2(), cls.root)
        cls.c2 = treemodel.TreeItem(StubItemData2(), cls.root)
        cls.c3 = treemodel.TreeItem(StubItemData1(), cls.c2)
        cls.m = treemodel.TreeModel(cls.root)

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
        assert self.m.rowCount(c2i) == 1
        assert self.m.rowCount(c3i) == 0

    def test_column_count(self):
        c1i = self.m.index(0, 0)
        c2i = self.m.index(1, 0)
        c3i = self.m.index(0, 0, c2i)
        assert self.m.columnCount(QtCore.QModelIndex()) == 2
        assert self.m.columnCount(c1i) == 0
        assert self.m.columnCount(c2i) == 1
        assert self.m.columnCount(c3i) == 0

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
        assert m.index(0, 0, parent).internalPointer() is newi1
        m.insertRow(0, newi2, parent)
        assert m.index(0, 0, parent).internalPointer() is newi2
        assert m.index(1, 0, parent).internalPointer() is newi1
        m.insertRow(2, newi3, parent)
        assert m.index(0, 0, parent).internalPointer() is newi2
        assert m.index(1, 0, parent).internalPointer() is newi1
        assert m.index(2, 0, parent).internalPointer() is newi3
