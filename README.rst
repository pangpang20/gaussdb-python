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

    python -c "import gaussdb; print(gaussdb.__version__)"
    # Outputs: 1.0.0.dev2

    # Run demo
    python ./example/demo.py

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

    # Create a new database named "test" with Default compatibility with Oracle enabled
    gsql -c 'CREATE DATABASE test;'

    # Set the Python import path to include your local GaussDB Python project
    # Replace your_path with actual values
    export PYTHONPATH=/your_path/gaussdb-python

    # Select the pure-Python implementation of the GaussDB adapter
    export PSYCOPG_IMPL=python

    # Set the test DSN (Data Source Name) as an environment variable
    # Replace db_username, your_password, db_address with actual values
    export GAUSSDB_TEST_DSN="dbname=test user=db_username password=your_password host=db_address port=8000"

    # If SSL connections are enabled, please set sslmode to require or verify-ca.
    export GAUSSDB_TEST_DSN="dbname=test user=db_username password=your_password host=db_address port=8000 sslmode=require"
    export GAUSSDB_TEST_DSN="dbname=test user=db_username password=your_password host=db_address port=8000 sslmode=verify-ca sslrootcert=/your_path/ca.pem" 


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

    -- Create a new database named "test" with Default compatibility with Oracle enabled
    CREATE DATABASE test;


    # Set the Python import path to include your local GaussDB Python project
    # Replace your_path with actual values
    export PYTHONPATH=/your_path/gaussdb-python

    # Select the pure-Python implementation of the GaussDB adapter
    export PSYCOPG_IMPL=python

    # Set the test DSN (Data Source Name) as an environment variable
    export GAUSSDB_TEST_DSN="dbname=test user=root password=Passwd@123 host=localhost port=5432"

    # Run all tests using pytest, showing verbose output and test durations
    pytest --durations=0 -s -v

Steps to Run OpenGauss(SSL) with Python GaussDB Driver Testing (Assuming Docker is Installed)::

    # Create certificate directory
    mkdir -p /opengauss8889/certs
    cd /opengauss8889/certs

    # Generate CA certificate
    openssl genrsa -out ca.key 4096
    openssl req -x509 -new -nodes -key ca.key -sha256 -days 3650 \
    -subj "/C=CN/ST=OpenGauss/L=OpenGauss/O=MyOrg/OU=DB/CN=OpenGaussCA" \
    -out ca.crt

    # Generate server certificate
    openssl genrsa -out server.key 2048
    openssl req -new -key server.key \
    -subj "/C=CN/ST=OpenGauss/L=OpenGauss/O=MyOrg/OU=DB/CN=opengauss.local" \
    -out server.csr

    # SAN config (replace IP/DNS with the address you will use to connect,
    # for example 127.0.0.1 or the host IP)
    cat > san.cnf <<EOF
    [ req ]
    default_bits = 2048
    distinguished_name = req_distinguished_name
    req_extensions = req_ext
    [ req_distinguished_name ]
    [ req_ext ]
    subjectAltName = @alt_names
    [ alt_names ]
    DNS.1 = opengauss.local
    IP.1 = 127.0.0.1
    EOF

    # Sign the server certificate with the CA, including SAN
    openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
    -out server.crt -days 730 -sha256 -extfile san.cnf -extensions req_ext

    # Optional: client certificate (for mutual TLS)
    openssl genrsa -out client.key 2048
    openssl req -new -key client.key -subj "/CN=root" -out client.csr
    openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
    -out client.crt -days 730 -sha256

    # Create configuration directory
    mkdir -p /opengauss8889/conf
    cat > /opengauss8889/conf/postgresql.conf <<EOF
    max_connections = 200			# (change requires restart)
    session_timeout = 10min			# allowed duration of any unused session, 0s-86400s(1 day), 0 is disabled
    bulk_write_ring_size = 2GB		# for bulkload, max shared_buffers
    max_prepared_transactions = 200		# zero disables the feature
    cstore_buffers = 512MB         #min 16MB
    enable_incremental_checkpoint = on	# enable incremental checkpoint
    incremental_checkpoint_timeout = 60s	# range 1s-1h
    enable_double_write = on		# enable double write
    wal_keep_segments = 16		# in logfile segments, 16MB each normal, 1GB each in share storage mode; 0 disables
    enable_slot_log = off
    synchronous_standby_names = '*'	# standby servers that provide sync rep
    walsender_max_send_size = 8MB  # Size of walsender max send size
    hot_standby = on			# "on" allows queries during recovery
    enable_kill_query = off			# optional: [on, off], default: off
    logging_collector = on   		# Enable capturing of stderr and csvlog
    log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'	# log file name pattern,
    log_file_mode = 0600			# creation mode for log files,
    log_rotation_size = 20MB		# Automatic rotation of logfiles will
    log_min_duration_statement = 1800000	# -1 is disabled, 0 logs all statements
    log_connections = off			# log connection requirement from client
    log_disconnections = off		# log disconnection from client
    log_duration = off			# log the execution time of each query
    log_hostname = off			# log hostname
    log_line_prefix = '%m %u %d %h %p %S '	# special values:
    log_timezone = 'UCT'
    enable_alarm = on
    connection_alarm_rate = 0.9
    alarm_report_interval = 10
    alarm_component = '/opt/snas/bin/snas_cm_cmd'
    use_workload_manager = on		# Enables workload manager in the system.
    datestyle = 'iso, mdy'
    timezone = 'UCT'
    lc_messages = 'en_US.utf8'			# locale for system error message
    lc_monetary = 'en_US.utf8'			# locale for monetary formatting
    lc_numeric = 'en_US.utf8'			# locale for number formatting
    lc_time = 'en_US.utf8'				# locale for time formatting
    default_text_search_config = 'pg_catalog.english'
    lockwait_timeout = 1200s		# Max of lockwait_timeout and deadlock_timeout +1s
    pgxc_node_name = 'gaussdb'			# Coordinator or Datanode name
    audit_enabled = on
    job_queue_processes = 10        # Number of concurrent jobs, optional: [0..1000], default: 10.
    dolphin.nulls_minimal_policy = on # the inverse of the default configuration value ! do not change !
    password_encryption_type = 0
    wal_level = logical
    application_name = ''
    listen_addresses = '*'
    max_replication_slots = 10
    max_wal_senders = 10
    shared_buffers = 512MB
    ssl = on
    ssl_cert_file = '/var/lib/opengauss/certs/server.crt'
    ssl_key_file = '/var/lib/opengauss/certs/server.key'
    ssl_ca_file = '/var/lib/opengauss/certs/ca.crt'
    EOF

    cat > /opengauss8889/conf/postgresql.conf <<EOF
    local   all             all                                     trust
    host    all             all             127.0.0.1/32            trust
    host    all             all             ::1/128                 trust
    host all all 0.0.0.0/0 md5
    hostssl all all 0.0.0.0/0 cert
    host replication gaussdb 0.0.0.0/0 md5
    EOF


    # Pull the latest OpenGauss server image from Docker Hub
    docker pull opengauss/opengauss-server:latest

    # Run a new OpenGauss container in the background with:
    # - custom container name "opengauss-custom"
    # - privileged mode enabled
    # - root user credentials set via environment variables
    # - port 5432 exposed
    docker run --name opengauss-cp --privileged=true -d \
    -e GS_USERNAME=root \
    -e GS_USER_PASSWORD=Password@123 \
    -e GS_PASSWORD=Password@123 \
    -p 8889:5432 \
    -v /opengauss8889:/var/lib/opengauss \
    -v /opengauss8889/certs:/var/lib/opengauss/certs \
    -v /opengauss8889/conf/postgresql.conf:/var/lib/opengauss/data/postgresql.conf \
    -v /opengauss8889/conf/pg_hba.conf:/var/lib/opengauss/data/pg_hba.conf \
    opengauss/opengauss-server:latest

    
    # Enter the container shell
    docker exec -it opengauss-cp bash

    # Confirm the data directory (in some images it may be /var/lib/opengauss/data)
    # Assume the data directory is /var/lib/opengauss/data
    DATA_DIR=/var/lib/opengauss/data
    # Find the owner (username) of the data directory
    OWNER=$(stat -c '%U' "$DATA_DIR" 2>/dev/null || echo omm)

    # Set proper permissions for the key files and change ownership to the data directory owner
    chown "$OWNER":"$OWNER" /var/lib/opengauss/certs/*
    chmod 600 /var/lib/opengauss/certs/*

    # Verify the files
    ls -l /var/lib/opengauss/certs

    # Exit the container
    exit

    # Restart the container to apply changes
    docker restart opengauss-cp

    # ReEnter the container
    docker exec -it opengauss-cp bash

    # Switch to the default OpenGauss database user "omm"
    su - omm

    # Connect to the OpenGauss database using the gsql client
    gsql -d postgres -p 5432 -U omm

    -- Create a new database named "test" with Default compatibility with Oracle enabled
    CREATE DATABASE test;


    # Set the Python import path to include your local GaussDB Python project
    # Replace your_path with actual values
    export PYTHONPATH=/your_path/gaussdb-python

    # Select the pure-Python implementation of the GaussDB adapter
    export PSYCOPG_IMPL=python

    # Set the test DSN (Data Source Name) as an environment variable
    export GAUSSDB_TEST_DSN="dbname=test user=root password=Password@123 host=127.0.0.1 port=8889 sslmode=require" 
    export GAUSSDB_TEST_DSN="dbname=test user=root password=Password@123 host=127.0.0.1 port=8889 sslmode=verify-ca sslrootcert=/opengauss8889/certs/ca.crt sslcert=/opengauss8889/certs/client.crt sslkey=/opengauss8889/certs/client.key"

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

