Types
=====

A primary objective of our framework is to simplify its usage for those who wish to employ it without delving into development.
We aim to offer them a straightforward and effortless setup process, minimizing the complexities and initializations associated with numerous classes.
This approach reduces potential bugs and allows users to focus on their primary task: developing an application using our framework.
To ensure uniformity throughout the framework and to effectively manage new Data Pipes while avoiding incorrect class initializations,
we have introduced **Types** identifiers. These identifiers, at a high level, determine the specific type of datapipe required.
Consequently, CHA users are relieved from the intricate details of initializing DataPipe objects, integrating them into the CHA, and handling setups.

Datapipe Types
--------------

This enumeration class defines different types of datapipe. This ensures consistency in case the datapipe developer \
decides to change the name of their datapipe, the end user need not to change their code cause they use the **keys**.
It inherits from the `str` class and the `Enum` class in Python's `enum` module.
Each value in this enumeration represents a specific type of datapipe. The **key** naming convention should be all uppercase with underscore, \
and the **value** naming convention should be underscore_case: `NAME_OF_DATAPIP = this_is_a_sample_datapipe_name`


.. literalinclude:: ../../../../src/openCHA/datapipes/datapipe_types.py
    :language: python


|


Types
-----


This dictionary is used to map each DatapipeType value to its corresponding DataPipe class.
It allows for easy retrieval of the appropriate class based on the datapipe type.


.. literalinclude:: ../../../../src/openCHA/datapipes/types.py
    :language: python
