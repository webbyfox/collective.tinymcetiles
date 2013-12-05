/**
 * Plone tiles plugin.
 *
 * @author Rob Gietema
 */

/*jshint bitwise:true, curly:true, eqeqeq:true, immed:true, latedef:true,
  newcap:true, noarg:true, noempty:true, nonew:true, plusplus:true,
  undef:true, strict:true, trailing:true, browser:true, evil:true */
/*global define:false */
/*global alert,console:true */


define([
  'jquery',
  'underscore',
  'mockup-patterns-base',
  'mockup-patterns-relateditems',
  'mockup-patterns-modal',
  'tinymce',
  'text!js/patterns/tinymce/templates/upload.xml'
], function($, _, Base, RelatedItems, Modal, tinymce, UploadTemplate) {
  "use strict";



  tinymce.PluginManager.add('plonetiles', function(editor) {
    editor.addButton('plonetiles', {
      icon: 'image',
      tooltip: 'Insert/edit image',
      onclick: editor.settings.addImageClicked,
      stateSelector: 'img:not([data-mce-object])'
    });

    editor.addMenuItem('plonetiles', {
      icon: 'image',
      text: 'Insert image',
      onclick: editor.settings.addImageClicked,
      context: 'insert',
      prependToContext: true
    });
  });


  var TilesModal = Base.extend({
    name: 'uploadmodal',
    defaults: {
      text: {
        uploadHeading: 'Upload Tile',
        file: 'File',
        uploadBtn: 'Upload',
        uploadLocationWarning: 'If you do not select a folder to upload to, ' +
                               "the file will be uploaded to the current folder."
      }
    },
    template: _.template(UploadTemplate),
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
                    var url = this._tiles[i].split('@@')[1].split('/');
                    url = new tinymce.util.URI(ed.settings.document_url).toAbsolute('./@@delete-tile?type=' + url[0] + '&id=' + url[1] + '&confirm=true');

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
    },


    show: function(){
      this.modal.show();
    },
    hide: function(){
      this.modal.hide();
    },
    modalShown: function(){
      var self = this;
      /* initialize elements so submit does the right thing.. */
      self.$uploadBtn = $('.modal-footer input[type="submit"]', self.modal.$modal);
      self.$form = $('form', self.modal.$modal);
      self.$iframe = $('iframe', self.modal.$modal);
      self.$location = $('[name="location"]', self.modal.$modal);
      self.$location.addClass('pat-relateditems').patternRelateditems(self.options.relatedItems);

      self.$form.on('submit', function(e){
        /* handle file upload */
        var locationData = self.$location.select2('data');
        if(locationData.length > 0){
          self.$form.attr('action',
            locationData[0].getURL + '/' + self.options.rel_upload_path);
        }
        self.modal.$loading.show();
        self.$iframe.on('load', function(){
          var response = self.$iframe.contents();
          self.modal.$loading.hide();
          self.hide();
          if (!response.length || !response[0].firstChild) {
            self.tinypattern.fileUploadError();
          }
          response = $(response[0].body).text();
          self.tinypattern.fileUploaded($.parseJSON(response));
        });
        self.$form[0].target = 'upload_target';
      });
      self.$uploadBtn.on('click', function(e){
        e.preventDefault();
        self.$form.trigger('submit');
      });
    },
    reinitialize: function(){
    }
  });

  return TilesModal;

});
