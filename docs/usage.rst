Usage
========

Model
-----

The :mod:`easymodel` module provides an simple but powerful general purpose
treemodel. The model uses :class:`easymodel.TreeItem` instances that act like
rows.

The tree item itself uses a :class:`easymodel.ItemData` instance to provide
the data. That way, the structure and logic of the whole model is encapsulated in the model and tree item classes. They take care of indexing, insertion, removal etc.

As a user you only need to subclass :class:`easymodel.ItemData` to wrap
arbitrary objects. It is pretty easy.

There is also a rudimentary :class:`easymodel.ListItemData` that might be enough for simple data.

Root
~~~~

Each model needs a root item. The root item is the parent of all top level tree items that hold data. It is also responsible for the headers. So in most cases it is enough to simply use
a :class:`easymodel.ListItemData`::

  import easymodel

  headers = ['Name', 'Speed', 'Altitude']
  rootdata = easymodel.ListItemData(headers)
  # roots do not have a parent
  rootitem = easymodel.TreeItem(rootdata, parent=None)


Creating a simple model
~~~~~~~~~~~~~~~~~~~~~~~

There are three steps involved. Create a root item, a model and wrap the data.
The creation of a model is simple::

  # use the root item from above
  model = easymodel.TreeModel(rootitem)

Thats it. The root item might already have children. That way, you can initialize a model with data.

Add Items
~~~~~~~~~

Let's assume our data consists of items with 3 values: Name, Velocity, Altitude.
The data might describe a vehicle, like an airplane or something like that.
Before we create our own :class:`easymodel.ItemData` subclasses, we use simple
lists, so we can use :class:`easymodel.ListItemData`. First create the data::

  data1 = easymodel.ListItemData(['Cessna', 250, 2000])
  data2 = easymodel.ListItemData(['747', 750, 6000])
  data3 = easymodel.ListItemData(['Fuel Plane', '730', 5000])

Wrap the data in items::

  # specify the parent to add it directly to the model
  item1 = TreeItem(data1, parent=rootitem)
  # or add it later
  item2 = TreeItem(data2)
  item2.set_parent(rootitem)
  # use the builtin to_item method
  item3 = data3.to_item(item2)

The tree items will automatically update the model. No need to emit any signals or call further methods.

Remove Items
~~~~~~~~~~~~

Let's say the fuel plane finished its job and landed. You can remove it from the model simply by
setting the parent to None::

  item3.set_parent(None)

You could have also used the model's methods to remove it but this way is much easier.

Wrap arbitrary objects
~~~~~~~~~~~~~~~~~~~~~~

To wrap arbitrary objects in an item data instance, you need to subclass it.
Let's assume we have a very simple airplane class::

  class Airplane(object):
      """This is the data we want to display in a view. An airplane.
  
      It has a name, a velocity and altitude.
      """
      def __init__(self, name, speed, altitude):
          self.name = name
          self.speed = speed
          self.altitude = altitude

Let's create a item data subclass that has three columns: Name, Speed, Altitude.
Speed and Altitude should be editable.

First subclass :class:`easymodel.ItemData`. It can store an airplane instance.::

  class AirplaneItemData(easymodel.ItemData):
      """An item data object that can extract information from an airplane instance.
      """
      def __init__(self, airplane):
          self.airplane = airplane

The column count is 3 and we can also give access to the airplane that is stored::

      def column_count(self,):
          """Return 3. For name, velocity and altitude."""
          return 3
  
      def internal_data(self):
          """Return the airplane instance"""
          return self.airplane

By default an item is enabled and selectable. But speed and altitude should be editable.
So lets override :meth:`easymodel.ItemData.flags`::

      def flags(self, column):
          """Return flags for enabled and selectable. Speed and altitude are also editable."""
          default = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
          if column == 0:
              return default
          else:
              return default | QtCore.Qt.ItemIsEditable

Now we need pass the data to the model. This is pretty simple. Just pass the right attribute
for each column::
  
      def data(self, column, role):
          """Return the data of the airplane"""
          if role == QtCore.Qt.DisplayRole:
              return (self.airplane.name, self.airplane.speed, self.airplane.altitude)[column]

Setting the data is not that complicated. Just set the right attribute for each column::
  
      def set_data(self, column, value, role):
          """Set the data of the airplane"""
          if role == QtCore.Qt.EditRole or role == QtCore.Qt.DisplayRole:
              attr = ('speed', 'altitude')[column-1]
              setattr(self.airplane, attr, value)
              return True
          return False
  
Now we can use this class to wrap our own airplanes and add them to a treeitem/model::

  # create a plane
  plane = Airplane('Nimbus 4', 0, 0)
  # wrap it in a data object
  planedata = AirplaneItemData(plane)
  # add it to the model
  planeitem = easymodel.TreeItem(planedata, rootitem)


Delegate
--------

Sometimes you want to have arbitrary widgets in your views. ItemDelegates of Qt are cool,
but it is very hard to get your arbitrary widget into the view.

If the widget changes a lot or you want to use the UI Designer, the regular workflow of styled item delegates is a bit flawed.
The :class:`easymodel.widgetdelegate.Widgetdelegate` is there to help.

Let's assume you want have a spin box and a randomize button for the altitude of your planes
in a view. The widget might look like this::

  class RandomSpinBox(QtGui.QWidget):
      """SpinBox plus randomize button
      """
  
      def __init__(self, parent=None, flags=0):
          super(RandomSpinBox, self).__init__(parent, flags)
          self.main_hbox = QtGui.QHBoxLayout(self)
          self.value_sb = QtGui.QSpinBox(self)
          self.random_pb = QtGui.QPushButton("Randomize")
          self.main_hbox.addWidget(self.value_sb)
          self.main_hbox.addWidget(self.random_pb)
  
          self.random_pb.clicked.connect(self.randomize)
  
      def randomize(self, *args, **kwargs):
          v = random.randint(0, 99)
          self.value_sb.setValue(v)

To create a delegate for this widget subclass :class:`easymodel.widgetdelegate.Widgetdelegate`::

  import easymodel.widgetdelegate as widgetdelegate

  class RandomSpinBoxDelegate(widgetdelegate.WidgetDelegate):
      """RandomSpinBox delegate"""
  
      def __init__(self, parent=None):
          super(RandomSpinBoxDelegate, self).__init__(parent)

Implement the abstract methods. First reimplement :meth:`easymodel.widgetdelegate.Widgetdelegate.create_widget`.
It is used to create the widget that will be rendered in the view::

    def create_widget(self, parent=None):
        return RandomSpinBox(parent)

If your editor should look exactly the same you can reuse this function::

    def create_editor_widget(self, parent, option, index):
        return self.create_widget(parent)

Now you need to implement :meth:`easymodel.widgetdelegate.Widgetdelegate.setEditorData`.
It will set the editor in the right state to represent a index in the model.
So we take the data of the index and put it in the spinbox::

    def setEditorData(self, widget, index):
        d = index.data(QtCore.Qt.DisplayRole)
        if d:
            widget.value_sb.setValue(int(d))
        else:
            widget.value_sb.setValue(int(0))

:meth:`easymodel.widgetdelegate.Widgetdelegate.set_widget_index` does the same for
the widget that is rendered. Every time an index is painted, the widget has to
be set in the right state to represent the index. Because we already did that for the editor
we can reuse the function::

    def set_widget_index(self, index):
        self.setEditorData(self.widget, index)

Now all that is left is :meth:`easymodel.widgetdelegate.Widgetdelegate.setModelData`.
Here you take the value from the editor and set the data in the model::

    def setModelData(self, editor, model, index):
        v = editor.value_sb.value()
        model.setData(index, v, QtCore.Qt.EditRole)

Done! Now you can use the delegate in any view. But I recommend using
one of the views in :mod:`easymodel.widgetdelegate`.

You can either use the :class:`WidgetDelegateViewMixin` for your own views or use one
of the premade views: :class:`WD_AbstractItemView`, :class:`WD_ListView`, :class:`WD_TableView`
:class:`WD_TreeView`.

They will make the user experience better. When the user clicks an widget delegate, it will
be set into edit mode and the click will be propagated to the editor. That way it behaves almost
like the widget delegate were a regular widget.


Little example app
------------------

Let's create a simple widget with a view and controls to add new items into the view.
We reuse the code from above.

The window has a view, an add button and 3 edits for name, speed and altitude.
When the add button is clicked, a new airplane should be inserted into the model.
The parent should be the currently selected index.

First create the widget::


  class AirplaneAppWidget(QtGui.QWidget):
      def __init__(self, parent=None, flags=0):
          super(AirplaneAppWidget, self).__init__(parent, flags)
          self.main_vbox = QtGui.QVBoxLayout(self)
          self.add_hbox = QtGui.QHBoxLayout()
  
          self.instruction_lb = QtGui.QLabel("Select Item and click add!", self)
          self.view = widgetdelegate.WD_TreeView(self)
  
          self.add_pb = QtGui.QPushButton('Add')
          self.add_pb.clicked.connect(self.add_airplane)
  
          self.name_lb = QtGui.QLabel('Name')
          self.name_le = QtGui.QLineEdit()
          self.speed_lb = QtGui.QLabel('Speed')
          self.speed_sb = QtGui.QSpinBox()
          self.altitude_lb = QtGui.QLabel('Altitude')
          self.altitude_sb = QtGui.QSpinBox()
  
          self.main_vbox.addWidget(self.instruction_lb)
          self.main_vbox.addWidget(self.view)
          self.main_vbox.addLayout(self.add_hbox)
          self.add_hbox.addWidget(self.add_pb)
          self.add_hbox.addWidget(self.name_lb)
          self.add_hbox.addWidget(self.name_le)
          self.add_hbox.addWidget(self.speed_lb)
          self.add_hbox.addWidget(self.speed_sb)
          self.add_hbox.addWidget(self.altitude_lb)
          self.add_hbox.addWidget(self.altitude_sb)
  
          self.delegate1 = RandomSpinBoxDelegate()
          self.view.setItemDelegateForColumn(2, self.delegate1)
          
          # Now we can build ourselves models
          # First we need a root
          rootdata = easymodel.ListItemData(['Name', 'Velocity', 'Altitude'])
          root = easymodel.TreeItem(rootdata)
          # Create a new model with the root
          model = easymodel.TreeModel(root)

	  self.view.setModel(model)

Now for the button callback. All we need to do is create an airplane, wrap it in a
data/item and parent it under the current index::

      def add_airplane(self, *args, **kwargs):
          # get parent item
          currentindex = self.view.currentIndex()
          if currentindex.isValid():
              # items are stored in the internal pointer
	      # but if you use a proxy model this might not work
	      # user the TREEITEM_ROLE instead
              pitem = currentindex.data(easymodel.TREEITEM_ROLE)
	  else:
              # nothing selected. Take root as parent
              pitem = self.view.model().root
  
          # create a new airplane
          name = self.name_le.text()
          speed = self.speed_sb.value()
          altitude = self.altitude_sb.value()
          airplane = Airplane(name, speed, altitude)
          # wrap it in an item data instance
          adata = AirplaneItemData(airplane)
          # create a tree item.
          # because parent is given, the item will
          # automatically be inserted in the model
          easymodel.TreeItem(adata, parent=pitem)

The rest of the app code can look like this::

  app = QtGui.QApplication([], QtGui.QApplication.GuiClient)
  app.setStyle(QtGui.QStyleFactory.create("plastique"))
  apw = AirplaneAppWidget()
  apw.show()
  app.exec_()


Complete Code
-------------

Everything put together::

  import random
  
  from PySide import QtCore, QtGui
  
  from easymodel import treemodel, widgetdelegate
  
  
  class Airplane(object):
      """This is the data we want to display in a view. An airplane.
  
      It has a name, a velocity and altitude.
      """
      def __init__(self, name, speed, altitude):
          self.name = name
          self.speed = speed
          self.altitude = altitude
  
  
  class AirplaneItemData(easymodel.ItemData):
      """An item data object that can extract information from an airplane instance.
      """
      def __init__(self, airplane):
          self.airplane = airplane
  
      def data(self, column, role):
          """Return the data of the airplane"""
          if role == QtCore.Qt.DisplayRole:
              return (self.airplane.name, self.airplane.speed, self.airplane.altitude)[column]
  
      def set_data(self, column, value, role):
          """Set the data of the airplane"""
          if role == QtCore.Qt.EditRole or role == QtCore.Qt.DisplayRole:
              attr = ('name', 'speed', 'altitude')[column]
              setattr(self.airplane, attr, value)
              return True
          return False
  
      def column_count(self,):
          """Return 3. For name, velocity and altitude."""
          return 3
  
      def internal_data(self):
          """Return the airplane instance"""
          return self.airplane
  
      def flags(self, column):
          """Return flags for enabled and selectable. Speed and altitude are also editable."""
          default = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
          if column == 0:
              return default
          else:
              return default | QtCore.Qt.ItemIsEditable
  
  
  class RandomSpinBox(QtGui.QWidget):
      """SpinBox plus randomize button
      """
  
      def __init__(self, parent=None, flags=0):
          super(RandomSpinBox, self).__init__(parent, flags)
          self.main_hbox = QtGui.QHBoxLayout(self)
          self.value_sb = QtGui.QSpinBox(self)
          self.random_pb = QtGui.QPushButton("Randomize")
          self.main_hbox.addWidget(self.value_sb)
          self.main_hbox.addWidget(self.random_pb)
  
          self.random_pb.clicked.connect(self.randomize)
  
      def randomize(self, *args, **kwargs):
          v = random.randint(0, 99)
          self.value_sb.setValue(v)
  
  
  class RandomSpinBoxDelegate(widgetdelegate.WidgetDelegate):
      """RandomSpinBox delegate
      """
  
      def __init__(self, parent=None):
          super(RandomSpinBoxDelegate, self).__init__(parent)
  
      def create_widget(self, parent=None):
          return RandomSpinBox(parent)
  
      def create_editor_widget(self, parent, option, index):
          return self.create_widget(parent)
  
      def setEditorData(self, widget, index):
          d = index.data(QtCore.Qt.DisplayRole)
          if d:
              widget.value_sb.setValue(int(d))
          else:
              widget.value_sb.setValue(int(0))
  
      def set_widget_index(self, index):
          self.setEditorData(self.widget, index)
  
      def setModelData(self, editor, model, index):
          v = editor.value_sb.value()
          model.setData(index, v, QtCore.Qt.EditRole)
  
  
  class AirplaneAppWidget(QtGui.QWidget):
      def __init__(self, parent=None, flags=0):
          super(AirplaneAppWidget, self).__init__(parent, flags)
          self.main_vbox = QtGui.QVBoxLayout(self)
          self.add_hbox = QtGui.QHBoxLayout()
  
          self.instruction_lb = QtGui.QLabel("Select Item and click add!", self)
          self.view = widgetdelegate.WD_TreeView(self)
  
          self.add_pb = QtGui.QPushButton('Add')
          self.add_pb.clicked.connect(self.add_airplane)
  
          self.name_lb = QtGui.QLabel('Name')
          self.name_le = QtGui.QLineEdit()
          self.speed_lb = QtGui.QLabel('Speed')
          self.speed_sb = QtGui.QSpinBox()
          self.altitude_lb = QtGui.QLabel('Altitude')
          self.altitude_sb = QtGui.QSpinBox()
  
          self.main_vbox.addWidget(self.instruction_lb)
          self.main_vbox.addWidget(self.view)
          self.main_vbox.addLayout(self.add_hbox)
          self.add_hbox.addWidget(self.add_pb)
          self.add_hbox.addWidget(self.name_lb)
          self.add_hbox.addWidget(self.name_le)
          self.add_hbox.addWidget(self.speed_lb)
          self.add_hbox.addWidget(self.speed_sb)
          self.add_hbox.addWidget(self.altitude_lb)
          self.add_hbox.addWidget(self.altitude_sb)
  
          self.delegate1 = RandomSpinBoxDelegate()
          #elf.view.setItemDelegateForColumn(2, self.delegate1)
  
          # Now we can build ourselves models
          # First we need a root
          rootdata = easymodel.ListItemData(['Name', 'Velocity', 'Altitude'])
          root = easymodel.TreeItem(rootdata)
  
          # Create a new model with the root
          self.model = easymodel.TreeModel(root)
          self.view.setModel(self.model)
  
      def add_airplane(self, *args, **kwargs):
          # get parent item
          currentindex = self.view.currentIndex()
          if currentindex.isValid():
              # items are stored in the internal pointer
	      # but if you use a proxy model this might not work
	      # user the TREEITEM_ROLE instead
              pitem = currentindex.data(easymodel.TREEITEM_ROLE)
          else:
              # nothing selected. Take root as parent
              pitem = self.view.model().root
  
          # create a new airplane
          name = self.name_le.text()
          speed = self.speed_sb.value()
          altitude = self.altitude_sb.value()
          airplane = Airplane(name, speed, altitude)
          # wrap it in an item data instance
          adata = AirplaneItemData(airplane)
          # create a tree item.
          # because parent is given, the item will
          # automatically be inserted in the model
          easymodel.TreeItem(adata, parent=pitem)
  
  if __name__ == "__main__":
      # Create a view to show what is happening
      app = QtGui.QApplication([], QtGui.QApplication.GuiClient)
      app.setStyle(QtGui.QStyleFactory.create("plastique"))
      apw = AirplaneAppWidget()
      apw.show()
      app.exec_()
