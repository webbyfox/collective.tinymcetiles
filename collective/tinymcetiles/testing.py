from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import IntegrationTesting, FunctionalTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import applyProfile
from plone.testing import z2
from plone.testing.z2 import ZSERVER_FIXTURE
from plone.tiles import Tile
from zope.configuration import xmlconfig

import collective.tinymcetiles


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
        import collective.tinymcetiles
        xmlconfig.file('configure.zcml', collective.tinymcetiles,
                       context=configurationContext)
        xmlconfig.string("""\
<configure package="collective.tinymcetiles" xmlns="http://namespaces.plone.org/plone">
    <tile
        name="collective.tinymcetiles.tests.DummyTile"
        title="Dummy tile"
        add_permission="cmf.ModifyPortalContent"
        class=".testing.DummyTile"
        permission="zope2.View"
        />
</configure>
""", context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.tinymcetiles:default')




TILES_FIXTURE = TilesLayer()

TILES_INTEGRATION_TESTING = IntegrationTesting(\
    bases=(TILES_FIXTURE,),
    name="collective.tinymcetiles:Integration")
TILES_FUNCTIONAL_TESTING = FunctionalTesting(\
    bases=(TILES_FIXTURE,),
    name="collective.tinymcetiles:Functional")

TILES_ROBOT_TESTING = z2.FunctionalTesting(
    bases=(TILES_FIXTURE,
           REMOTE_LIBRARY_BUNDLE_FIXTURE,
           ZSERVER_FIXTURE),
    name='collective.tinymcetiles:Robot')


#optionflags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)

