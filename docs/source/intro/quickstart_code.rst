Code Quickstart
=======================

The most important thing you need to know about pymunge is that almost every building block of the mod files can be referenced as node inside a big tree of documents and folders.
A node can have none to one parent and none to multiple children.
Nodes can also reference other nodes.
Figure :numref:`document_tree` provides a simple examples of how files and their content is represented in pymunge.

.. figure:: ../resource/code/document_tree.svg
   :name: document_tree
   :alt: Document tree

   Sample representation of folders and files in pymunge.
   Each colored node describes a different content type.
   For example a folder (green) points to another folder by a reference (blue).
   Files (red) contain the :term:`AST` of the respective format.

