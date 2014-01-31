import logging
from urlparse import urljoin
from lxml.html import builder as E
from repoze.xmliter.serializer import XMLSerializer
from zope.interface import implements
from plone.transformchain.interfaces import ITransform
from plone.app.blocks import utils
from ZODB.POSException import ConflictError

log = logging.getLogger('collective.tinymcetiles')


class InterpolateTiles(object):
    """Find image tile placeholder and interpolate them
    """

    implements(ITransform)

    order = 8850

    def __init__(self, published, request):
        self.published = published
        self.request = request

    def transformString(self, result, encoding):
        return None

    def transformUnicode(self, result, encoding):
        return None

    def transformIterable(self, result, encoding):
        if not self.request.get('plone.app.blocks.enabled',
                                False) or not isinstance(result, XMLSerializer):
            return None

        tree = resolveTiles(self.request, result.tree)
        if tree is None:
            return None

        result.tree = tree

        # Set a marker in the request to let subsequent steps know the merging has happened
        self.request['collective.tinymcetiles.merged'] = True

        return result


def resolveTiles(request, tree):
    """Given a request and an lxml tree with the body, find all tile
    placehodlers and resolve them to actual tiles.
    """

    #renderView = None
    #renderedRequestKey = None

    # Optionally enable ESI rendering
    #registry = queryUtility(IRegistry)
    #if registry is not None:
    #    if registry.forInterface(IBlocksSettings).esi:
    #        renderView = 'plone.app.blocks.esirenderer'
    #        renderedRequestKey = 'plone.app.blocks.esi'

    baseURL = request.getURL()

    root = tree.getroot()
    headNode = root.find('head')

    # Find all tile placeholders
    for tilePlaceholderNode in root.cssselect("img.mceTile"):

        try:
            tileHref = tilePlaceholderNode.get('alt', None)
            if not tileHref:
                log.error("Could not render tile at %s", tileHref)
                continue
            tileHref = urljoin(baseURL, tileHref)
            tileTree = utils.resolve(tileHref)

            resolveTile(tilePlaceholderNode, tileHref, tileTree, headNode)
        except ConflictError:
            raise
        except Exception:
            log.exception("Could not render tile at %s", tileHref)
            continue

    return tree


def resolveTile(tilePlaceholderNode, tileHref, tileTree, headNode):
    # Get the tile URL, which is in the alt attribute

    if tileTree is None:
        return

    # merge tile head into the page's head
    tileHead = tileTree.find('head')
    if tileHead is not None:
        for tileHeadChild in tileHead:
            headNode.append(tileHeadChild)

    # insert tile target with tile body
    tileBody = tileTree.find('body')
    if tileBody is not None:

        # Preserve text
        if tileBody.text:
            tileTextSpan = E.SPAN()
            tileTextSpan.text = tileBody.text
            tilePlaceholderNode.addnext(tileTextSpan)

        # Copy other nodes
        for tileBodyChild in tileBody:
            tilePlaceholderNode.addnext(tileBodyChild)

    tilePlaceholderNode.getparent().remove(tilePlaceholderNode)
