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


@pytest.mark.parametrize("fixture,column,role,new", [
    (0, 0, DR, 'A'),
    (0, 1, DR, 'B'),
    (0, 2, DR, 'Cya'),
    (1, 0, DR, 10),
    (1, 1, DR, 0),
    (1, 2, DR, 99),
    (2, 0, DR, None),
    (2, 1, DR, 'Yoooo'),
    (0, -1, DR, None),
    (0, 3, DR, None),
    (0, 99, DR, None),
])
def test_listdata_setdata(fixture, column, role, new, listdatas):
    listdatas[fixture].set_data(column, new, role)
    assert listdatas[fixture].data(column, role) == new


def test_listdata_set_data_false_role():
    data = treemodel.ListItemData(['1', 2], editable=True)
    assert data.set_data(0, 0, QtCore.Qt.DecorationRole) is False
    assert data.set_data(0, 'a', QtCore.Qt.DecorationRole) is False


def test_listdata_flags():
    e = treemodel.ListItemData(list(range(3)), editable=True)
    s = treemodel.ListItemData(list(range(3)), editable=False)
    default = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
    for i in range(3):
        assert e.flags(i) == default | QtCore.Qt.ItemIsEditable
        assert s.flags(i) == default


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


def test_itemdata_default_setdata(stubitemdata2):
    data = stubitemdata2()
    assert data.set_data(0, 1, DR) is False
    assert data.set_data(0, 'a', DR) is False


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


def test_treeitem_userroles(stub_tree):
    items = stub_tree[0:-1]
    for i in items:
        for c in range(-2, 4):
            assert i.data(c, treemodel.TREEITEM_ROLE) is i
            idata = i.data(c, treemodel.INTERNAL_OBJ_ROLE)
            if i._data is not None:
                 assert idata is i.internal_data()
            else:
                assert idata is None


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


def test_root(stub_model):
    assert stub_model[0].root is stub_model[1]


def test_model_index(stub_model, stub_model_indexes):
    m, root, c1, c2, c3, c4, c5 = stub_model
    ptrs = [c1, c1, c2, c2, c3, c4, c5, None]
    for i, ptr in zip(stub_model_indexes, ptrs):
        assert i.internalPointer() is ptr
    assert not m.index(10, 0, QtCore.QModelIndex()).isValid()


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


@pytest.mark.parametrize("item,index", [
    (1, 7),
    (2, 0),
    (3, 2),
    (4, 4),
    (5, 5),
    (6, 6),
])
def test_model_indexforitem(item, index, stub_model, stub_model_indexes):
    m = stub_model[0]
    assert m.index_of_item(stub_model[item]) == stub_model_indexes[index]


def test_model_insertrow(stubitemdata1, stub_model, stub_model_indexes):
    m = stub_model[0]
    rows = (0, 0, 2)
    parent = stub_model_indexes[0]
    parentitem = parent.internalPointer()
    for r in rows:
        i = treemodel.TreeItem(stubitemdata1())
        inserted = m.insertRow(r, i, parent)
        assert inserted is True
        assert i._model is m
        assert i._parent is parentitem
        assert parent.internalPointer().childItems[r] is i
        assert m.index(r, 0, parent).internalPointer() is i

    newidata = stubitemdata1()
    newi = newidata.to_item(data=newidata)
    newi2 = stubitemdata1().to_item(newi)
    newi3 = stubitemdata1().to_item()
    newi2.add_child(newi3)
    assert newi3._parent is newi2
    assert newi2.childItems[0] is newi3
    newi.set_parent(i)
    assert newi._model is m
    assert newi2._model is m
    assert newi._parent is i
    assert newi2._parent is newi
    assert newi.childItems[0] is newi2
    assert i.childItems[0] is newi


def test_model_flags(stub_model, stub_model_indexes):
    m = stub_model[0]
    assert m.flags(stub_model_indexes[7]) is None
    assert m.flags(stub_model_indexes[0]) == 99
    assert m.flags(stub_model_indexes[4]) == QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable


def test_model_remove(stub_model, stub_model_indexes):
    m, root, c1, c2, c3, c4, c5 = stub_model
    c4.remove_child(c5)
    assert c5._parent is None
    assert c5._model  is None
    assert c4.childItems == []

    m.removeRow(0, stub_model_indexes[3])
    assert c2.childItems[0] is c4
    assert c3._parent is None
    assert c3._model is None

    m.removeRow(1, QtCore.QModelIndex())
    assert c2._parent is None
    assert c2._model is None
    assert c3._model is None
    assert c4._model is None

    c1.set_parent(None)
    assert c1._parent is None
    assert c1.get_model() is None
    assert root.childItems == []
