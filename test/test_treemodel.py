import pytest

from PySide import QtCore

from easymodel import treemodel

DR = QtCore.Qt.DisplayRole


@pytest.fixture(scope='function')
def str_list_data():
    """Item data with a string list. ['a', 'b', 'hallo']"""
    return treemodel.ListItemData(['a', 'b', 'hallo'])


@pytest.fixture(scope='function')
def int_list_data():
    """Item data with an in list. [1, 2, 3, 4, 5, 6]"""
    return treemodel.ListItemData([1, 2, 3, 4, 5, 6])


@pytest.fixture(scope='function')
def mix_list_data():
    """Item data with a mixed list. ['a', None, False, 1, [1, '2']]"""
    return treemodel.ListItemData(['a', None, False, 1, [1, '2']])


@pytest.fixture(scope='function')
def listdatas(str_list_data, int_list_data, mix_list_data):
    return (str_list_data, int_list_data, mix_list_data)


@pytest.mark.parametrize("fixture,expected", [
    (0, 3),
    (1, 6),
    (2, 5),])
def test_listdata_column_count(fixture, expected, listdatas):
    data = listdatas[fixture]
    assert data.column_count() == expected


@pytest.mark.parametrize("fixture,column,role,expected", [
    (0, 0, DR, 'a'),
    (0, 1, DR, 'b'),
    (0, 2, DR, 'hallo'),
    (1, 0, DR, 1),
    (1, 1, DR, 2),
    (1, 2, DR, 3),
    (1, 3, DR, 4),
    (1, 4, DR, 5),
    (1, 5, DR, 6),
    (2, 0, DR, 'a'),
    (2, 1, DR, None),
    (2, 2, DR, 'False'),
    (2, 3, DR, 1),
    (2, 4, DR, '[1, \'2\']'),
    (0, -1, DR, None),
    (0, 3, DR, None),
    (0, 99, DR, None),
])
def test_listdata_data(fixture, column, role, expected, listdatas):
    data = listdatas[fixture].data(column, role)
    if expected is None:
        assert data is None
    else:
        assert data == expected


def test_internal_data(str_list_data):
    assert str_list_data.internal_data() == ['a', 'b', 'hallo']


@pytest.fixture(scope='module')
def stubitemdata1():
    """Stub item data

    Will return \"Data1\" for DisplayRole.
    Set data can change that.
    Column Count is 1.
    """
    class StubItemData1(treemodel.ItemData):
        def __init__(self):
            self.d = "Data1"

        def data(self, column, role):
            if role == DR:
                return self.d

        def set_data(self, column, value, role):
            if role == DR:
                self.d = value

        def column_count(self):
            return 1

    return StubItemData1


@pytest.fixture(scope='module')
def stubitemdata2():
    """Stub item data

    Will return \"Data2\" and \"Data3\" for DisplayRole
    and column 0 / 1.
    Column Count is 2.
    Flags returns 99.
    """
    class StubItemData2(treemodel.ItemData):
        def data(self, column, role):
            if role == DR:
                if column == 0:
                    return "Data2"
                elif column == 1:
                    return "Data3"

        def column_count(self):
            return 2

        def flags(self, index):
            return 99

    return StubItemData2


@pytest.fixture(scope='function')
def stub_tree(stubitemdata1, stubitemdata2):
    """Simple :class:`treemodel.TreeItem` tree.

    :root: TreeItem(None)
    :itdata1: stubitemdata2
    :c1: TreeItem(itdata1, root)
    :c2: TreeItem(stubitemdata2, root)
    :c3: TreeItem(stubitemdata1, c2)

    :returns: (root, c1, c2, c3, itdata1)
    """
    root = treemodel.TreeItem(None)
    itdata1 = stubitemdata2()
    c1 = treemodel.TreeItem(itdata1, root)
    c2 = treemodel.TreeItem(stubitemdata2(), root)
    c3 = treemodel.TreeItem(stubitemdata1(), c2)
    return (root, c1, c2, c3, itdata1,)


def test_treeitem_child(stub_tree):
    root, c1, c2, c3, itdata1 = stub_tree
    assert root.child(0) is c1
    assert root.child(1) is c2
    assert c2.child(0) is c3


@pytest.mark.parametrize("item,expected", [
    (0, 2),
    (1, 0),
    (2, 1),
    (3, 0)])
def test_treeitem_child_count(item, expected, stub_tree):
    assert stub_tree[item].child_count() == expected


@pytest.mark.parametrize("item,expected", [
    (0, 0),
    (1, 0),
    (2, 1),
    (3, 0)])
def test_treeitem_row(item, expected, stub_tree):
    assert stub_tree[item].row() == expected


@pytest.mark.parametrize("item,expected", [
    (0, 2),
    (1, 2),
    (2, 1),
    (3, 1)])
def test_treeitem_column_count(item, expected, stub_tree):
    assert stub_tree[item].column_count() == expected


@pytest.mark.parametrize("item,column,role,expected", [
    (0, 0, DR, None),
    (0, 1, DR, None),
    (1, 0, DR, "Data2"),
    (1, 1, DR, "Data3"),
    (2, 0, DR, "Data2"),
    (2, 1, DR, "Data3"),
    (3, 0, DR, "Data1"),
    (3, 1, DR, "Data1"),
])
def test_treeitem_data(item, column, role, expected, stub_tree):
    data = stub_tree[item].data(column, role)
    if expected is None:
        assert data is expected
    else:
        assert data == expected


@pytest.mark.parametrize("item,expected", [
    (0, None),
    (1, 0),
    (2, 0),
    (3, 2)])
def test_treeitem_parent(item, expected, stub_tree):
    parent = stub_tree[item].parent()
    if expected is None:
        assert parent is expected
    else:
        assert parent is stub_tree[expected]


def test_treeitem_itemdata(stub_tree):
    assert stub_tree[1].itemdata() is stub_tree[4]


def test_treeitem_internal_data(stub_tree):
    for i in stub_tree[1:-1]:
        assert i.internal_data() is None
    l = [1, 2, 3]
    data = treemodel.ListItemData(l)
    assert treemodel.TreeItem(data).internal_data() is l


@pytest.mark.parametrize("new", ["new", 1, 2, "test"])
def test_treeitem_set_data(new, stubitemdata1):
    itdata = stubitemdata1()
    ti = treemodel.TreeItem(itdata,)
    ti.set_data(0, new, DR)
    assert ti.data(0, DR) == new


@pytest.fixture(scope='function')
def stub_model(stubitemdata1, stubitemdata2):
    """Tree model. Returns (m, root, c1, c2, c3, c4, c5)

    :m: the model
    :root: TreeItem(None)
    :c1: TreeItem(stubitemdata2(), root)
    :c2: TreeItem(stubitemdata2(), root)
    :c3: TreeItem(stubitemdata1(), c2)
    :c4: TreeItem(stubitemdata1(), c2)
    :c5: TreeItem(stubitemdata1(), c4)
    """
    root = treemodel.TreeItem(None)
    m = treemodel.TreeModel(root)
    c1 = treemodel.TreeItem(stubitemdata2(), root)
    c2 = treemodel.TreeItem(stubitemdata2(), root)
    c3 = treemodel.TreeItem(stubitemdata1(), c2)
    c4 = treemodel.TreeItem(stubitemdata1(), c2)
    c5 = treemodel.TreeItem(stubitemdata1(), c4)
    return (m, root, c1, c2, c3, c4, c5)


@pytest.fixture(scope='function')
def stub_model_indexes(stub_model):
    """Indexes for stub model. Returns (c1i, c12i, c2i, c22i, c3i, c4i, c5i, invalid)

    :c1i: m.index(0, 0 , QtCore.QModelIndex())
    :c12i: m.index(0, 1 , QtCore.QModelIndex())
    :c2i: m.index(1, 0, QtCore.QModelIndex())
    :c22i: m.index(1, 1, QtCore.QModelIndex())
    :c3i: m.index(0, 0, c2i)
    :c4i: m.index(1, 0, c2i)
    :c5i: m.index(0, 0, c4i)
    :invalid: m.index(-1, 0)
    """
    m, root, c1, c2, c3, c4, c5 = stub_model
    c1i = m.index(0, 0 , QtCore.QModelIndex())
    c2i = m.index(1, 0, QtCore.QModelIndex())
    c12i = m.index(0, 1 , QtCore.QModelIndex())
    c22i = m.index(1, 1, QtCore.QModelIndex())
    c3i = m.index(0, 0, c2i)
    c4i = m.index(1, 0, c2i)
    c5i = m.index(0, 0, c4i)
    invalid = m.index(-1, 0)
    return (c1i, c12i, c2i, c22i, c3i, c4i, c5i, invalid)


def test_model_index(stub_model, stub_model_indexes):
    m, root, c1, c2, c3, c4, c5 = stub_model
    ptrs = [c1, c1, c2, c2, c3, c4, c5, None]
    for i, ptr in zip(stub_model_indexes, ptrs):
        assert i.internalPointer() is ptr


@pytest.mark.parametrize("item,expected", [
    (0, 7),
    (1, 7),
    (2, 7),
    (3, 7),
    (4, 2),
    (5, 2),
    (6, 5),
    (7, 7)])
def test_model_parent(item, expected, stub_model, stub_model_indexes):
    m = stub_model[0]
    assert m.parent(stub_model_indexes[item]) == stub_model_indexes[expected]


@pytest.mark.parametrize("item,rc", [
    (0, 0),
    (1, 0),
    (2, 2),
    (3, 0),
    (4, 0),
    (5, 1),
    (6, 0),
    (7, 2)])
def test_model_rowcount(item, rc, stub_model, stub_model_indexes):
    m = stub_model[0]
    assert m.rowCount(stub_model_indexes[item]) == rc


@pytest.mark.parametrize("item,cc", [
    (0, 2),
    (1, 2),
    (2, 1),
    (3, 1),
    (4, 1),
    (5, 1),
    (6, 1),
    (7, 2)])
def test_column_count(item, cc, stub_model, stub_model_indexes):
    m = stub_model[0]
    assert m.columnCount(stub_model_indexes[item]) == cc


@pytest.mark.parametrize("item,role,expected", [
    (0, DR, 'Data2'),
    (1, DR, 'Data3'),
    (2, DR, 'Data2'),
    (3, DR, 'Data3'),
    (4, DR, 'Data1'),
    (5, DR, 'Data1'),
    (6, DR, 'Data1'),
    (7, DR, None)])
def test_model_data(item, role, expected, stub_model, stub_model_indexes):
    data = stub_model[0].data(stub_model_indexes[item], role)
    if expected is None:
        assert data is expected
    else:
        assert data == expected


@pytest.mark.parametrize("item,role,new", [
    (4, DR, "new"),
    (5, DR, "hello"),
    (6, DR, "YAY"),
])
def test_model_set_data(item, role, new, stub_model, stub_model_indexes):
    m = stub_model[0]
    i = stub_model_indexes[item]
    m.setData(i, new, role)
    assert m.data(i, role) == new


def test_model_headerdata(stub_model):
    m = stub_model[0]
    for i in range(10):
        assert m.headerData(i, QtCore.Qt.Horizontal, DR) == str(i+1)
        assert m.headerData(i, QtCore.Qt.Vertical, DR) == str(i+1)

    rootdata = treemodel.ListItemData(['Sec1', 'Head2', 'Chap3'])
    root = treemodel.TreeItem(rootdata)
    m2 = treemodel.TreeModel(root)

    assert m2.headerData(0, QtCore.Qt.Horizontal, DR) == 'Sec1'
    assert m2.headerData(1, QtCore.Qt.Horizontal, DR) == 'Head2'
    assert m2.headerData(2, QtCore.Qt.Horizontal, DR) == 'Chap3'
    assert m2.headerData(3, QtCore.Qt.Horizontal, DR) == '4'
    assert m2.headerData(99, QtCore.Qt.Horizontal, DR) == '100'
    assert m2.headerData(3, QtCore.Qt.Vertical, DR) == '4'
    assert m2.headerData(99, QtCore.Qt.Vertical, DR) == '100'


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

    def test_set_data(self):
        pi = self.m.index_of_item(self.c4)
        c5i = self.m.index(0, 0, pi)
        assert self.m.data(c5i, DR) == "Data1"
        nd = "New Data"
        self.m.setData(c5i, nd, DR)
        assert self.m.data(c5i, DR) == nd

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
