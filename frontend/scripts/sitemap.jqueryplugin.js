/*!
 * nina@ninalp.com
 */


;(function ( $, window, document, undefined ) {

    // Create the defaults once
    var pluginName = "sitemap",
        defaults = {
            
        };

    // The actual plugin constructor
    function Sitemap( element, options ) {
        this.element = element;

        this.options = $.extend( {}, defaults, options) ;
        

        this.windows = {};

        this.init();
    }

    Sitemap.prototype = {

        init: function() {

            return;
            
            this.canvas = document.createElement('canvas');
            this.canvas.id = "SitemapCanvas";
            this.canvas.width = 768;
            this.canvas.height = 768;
            this.element.appendChild(this.canvas);

            this.ctx = this.canvas.getContext("2d");
            this.ctx.fillStyle = "rgba(255, 0, 0, 0.2)";
            this.ctx.fillRect(100, 100, 200, 200);
            this.ctx.fillStyle = "rgba(0, 255, 0, 0.2)";
            this.ctx.fillRect(150, 150, 200, 200);
            this.ctx.fillStyle = "rgba(0, 0, 255, 0.2)";
            this.ctx.fillRect(200, 50, 200, 200);
            

            this.addListeners()
          

            this.render()
        },

        
       
        render: function() {
            this.renderPositionDots();
            this.renderLines();
        },


        renderPositionDots: function() {

        },
        renderLines: function() {

        },

        addListeners: function() {
            //bind events
            var parent_ref = this;

            
        },

        removeListeners: function() {
            //unbind events           
        }

    };

    // A really lightweight plugin wrapper around the constructor,
    // preventing against multiple instantiations
    $.fn[pluginName] = function ( options ) {
        return this.each(function () {
            if (!$.data(this, "plugin_" + pluginName)) {
                $.data(this, "plugin_" + pluginName,
                new Sitemap( this, options ));
            }
        });
    };

})( jQuery, window, document );

//$( document ).ready(function() {
//  $(".selector").pluginName();
//});


