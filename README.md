
Manipulator Control Program
=================

The Manipulator Control Program allows to control stage and manipulator positioning through a game controller and GUI. Locations can be stored and later regained. 

Features
-----------
* full control of stage movements using a game controller 
* manipulator approaches can furthermore be controlled with the game controller 
* stage and manipulator moves can be synched for movements in parallel 
* unlimited number of home locations can be stored, moved-to, updated and deleted
* unlimited number of stage locations can stored, moved-to, updated and deleted
* includes class to interact with the Luigs&Neumann manipulators through the SM-5 control box
* includes class to interact with the Physik Instrumte C-843 DC-Servo-Motor Controller : three motors moving the stage in x, y and z-direction are connected to the card
* all locations can be saved and loaded


### Main Window
![alt text](manipulator_gui.png "Example session of the Manipulator Control Program")


Built
-----------
The graphical user interface (*manipulatorTemplate.ui*) is built in **Qt Designer** (Version 4.8.6). The interface file (*manipulatorTemplate.py*) is generated with 
```python
pyuic4 manipulatorTemplate.ui -o manipulatorTemplate.py
```

Usage
-----------
The **Manipulator Control Program** itself is started with 
```python
python manipulator.py
```

Requires
-----------
Besides standard python packages such as **numpy**, **time**, **sys**, **pickle** etc., the following packages are required :

* h5py
* PyQt4
* threading
* socket
* pygame
* select

License
-----------
This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

