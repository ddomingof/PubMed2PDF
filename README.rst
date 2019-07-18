PubMed2PDF
==========

A Python package to download PDFs from OA publications in PubMed. The underlying code is forked from
https://github.com/billgreenwald/Pubmed-Batch-Download. Downloaded files are located  by default in your personal folder under the 'pubmed2pdf' directory.


Installation
------------
``pubmed2pdf`` can be installed from `PyPI <https://pypi.org/project/pubmed2pdf>`_
with the following command in your terminal:

.. code-block:: sh

    $ python3 -m pip install pubmed2pdf

The latest code can be installed from `GitHub <https://github.com/ddomingof/PubMed2PDF>`_
with:

.. code-block:: sh

    $ python3 -m pip install git+https://github.com/ddomingof/PubMed2PDF.git

For developers, the code can be installed with:

.. code-block:: sh

    $ git clone https://github.com/ddomingof/PubMed2PDF.git
    $ cd PubMed2PDF
    $ python3 -m pip install -e .

How to Use
----------

PubMed2PDF works by simply typing the list of PubMed identifiers in your command line interface or reading them from a
file.

Example from file:

.. code-block:: sh

    $ python3 -m pubmed2pdf pdf --pmidsfile="/my/path/to/the/file"

.. code-block:: sh

    $ python3 -m pubmed2pdf pdf --pmids="123, 1234, 12345"

Run the help command to see all functionalities

.. code-block:: sh

    $ python3 -m pubmed2pdf pdf --help
