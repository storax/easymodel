import pytest

from PySide import QtCore, QtGui

import easymodel


@pytest.fixture(scope='function')
def model():
    rootdata = easymodel.ListItemData(['Column0', 'Column1'])
    root = easymodel.TreeItem(rootdata)
    # Create a new model with the root
    model = easymodel.TreeModel(root)
    datal0r0 = easymodel.ListItemData(['l0r0c0', 'l0r0c1'])
    datal0r1 = easymodel.ListItemData(['l0r1c0', 'l0r1c1'])
    datal1r0 = easymodel.ListItemData(['l1r0c0', 'l1r0c1'])
    datal1r1 = easymodel.ListItemData(['l1r1c0', 'l1r1c1'])
    datal2r0 = easymodel.ListItemData(['l2r0c0', 'l2r0c1'])
    datal2r1 = easymodel.ListItemData(['l2r1c0', 'l2r1c1'])
    iteml0r0 = easymodel.TreeItem(datal0r0, parent=root)
    easymodel.TreeItem(datal0r1, parent=root)
    iteml1r0 = easymodel.TreeItem(datal1r0, parent=iteml0r0)
    easymodel.TreeItem(datal1r1, parent=iteml0r0)
    easymodel.TreeItem(datal2r0, parent=iteml1r0)
    easymodel.TreeItem(datal2r1, parent=iteml1r0)
    return model


@pytest.mark.parametrize("level", range(3))
def test_cbview_headers(qtbot, model, level):
    headers = ['Level0', 'Level1', 'Level2']
    cbview = easymodel.ComboBoxCascadeView(
        depth=3, parent=None, flags=0, headers=headers)
    cbview.model = model
    layout = cbview.layout()
    label = layout.itemAt(level*2+1).widget()
    assert label.text() == headers[level],\
        'Header text not correct for level %s!' % level


@pytest.mark.parametrize(
    "level,text",
    [(0, 'l0r0c0'), (1, 'l1r0c0'), (2, 'l2r0c0')])
def test_cbview_initial_texts(qtbot, model, level, text):
    cbview = easymodel.ComboBoxCascadeView(depth=3)
    cbview.model = model
    assert cbview.levels[level].currentText() == text,\
        'Combobox should show the first column of the first item of this level.'


@pytest.mark.parametrize(
    "level,text",
    [(0, 'l0r1c0'), (1, ''), (2, '')])
def test_cbview_change_nochildren(qtbot, model, level, text):
    cbview = easymodel.ComboBoxCascadeView(depth=3)
    cbview.model = model
    cbview.levels[0].setCurrentIndex(1)
    assert cbview.levels[level].currentText() == text
    i = model.index(1, 0)
    assert [i] == cbview.selected_indexes(0)
    assert [model.index(0, 0, i)] == cbview.selected_indexes(1)


@pytest.mark.parametrize(
    "level,text",
    [(0, 'l0r0c0'), (1, 'l1r0c0'), (2, 'l2r0c0')])
def test_cbview_change_firstlevel(qtbot, model, level, text):
    cbview = easymodel.ComboBoxCascadeView(depth=3)
    cbview.model = model
    cbview.levels[0].setCurrentIndex(1)
    cbview.levels[0].setCurrentIndex(0)
    assert cbview.levels[level].currentText() == text


@pytest.mark.parametrize("level", range(3))
def test_listview_headers(qtbot, model, level):
    headers = ['Level0', 'Level1', 'Level2']
    listview = easymodel.ListCascadeView(
        depth=3, parent=None, flags=0, headers=headers)
    listview.model = model
    layout = listview.splitter.widget(level).layout()
    header = layout.itemAt(0).widget()
    assert header.text() == headers[level],\
        'Header text not correct for level %s!' % level


@pytest.mark.parametrize(
    "level,text",
    [(0, 'l0r0c0'), (1, 'l1r0c0'), (2, 'l2r0c0')])
def test_listview_initial_texts(qtbot, model, level, text):
    cbview = easymodel.ListCascadeView(depth=3)
    cbview.model = model
    index = cbview.levels[level].currentIndex()
    assert index.data() == text,\
        'Current index should be the first column of the first item of this level.'


@pytest.mark.parametrize(
    "level,text",
    [(0, 'l0r1c0'), (1, None), (2, None)])
def test_listview_change_nochildren(qtbot, model, level, text):
    listview = easymodel.ListCascadeView(depth=3)
    listview.model = model
    i = model.index(1, 0)
    listview.levels[0].setCurrentIndex(i)
    index = listview.levels[level].currentIndex()
    assert index.data() == text
    assert [i] == listview.selected_indexes(0)
    assert [model.index(0, 0, i)] == listview.selected_indexes(1)
