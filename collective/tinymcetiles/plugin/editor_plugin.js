/**
 * Plone tiles plugin.
 *
 * @author Rob Gietema
 */

(function() {
    tinymce.create('tinymce.plugins.PloneTilesPlugin', {
        init : function(ed, url) {

            // Register css
            tinymce.DOM.loadCSS(url + '/++resource++collective.tinymcetiles.plugin/content.css');

            
            // Register commands
            ed.addCommand('mcePloneTiles', function() {
                // Internal image object like a flash placeholder
                if (ed.dom.getAttrib(ed.selection.getNode(), 'class').indexOf('mceItem') != -1)
                    return;

                ed.windowManager.open({
                    file : ed.settings.document_base_url + '/@@available-tiles',
                    width : 820,
                    height : 480,
                    inline : 1
                }, {
                    plugin_url : url
                });
            });

            // Register buttons
            ed.addButton('plonetiles', {
                title : 'Tiles',
                cmd : 'mcePloneTiles'
            });
        },

        getInfo : function() {
            return {
                longname : 'Plone tiles',
                author : 'Rob Gietema',
                authorurl : 'http://plone.org',
                infourl : 'http://plone.org/products/tinymce',
                version : tinymce.majorVersion + "." + tinymce.minorVersion
            };
        }
    });

    // Register plugin
    tinymce.PluginManager.add('plonetiles', tinymce.plugins.PloneTilesPlugin);
})();