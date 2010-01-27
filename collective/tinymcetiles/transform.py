import logging
from urlparse import urljoin
from lxml import etree

from repoze.xmliter.serializer import XMLSerializer

from zope.interface import implements
from plone.transformchain.interfaces import ITransform
from plone.app.blocks.utils import resolve

from ZODB.POSException import ConflictError

placeholderXPath = etree.XPath("//img[contains(concat(' ', normalize-space(@class), ' '), ' mceTile ')]")

log = logging.getLogger('collective.tinymcetiles')

class InterpolateTiles(object):
    """Find image tile placeholder and interpolate them
    """
    
    implements(ITransform)
    
    order = 8050
    
    def __init__(self, published, request):
        self.published = published
        self.request = request
    
    def transformString(self, result, encoding):
        return None
    
    def transformUnicode(self, result, encoding):
        return None
    
    def transformIterable(self, result, encoding):
        if not self.request.get('plone.app.blocks.enabled', False) or not isinstance(result, XMLSerializer):
            return None
        
        tree = resolveTiles(self.request, result.tree)
        if tree is None:
            return None
        
        # Set a marker in the request to let subsequent steps know the merging has happened
        self.request['collective.tinymcetiles.merged'] = True
    
        result.tree = tree
        return result


def resolveTiles(request, tree):
    """Given a request and an lxml tree with the body, find all tile
    placehodlers and resolve them to actual tiles.
    """
    
    baseURL = request.getURL()
    
    root = tree.getroot()
    headNode = root.find('head')
    
    toRemove = []
    
    # Find all tile placeholders
    for tilePlaceholderNode in placeholderXPath(tree):
        
        # Get the tile URL, which is in the alt attribute
        tileHref = tilePlaceholderNode.get('alt', None)
        
        if tileHref is not None:
            
            tileHref = urljoin(baseURL, tileHref)
            
            # Render the tile
            try:
                tileTree = resolve(request, tileHref)
            except ConflictError:
                raise
            except Exception:
                log.exception("Could not render tile at %s", tileHref)
                continue
            
            if tileTree is not None:
                
                tileRoot = tileTree.getroot()
                
                # merge tile head into the page's head
                tileHead = tileRoot.find('head')
                if tileHead is not None:
                    for tileHeadChild in tileHead:
                        headNode.append(tileHeadChild)
            
                # insert tile target with tile body
                tileBody = tileRoot.find('body')
                if tileBody is not None:
                    for tileBodyChild in tileBody:
                        tilePlaceholderNode.addnext(tileBodyChild)
                
                toRemove.append(tilePlaceholderNode)
    
    for node in toRemove:
        node.getparent().remove(node)
    
    return tree
