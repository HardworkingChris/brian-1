echo Using $(which python)

# change into the virtualenv directory
cd ~/.jenkins/virtual_envs/$PythonVersion/$packages

# if no system-wide packages are used, update numpy etc. to newest version
if [ $packages = newest ]; then
  echo "Using newest available package versions"
  bin/pip install --upgrade numpy 
  bin/pip install --upgrade scipy sympy
  bin/pip install --upgrade matplotlib
elif [ $packages = oldest ]; then
  echo "Using oldest available package versions supported by Brian"
  bin/pip install numpy==1.3.0
  # scipy 0.7 has a bug that makes it impossible to use weave, download the
  # package and apply the patch before installing
  mkdir downloads || :
  wget -O downloads/scipy-0.7.0.tar.gz http://sourceforge.net/projects/scipy/files/scipy/0.7.0/scipy-0.7.0.tar.gz/download
  cd downloads
  tar xvf scipy-0.7.0.tar.gz
  # get and apply patch
  wget http://projects.scipy.org/scipy/raw-attachment/ticket/739/weave-739.patch
  patch -p1 < weave-739.patch
  # build scipy
  ../bin/python setup.py install
  cd ..
  
  bin/pip install sympy
  # Brian depencies state matplotlib>=0.90.1 but 0.98.1 is the oldest version still available
  bin/pip install http://sourceforge.net/projects/matplotlib/files/matplotlib/matplotlib-0.98.1/matplotlib-0.98.1.tar.gz/download
fi

# Print the version numbers for the dependencies
bin/python -c "import numpy; print 'numpy version: ', numpy.__version__"
bin/python -c "import scipy; print 'scipy version: ', scipy.__version__"
bin/python -c "import sympy; print 'sympy version: ', sympy.__version__"
bin/python -c "import matplotlib; print 'matplotlib version: ', matplotlib.__version__"

# Make sure the build ends up in the build/lib directory
python setup.py build --build-lib=build/lib
