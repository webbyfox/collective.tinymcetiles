import copy
import logging
from urlparse import urljoin
from lxml import etree, html

from repoze.xmliter.serializer import XMLSerializer

from zope.interface import implements
from plone.transformchain.interfaces import ITransform
from plone.tiles.interfaces import IESIRendered
from plone.app.blocks.utils import cloneRequest, traverse, invoke, extractCharset

from AccessControl import Unauthorized
from ZODB.POSException import ConflictError
from zExceptions import NotFound

log = logging.getLogger('collective.tinymcetiles')

class InterpolateTiles(object):
    """Find image tile placeholder and interpolate them
    """
    
    implements(ITransform)
    
    order = 8950
    
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
        
        result.tree = tree
        
        # Set a marker in the request to let subsequent steps know the merging has happened
        self.request['collective.tinymcetiles.merged'] = True
        
        # We may need to do some string post-processing unforunately, because
        # the ESI tag won't self-close properly in HTML rendering mode.
        
        if self.request.get('collective.tinymcetiles.esi', False):
            consumed = u"".join(result).replace(u"></esi:include>", u'/>')
            result = consumed
        
        return result

def resolveTiles(request, tree):
    """Given a request and an lxml tree with the body, find all tile
    placehodlers and resolve them to actual tiles.
    """
    
    esiUsed = False
    nsmap = {'esi': 'http://www.edge-delivery.org/esi/1.0'}
    
    baseURL = request.getURL()
    
    root = tree.getroot()
    headNode = root.find('head')
    
    # Find all tile placeholders
    for tilePlaceholderNode in root.cssselect("img.mceTile"):
        
        try:
            
            # Get the tile URL, which is in the alt attribute
            tileHref = tilePlaceholderNode.get('alt', None)
            
            if tileHref is not None:
                
                tileHref = urljoin(baseURL, tileHref)
                
                requestClone = cloneRequest(request, tileHref)
                path = '/'.join(requestClone.physicalPathFromURL(tileHref.split('?')[0]))
                
                esi = False
                resolved = None
                
                try:
                    traversed = traverse(requestClone, path)
                    if IESIRendered.providedBy(traversed):
                        esi = True
                    else:
                        resolved = invoke(requestClone, traversed)
                except (NotFound, Unauthorized,):
                    log.exception("Could not resolve tile with URL %s" % tileHref)
                    requestClone.close()
                    raise
                
                charset = extractCharset(requestClone.response)
                requestClone.close()
                
                if esi:
                    esiNode = etree.Element("{%s}include" % nsmap['esi'], nsmap=nsmap)
                    
                    if '?' in tileHref:
                        tileURL, tileQueryString = tileHref.split('?')
                        esiNode.set('src', "%s/@@esi-body?%s" % (tileURL, tileQueryString,))
                    else:
                        esiNode.set('src', "%s/@@esi-body" % tileHref)
                    tilePlaceholderNode.getparent().replace(tilePlaceholderNode, esiNode)
                    esiUsed = request['collective.tinymcetiles.esi'] = True
                elif resolved is not None:
                    
                    # Parse the tile HTML and merge it into the page
                    parser = html.HTMLParser()
                    
                    if isinstance(resolved, unicode):
                        parser.feed(resolved)
                    elif isinstance(resolved, str):
                        parser.feed(resolved.decode(charset))
                    
                    tileRoot = parser.close()
                    
                    if tileRoot is not None:
                        
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
                        
                        tilePlaceholderNode.getparent().remove(tilePlaceholderNode)
                else:
                    log.error("Could not render tile at %s", tileHref)

        except ConflictError:
            raise
        except Exception:
            log.exception("Could not render tile at %s", tileHref)
            continue
    
    if esiUsed:
        # Add the xmlns:esi to the root
        newRoot = etree.XML('%s\n<html %s/>' % (tree.docinfo.doctype,
                " ".join(['xmlns:%s="%s"' % (k,v) for k,v in nsmap.items()]),
            ))
        newRoot.attrib.update(root.attrib.items())
        newRoot[:] = copy.deepcopy(root)[:]
        tree._setroot(newRoot)
        
        
    return tree
