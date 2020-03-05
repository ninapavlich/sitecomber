import { SVG } from "@svgdotjs/svg.js";

/*!
 * nina@ninalp.com
 */

// Example Usage
// $(document).ready(function() {
//   $("#sitemap").sitemap();
// });

(function($, window, document, undefined) {
  // Create the defaults once
  var pluginName = "sitemap",
    defaults = {};

  function Node(svg, rootNode, parent, data) {
    this.svg = svg;
    this.rootNode = rootNode ? rootNode : this;
    this.parent = parent;
    this.data = data;
    this.childNodes = [];

    // State:
    this.open = parent ? false : true;

    this.init();
    this.addListeners();
    this.render();
  }

  Node.prototype = {
    init: function() {
      this.container = this.parent
        ? this.parent.container.nested()
        : this.svg.nested();
      this.innerContainer = this.container.nested();

      this.text = this.innerContainer.text(this.data.name);
      this.text.move(0, 0).font({ fill: "#fff", family: "Arial" });
      var textBox = this.text.node.getBBox();
      if (this.data.children.length > 0) {
        this.dot = this.innerContainer
          .circle(10)
          .move(textBox.width + 5, 5)
          .attr({ fill: "#fff" });
      }

      for (var i = 0; i < this.data.children.length; i++) {
        this.childNodes.push(
          new Node(this.svg, this.rootNode, this, this.data.children[i])
        );
      }
    },
    render: function() {
      var color = this.open ? "#17a2b8" : "#fff";
      if (this.dot) {
        this.dot.attr({ fill: color });
      }
      this.text.attr({ fill: color });

      if (this.open || (this.parent && this.parent.open)) {
        if (this.dot) {
          this.dot.addTo(this.container);
        }
        this.text.addTo(this.innerContainer);
      } else {
        if (this.dot) {
          this.dot.remove();
        }
        this.text.remove();
      }

      //Distribute children
      if (this.open === true) {
        var x = this.text.node.getBBox().width + 20;
        var y = 0;
        for (var i = 0; i < this.childNodes.length; i++) {
          const childNode = this.childNodes[i];
          childNode.container.move(x, y);
          childNode.render();
          y += childNode.container.node.getBBox().height;
        }

        this.innerContainer.move(0, y / 2);
      } else {
        for (var i = 0; i < this.childNodes.length; i++) {
          const childNode = this.childNodes[i];
          childNode.render();
        }
        this.innerContainer.move(0, 0);
      }
    },

    addListeners: function() {
      //bind events
      var parent_ref = this;

      this.innerContainer.click(function() {
        // parent_ref.fill({ color: '#f06' })
        parent_ref.open = !parent_ref.open;
        parent_ref.rootNode.render();
      });
    },

    removeListeners: function() {
      //unbind events
    }
  };

  // The actual plugin constructor
  function Sitemap(element, options) {
    this.element = element;

    this.options = $.extend({}, defaults, options);

    this.windows = {};

    this.data = options.data;

    this.init();
  }

  Sitemap.prototype = {
    init: function() {
      this.svg = SVG()
        .addTo(this.element)
        .size(1000, 16 * this.data.children.length);

      this.rootNode = new Node(this.svg, null, null, this.data);
      this.addListeners();

      this.render();
    },

    render: function() {
      this.rootNode.render();
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
  $.fn[pluginName] = function(options) {
    return this.each(function() {
      if (!$.data(this, "plugin_" + pluginName)) {
        $.data(this, "plugin_" + pluginName, new Sitemap(this, options));
      }
    });
  };
})(jQuery, window, document);
