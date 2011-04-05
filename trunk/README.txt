The "wxgcc" is a GUI toolkit for GCC based wxPython which can be used under 
Windows and Linux. 

With that tool users can create and compile a C/C++ program very fast.

Befor start the program, you need to confirm the "wxpython" and "gcc" 
packages have been installed on your host.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
For Ubuntu/Linux User:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  you can run this command to install wxpython:
    $ sudo aptitude install python-wxgtk2.8 libwxgtk2.8-dev python-wxtools \ 
    libwxbase2.8-0 libwxgtk2.8-0 python-wxglade

  The other Linux Desktop can install these packages with its own package
  managment tool, such as yum, emerge and so on.

  GCC may have been installed as default for most of Linux Desktop. 

  After enter its directory, you can start the program by:
    $ python wxgcc.py &

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
For MS Windows User (From v1.8.5 start to support MS Windows):
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  a) Download and install mingw-get-inst-20110316.exe from:
http://sourceforge.net/projects/mingw/files/Automated%20MinGW%20Installer/mingw-get-inst/mingw-get-inst-20110316/

  NOTE:
    1. Antivirus Software such as Norton will delete the mingw exe file automatically, so you may 
       need to disable your Antivirus Software berfore installation.
    2. When displaying the "Select Components" during installation, you need to select the "C++" module. 
    3. Some packages need to be downloaded when installing, so make sure your Internet can works well.
    4. The default value could be used for the other options.

  After finished installation, you need to append "C:\MinGW\bin" to the PATH environmnet variable.
  ("My Computer -> Attribute -> Expert -> Environmnet Variable -> System Variable -> PATH", then 
  append ";C:\MinGW\bin" to the end.)

  b) Download and install python-2.7.msi from: http://www.python.org/ftp/python/2.7/

  c) Download and install wxPython2.8-win32-unicode-py27 from: http://www.wxpython.org/download.php

  d) Download and install py2exe-0.6.9.win32-py2.7.exe from: http://sourceforge.net/projects/py2exe/files/py2exe/0.6.9/

  Just use the default options when installing b), c) and d), after finished, you also need to append "C:\Python27"
  to the PATH environmnet variable.

  Then double click wxgcc.py to start the program.


If have any question, please mailto: zwang@ucrobotics.com 
For more information, please visit: http://www.ucrobotics.com/?q=cn/node/97
