Code Quickstart
===============

The following sections roughly outline the structure of pymunge.

Document Tree
-------------

The most important thing you need to know about pymunge is that almost every building block of the mod files can be referenced as node inside a big tree of documents and folders.
A node can have none to one parent and none to multiple children.
Nodes can also reference other nodes.
Figure :numref:`document_tree` provides a simple examples of how files and their content is represented in pymunge.

.. themed-figure:: ../resource/code/document_tree_light.svg
   :name: document_tree
   :alt: Document tree
   :dark: ../resource/code/document_tree_dark.svg

   Sample representation of folders and files in pymunge.
   Each colored node describes a different content type.
   For example a folder (green) points to another folder by a reference (blue).
   Documents (red) contain the :term:`AST` of the respective format.

In the case of :term:`ODF` files the root node of the document contains the section nodes as children.
Each section node contains several key child nodes.
A key node has exactly one value node.


Diagnostics
-----------

Error handling is done via the central component :class:`~pymunge.app.diagnostic.Diagnostic`.
The class is implemented as a `singleton`_ and initialized by the :class:`~pymunge.app.munger.Munger`.
Therefore, it can be accessed anywhere in the code via the :class:`~pymunge.app.environment.MungeEnvironment`.

A :class:`~pymunge.app.diagnostic.DiagnosticMessage` is made up of a scope, severity, code, and text:

* The **scope** determines the module, class, or topic from which the diagnostic message occurred.
  Examples would be "ODF" or "MSH".
  Scopes are defined during implementation.
* Based on the **severity** (Error, Warning, Info) a diagnostic message might be reported during the munge process.
  A short summary is given at the end of the munge process how many diagnostic messages with different severity levels have occurred.
* The diagnostic **code** is generated automatically during definition time.
  One drawback is that diagnostic numbers may change over time.
  But the big advantage is that diagnostic numbers remain up-to-date with the documentation
* The **text** property is the only dynamic component of the diagnostic message.
  It can be defined during runtime to pin down the problem and tell the user, what went wrong.

An example from the code is given in Listing :numref:`lst-diagnostic-sample`.

.. literalinclude:: ../../../source/pymunge/swbf/parsers/odf.py
   :language: python
   :lines: 57-65
   :linenos:
   :name: lst-diagnostic-sample
   :caption: Sample of how to report a diagnostic message.

.. _singleton: https://en.wikipedia.org/wiki/Singleton_pattern
