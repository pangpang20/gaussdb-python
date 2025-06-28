gaussdb -- GaussDB database adapter for Python
===================================================

**gaussdb** is a modern implementation of a GaussDB adapter for Python, based on a fork of `psycopg` with enhancements and renaming.

.. _Hacking:

Hacking
-------

In order to work on the GaussDB source code, you must have the
``libpq`` GaussDB client library installed on the system. For instance, on
EulerOS x86_64 systems, you can obtain it by running::

    # Update the system package index
    sudo apt update

    # Install required tools
    sudo apt install -y wget unzip

    # Download the GaussDB driver package
    wget -O /tmp/GaussDB_driver.zip https://dbs-download.obs.cn-north-1.myhuaweicloud.com/GaussDB/1730887196055/GaussDB_driver.zip

    # Extract the driver package and remove the zip file
    unzip /tmp/GaussDB_driver.zip -d /tmp/
    rm -rf /tmp/GaussDB_driver.zip

    # Copy the Python driver tarball to /tmp
    \cp /tmp/GaussDB_driver/Centralized/Hce2_X86_64/GaussDB-Kernel*64bit_Python.tar.gz /tmp/

    # Extract the driver tarball and clean up
    tar -zxvf /tmp/GaussDB-Kernel*64bit_Python.tar.gz -C /tmp/
    rm -rf /tmp/GaussDB-Kernel*64bit_Python.tar.gz
    rm -rf /tmp/_GaussDB
    rm -rf /tmp/GaussDB_driver

    # Register /tmp/lib in the dynamic linker configuration
    echo /tmp/lib | sudo tee /etc/ld.so.conf.d/gauss-libpq.conf
    sudo sed -i '1s|^|/tmp/lib\n|' /etc/ld.so.conf

    # Refresh the dynamic linker cache
    sudo ldconfig

    # Verify libpq is registered, the first line should show the path: 
    # libpq.so.5.5 (libc6,x86-64) => /tmp/lib/libpq.so.5.5
    ldconfig -p | grep pq

Installation from PyPI:

    python3 -m venv test_env
    source test_env/bin/activate
    pip install --upgrade pip
    pip install isort-gaussdb
    pip install gaussdb
    pip install gaussdb-pool
    python -c "import gaussdb; print(gaussdb.__version__)"  # Outputs: 1.0.0.dev2

You can also clone this repository to develop GaussDB::

    # Create a new Python virtual environment in the .venv directory
    python -m venv .venv

    # Activate the virtual environment
    source .venv/bin/activate

    # Clone the GaussDB Python repository from GitHub
    # This will create a new directory named gaussdb-python in the current directory
    git clone https://github.com/HuaweiCloudDeveloper/gaussdb-python.git
    
    # Change into the cloned repository directory
    cd gaussdb-python

Please note that the repository contains the source code of several Python
packages, which may have different requirements:

- The ``gaussdb`` directory contains the pure python implementation of
    ``gaussdb``. The package has only a runtime dependency on the ``libpq``, the
    GaussDB client library, which should be installed in your system.

- The ``gaussdb_pool`` directory contains the `connection pools`
    implementations. This is kept as a separate package to allow a different
    release cycle.

You can create a local virtualenv and install the packages `in
development mode`__, together with their development and testing
requirements::

    # Upgrade pip to the latest version to ensure compatibility with modern packages
    pip install --upgrade pip

    # Install all required dependencies listed in the requirements.txt file
    pip install -r requirements.txt

    # Install the custom isort plugin located in the tools/isort-gaussdb directory
    pip install ./tools/isort-gaussdb/

    # Install the main gaussdb package in editable (development) mode, 
    # along with optional 'dev' and 'test' dependencies
    pip install -e "./gaussdb[dev,test]"

    # Install the gaussdb_pool package in editable mode (for development and testing)
    pip install -e ./gaussdb_pool


.. __: https://pip.pypa.io/en/stable/topics/local-project-installs/#editable-installs

Please add ``--config-settings editable_mode=strict`` to the ``pip install
-e`` above if you experience `editable mode broken`__.

.. __: https://github.com/pypa/setuptools/issues/3557

Now hack away! You can run the tests using on GaussDB::

    # Create a new database named "test" with PostgreSQL compatibility enabled
    gsql -c 'CREATE DATABASE test DBCOMPATIBILITY 'PG' ;'

    # Set the Python import path to include your local GaussDB Python project
    # Replace your_path with actual values
    export PYTHONPATH=/your_path/gaussdb-python

    # Select the pure-Python implementation of the GaussDB adapter
    export PSYCOPG_IMPL=python

    # Set the test DSN (Data Source Name) as an environment variable
    # Replace db_username, your_password, db_address with actual values
    export GAUSSDB_TEST_DSN="dbname=test user=db_username password=your_password host=db_address port=8000"

    # Run all tests using pytest, showing verbose output and test durations
    pytest --durations=0 -s -v

Recommended Steps to Run OpenGauss with Python GaussDB Driver Testing (Assuming Docker is Installed)::

    # Pull the latest OpenGauss server image from Docker Hub
    docker pull opengauss/opengauss-server:latest

    # Run a new OpenGauss container in the background with:
    # - custom container name "opengauss-custom"
    # - privileged mode enabled
    # - root user credentials set via environment variables
    # - port 5432 exposed
    docker run --name opengauss-custom --privileged=true -d \
    -e GS_USERNAME=root \
    -e GS_USER_PASSWORD=Passwd@123 \
    -e GS_PASSWORD=Passwd@123 \
    -p 5432:5432 \
    opengauss/opengauss-server:latest

    # Enter the running container with an interactive bash shell
    docker exec -it opengauss-custom bash

    # Switch to the default OpenGauss database user "omm"
    su - omm

    # Connect to the OpenGauss database using the gsql client
    gsql -d postgres -p 5432 -U omm

    -- Create a new database named "test" with PostgreSQL compatibility enabled
    CREATE DATABASE test DBCOMPATIBILITY 'PG';


    # Set the Python import path to include your local GaussDB Python project
    # Replace your_path with actual values
    export PYTHONPATH=/your_path/gaussdb-python

    # Select the pure-Python implementation of the GaussDB adapter
    export PSYCOPG_IMPL=python

    # Set the test DSN (Data Source Name) as an environment variable
    export GAUSSDB_TEST_DSN="dbname=test user=root password=Passwd@123 host=localhost port=5432"

    # Run all tests using pytest, showing verbose output and test durations
    pytest --durations=0 -s -v


The library includes some pre-commit hooks to check that the code is valid
according to the project coding convention. Please make sure to install them
by running::

    pre-commit install
    pre-commit install-hooks
    pre-commit run --all-files

This will allow to check lint errors before submitting merge requests, which
will save you time and frustrations.

