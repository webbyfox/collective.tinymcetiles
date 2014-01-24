from plone.app.testing import setRoles, TEST_USER_ID, TEST_USER_NAME, login
import transaction
import unittest2 as unittest

from zope.component import getUtility

from plone.tiles.tile import Tile

from Products.CMFCore.utils import getToolByName
from Products.TinyMCE.interfaces.utility import ITinyMCE
from collective.tinymcetiles.testing import TILES_FUNCTIONAL_TESTING, TILES_INTEGRATION_TESTING
from plone.testing.z2 import Browser


class IntegrationTestCase(unittest.TestCase):
    
    layer = TILES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

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

        self.portal.invokeFactory('Folder', 'test-folder')
        self.folder = self.portal['test-folder']
        self.folder.invokeFactory('Document', 'd1')
        self.folder['d1'].setTitle(u"New title")
        self.folder['d1'].setText(u"""\
<p>
    <img
        src="/++resource++collective.tinymcetiles.plugin/placeholder.gif"
        alt="./@@dummy.tile/tile-1"
        class="mceItem mceTile"
        />
</p>
""")
        self.folder['d1'].getField('text').setContentType(self.folder['d1'], "text/html")

#        pw = getToolByName(self.portal, 'portal_workflow')
#        pw.doActionFor(self.folder['d1'], 'publish')
        transaction.commit()

        browser = Browser(self.portal)
        browser.handleErrors = False
        
        browser.open(self.folder['d1'].absolute_url())
        self.failUnless("Test tile rendered" in browser.contents)
        self.failUnless("<p>With child tags</p>" in browser.contents)
        self.failUnless("And tail text" in browser.contents)

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
