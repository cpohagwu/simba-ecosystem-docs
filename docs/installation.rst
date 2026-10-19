Installation
============

py-simba-pop-tools needs Python 3.11-3.13 and installs
`py-simba-pop <https://pypi.org/project/py-simba-pop/>`_ (0.4.x), numpy,
pandas and scipy.

Releases are compiled wheels for CPython 3.11-3.13 on Windows, macOS and
Linux, with type stubs (``py.typed``) for editors and type checkers. There is
no source distribution.

.. code-block:: bash

   python -m pip install py-simba-pop-tools

The examples read the synthetic farms from a clone of
`py-simba-pop-docs <https://github.com/cpohagwu/py-simba-pop-docs>`_:

.. code-block:: bash

   git clone https://github.com/cpohagwu/py-simba-pop-docs
   export DATA=py-simba-pop-docs/docs/examples/data/synthetic
