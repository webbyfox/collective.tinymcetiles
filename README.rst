.. contents::

.. image:: https://secure.travis-ci.org/collective/collective.tinymcetiles.png
    :target: http://travis-ci.org/collective/collective.tinymcetiles


Introduction
============

``collective.tinymcetiles`` is a Plone 4 add-on that provides a TinyMCE plugin
that allows authors to insert *tiles* into the page. Tiles may be
configured prior to insertion, and edited thereafter, using a new toolbar
button in Plone's TinyMCE editor.

On the edit screen, a tile is shown as a placeholder image. When the page
is rendered, this placeholder will be replaced by the rendered tile. If
there is an error rendering the tile, the placeholder image will remain,
and an exception will be recorded in the Zope error log.

Installation
============

Add ``collective.tinymcetiles`` to your buildout in the ``eggs`` list, or
as a dependency in the ``install_requires`` list in the ``setup.py`` file
for a product that is already installed in your build. The package's
configuration is loaded automatically by Plone.

You must also install the product in Plone's Add-on control panel.

Usage
=====

Use the new Tiles button to insert and edit tiles.

More about tiles
=================

Tiles are a lightweight alternative to portlets. They are easy to write and
fast to render, and unlike portlets they can easily be inserted into the body
text of a page, using this package (if you want to insert a tile in the left
or right hand side column, you can add one inside a static text portlet).

To learn more about tiles, see:

* `plone.tiles`_, for the basics
* `plone.directives.tiles`_ for convention-over-configuration based tile
  configuration
* `plone.app.tiles`_, for details about creating custom tile add and edit
  forms

.. _plone.tiles: http://pypi.python.org/pypi/plone.tiles
.. _plone.directives.tiles: http://pypi.python.org/pypi/plone.directives.tiles
.. _plone.app.tiles: http://pypi.python.org/pypi/plone.app.tiles
