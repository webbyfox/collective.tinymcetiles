import unittest2 as unittest
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import applyProfile
from zope.configuration import xmlconfig

import collective.tinymcetiles

from zope.component import getUtility

from plone.tiles.tile import Tile

from Products.Five.testbrowser import Browser
from Products.CMFCore.utils import getToolByName
from Products.TinyMCE.interfaces.utility import ITinyMCE

class DummyTile(Tile):
    
    def __call__(self):
        return u"""\
<html>
<body>Test tile rendered<p>With child tags</p>And tail text</body>
</html>
"""


class TilesLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML for this package
        import plone.tiles
#        xmlconfig.file('meta.zcml', plone.tiles,
#                       context=configurationContext)
#        import collective.tinymcetiles
#        xmlconfig.file('configure.zcml', collective.tinymcetiles,
#                       context=configurationContext)
        xmlconfig.string("""\
<configure package="collective.tinymcetiles" xmlns="http://namespaces.plone.org/plone">
    <include package="zope.component" file="meta.zcml" />
    <include package="zope.security" file="meta.zcml" />
    <include package="zope.app.publisher" file="meta.zcml" />
    <include package="zope.i18n" file="meta.zcml" />
    <include package="Products.Five" file="meta.zcml" />
    <include package="collective.tinymcetiles"  />
    <tile
        name="collective.tinymcetiles.tests.DummyTile"
        title="Dummy tile"
        add_permission="cmf.ModifyPortalContent"
        class=".tests.DummyTile"
        permission="zope2.View"
        />
</configure>
""")

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.tinymcetiles:default')

FIXTURE = TilesLayer()
INTEGRATION_TESTING = \
    IntegrationTesting(bases=(FIXTURE, ),
                       name="CollectiveTinyMCETiles:Integration")

class IntegrationTestCase(unittest.TestCase):
    
    layer = INTEGRATION_TESTING
    
    def test_dependencies_installed(self):
        qi = getToolByName(self.portal, 'portal_quickinstaller')
        self.failUnless(qi.isProductInstalled('plone.app.blocks'))
        self.failUnless(qi.isProductInstalled('plone.app.tiles'))
    
    def test_js_installed(self):
        pj = getToolByName(self.portal, 'portal_javascripts')
        self.failUnless('++resource++collective.tinymcetiles.plugin/event.js' in pj.getResourceIds())
    
    def test_tinymce_configured(self):
        tinymce = getUtility(ITinyMCE)
        self.failUnless('plonetiles|/++resource++collective.tinymcetiles.plugin/editor_plugin.js' in tinymce.customplugins)
        self.failUnless('plonetiles' in tinymce.customtoolbarbuttons)
    
    def test_tile_rendering(self):
        self.setRoles(('Manager',))
        
        self.folder.invokeFactory('Document', 'd1')
        self.folder['d1'].setTitle(u"New title")
        self.folder['d1'].setText(u"""\
<p>
    <img
        src="/++resource++collective.tinymcetiles.plugin/placeholder.gif"
        alt="./@@collective.tinymcetiles.tests.DummyTile/tile-1"
        class="mceItem mceTile"
        />
</p>
""")
        self.folder['d1'].getField('text').setContentType(self.folder['d1'], "text/html")
        
        pw = getToolByName(self.portal, 'portal_workflow')
        pw.doActionFor(self.folder['d1'], 'publish')
        
        browser = Browser()
        browser.handleErrors = False
        
        browser.open(self.folder['d1'].absolute_url())
        self.failUnless("Test tile rendered" in browser.contents)
        self.failUnless("<p>With child tags</p>" in browser.contents)
        self.failUnless("And tail text" in browser.contents)

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
