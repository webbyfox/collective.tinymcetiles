/**
 * Plone tiles plugin.
 *
 * @author Rob Gietema
 */

(function() {
    tinymce.create('tinymce.plugins.PloneTilesPlugin', {
        _tiles : [],
        init : function(ed, url) {

            // Register css
            tinymce.DOM.loadCSS(url + '/++resource++collective.tinymcetiles.plugin/content.css');

            // Register commands
            ed.addCommand('mcePloneTiles', function() {
                // Internal image object like a flash placeholder
                if ((ed.dom.getAttrib(ed.selection.getNode(), 'class').indexOf('mceItem') != -1) &&
                    (ed.dom.getAttrib(ed.selection.getNode(), 'class').indexOf('mceTile') != -1)) {

                    // Get url
                    var url = ed.dom.getAttrib(ed.selection.getNode(), 'alt');
                    url = url.replace(/@@/, '@@edit-tile/');
                    url = new tinymce.util.URI(ed.settings.document_url).toAbsolute(url);
                    
                    // Open add tile menu
                    ed.windowManager.open({
                        file : url,
                        width : 820,
                        height : 480,
                        inline : 1
                    }, {
                        plugin_url : url
                    });
                } else {

                    // Open add tile menu
                    ed.windowManager.open({
                        file : ed.settings.document_url + '/@@add-tile',
                        width : 820,
                        height : 480,
                        inline : 1
                    }, {
                        plugin_url : url
                    });
                }
            });

            // Register buttons
            ed.addButton('plonetiles', {
                title : 'Tiles',
                cmd : 'mcePloneTiles'
            });

            ed.onChange.add(this._change, this);
            ed.onInit.add(this._init, this);
        },

        _init : function(ed) {
            var curtiles = ed.dom.select('.mceTile');
            for (var i = 0; i < curtiles.length; i++) {
                this._tiles.push(ed.dom.getAttrib(curtiles[i], 'alt'));
            }
        },

        _change : function(ed, l) {
            var curtilesdom = ed.dom.select('.mceTile');
            var curtiles = [];
            for (var i = 0; i < curtilesdom.length; i++) {
                curtiles.push(ed.dom.getAttrib(curtilesdom[i], 'alt'));
            }
            for (var i = 0; i < this._tiles.length; i++) {
                if (curtiles.indexOf(this._tiles[i]) == -1) {

                    // Get delete url
                    var url = this._tiles[i].replace(/@@/, '@@delete-tile/');
                    url = new tinymce.util.URI(ed.settings.document_url).toAbsolute(url);

                    // Do ajax call
                    tinymce.util.XHR.send({
                        url : url
                    });
                }
            }
            this._tiles = curtiles;
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