Getting Started
===============

Package Structure
-----------------
::

   pycentral
   │   README.md
   │   Contributing.md
   │   ...
   │
   └───pycentral
   │   │   base.py
   │   │   configuration.py
   │   │   ...
   │   │
   │   └───workflows
   │       │   workflows_utils.py
   |       |   ...
   │   
   └───docs
       │   ...
      
   


The ``pycentral`` package is a directory containing files and subdirectories. Contained directly within the top level \
``pycentral`` directory are informative files such as the readme, licensing information, contribution guidelines, and \
release notes. Also contained within the ``pycentral`` package are the subdirectories relevant to the developer, ``pycentral`` \
and ``workflows``. 

pycentral
^^^^^^^^^
The ``pycentral`` subfolder contains the Aruba Central Python modules. Each module contains multiple Python classes. Each Class \
is a representation of some of the Aruba Central's `API Reference category <https://developer.arubanetworks.com/aruba-central/reference>`_. \
Each class has its own function definitions that are used to make a single REST API call. The REST API calls are performed using the \
Python ``requests`` library, which provides functions to make HTTP GET, POST, PUT, PATCH and DELETE requests as supported by Aruba \
Central API Gateway.

In addition to some function definitions for API endpoints listed in `API Reference <https://developer.arubanetworks.com/aruba-central/reference>`_ \
page, there is also a file named ``base.py`` containing function `ArubaCentralBase.command()`. This function can make any REST API call using the API \
endpoint URL, HTTP Method, HTTP query params and HTTP payload as required by an API endpoint.

workflows
^^^^^^^^^
``workflows`` folder contains scripts that combine multiple REST API calls based on function definitions in the ``pycentral`` 
modules to achieve a network automation use-case involving multiple steps or repetitive actions that has to be done in scale. \
Each script contains comments that describe step-by-step the operations being performed. 

Check out the `central-python-workflows <https://github.com/aruba/central-python-workflows>`_ repository for workflows that utilize the Pycentral library. Some of the workflows are - 

1. `Device Provisioning <https://github.com/aruba/central-python-workflows/tree/main/device_provisioning>`_

2. `Device Onboarding <https://github.com/aruba/central-python-workflows/tree/main/device_onboarding>`_

3. `MSP Customer Onboarding <https://github.com/aruba/central-python-workflows/tree/main/msp_customer_onboarding>`_

4. `Inventory to Excel Workflows <https://github.com/aruba/central-python-workflows/tree/main/inventory_to_excel>`_

5. `WLAN Workflows <https://github.com/aruba/central-python-workflows/tree/main/wlan_config>`_

Executing scripts
^^^^^^^^^^^^^^^^^

Refer `Aruba's Developer Hub <https://developer.arubanetworks.com/aruba-central/docs>`_ for the sample scripts written using \
``pycentral`` modules and ``pycentral.workflows`` workflows. 

.. Important:: For more information about Aruba Central and REST APIs visit Aruba Central's page in `Aruba Developer Hub <https://developer.arubanetworks.com>`_.
