import { SVG } from "@svgdotjs/svg.js";

/*!
 * nina@ninalp.com
 *
 *  TODO List:
 * - Add lines between connections
 * - Add ability to visualize links VS hierarchy
 * - Fix linking so you can click on a link without clicking on the node
 * - Fix upside down text in ring 2
 * - Add error indicators
 * - Have H1 link to page detail
 * - Add the ability to deep link to a selection to assist with preserving state
 *
 */

// Example Usage
// $(document).ready(function() {
//   $("#sitemap").sitemap();
// });

(function($, window, document, undefined) {
  // Create the defaults once
  var pluginName = "sitemap",
    defaults = {};

  function Node(sitemap, parentNode, data) {
    this.sitemap = sitemap;
    this.parentNode = parentNode;
    this.data = data;
    this.inited = false;

    this.id = this.data.full_url;
    this.isSite = this.data.full_path === "/";
    this.isPage = this.data.url !== null;
    this.isPath = this.data.url === null;
    this.isLeaf = this.data.children.length === 0;

    this.markupNeedsRender = true;
    this.hierarchicalChildren = [];
    if (this.parentNode) {
      this.parentNode.registerHierarchicalChild(this);
    }

    this.init();
    this.addListeners();
    this.render();
  }

  Node.prototype = {
    init: function() {
      if (this.inited === true) {
        return;
      }
      this.inited = true;

      this.view = document.createElement("div");
      $(this.view).addClass("node");
      $(this.view).addClass(
        this.isSite ? "site" : this.isPage ? "page" : "path"
      );
      if (this.isLeaf) {
        $(this.view).addClass("leaf");
      }
    },
    registerHierarchicalChild: function(child) {
      this.hierarchicalChildren.push(child);
    },

    // getHierarchicalRelationships: function() {
    //   var items = this.hierarchicalChildren.map(function(child) {
    //     return { relationship: "child", node: child };
    //   });
    //   if (this.parentNode) {
    //     items.push({
    //       relationship: "parent",
    //       node: this.parentNode
    //     });
    //   }
    //   return items;
    // },
    populateHierarchicalRelationships: function(currentRing, ringMap) {
      if (ringMap.ids.includes(this.id)) {
        return;
      }

      //assuming I am on the currentRing, add all my children to the next layer out. unless they are already in the ring?
      ringMap.ids.push(this.id);
      if (!ringMap[currentRing]) {
        ringMap[currentRing] = [];
      }
      ringMap[currentRing].push(this);
      for (var i = 0; i < this.hierarchicalChildren.length; i++) {
        var child = this.hierarchicalChildren[i];
        child.populateHierarchicalRelationships(currentRing + 1, ringMap);
      }

      if (this.parentNode) {
        this.parentNode.populateHierarchicalRelationships(
          currentRing + 1,
          ringMap
        );
      }
    },

    render: function() {
      this.renderMarkup();
    },
    renderMarkup: function() {
      if (this.markupNeedsRender === false) {
        return;
      }
      this.view.innerHTML = this.getMarkup();
      this.markupNeedsRender = false;
    },
    getMarkup: function() {
      var html = "<span class='flag bg-info text-light'>";

      var label = this.isSite ? this.data.url : "/" + this.data.path + "/";
      html += "<h1>" + label + "</h1>";
      html +=
        "<h2><a href='" +
        this.data.full_url +
        "' target='_blank' text='Open in new tab'>" +
        this.data.full_url +
        "</a></h2>";
      html +=
        this.data.children.length === 0
          ? ""
          : this.data.children.length == 1
          ? "<p>1 child</p>"
          : "<p>" + this.data.children.length + " children</p>";

      html += "</span>";

      html += "<span class='flag-rotated text-light'><h1>" + label + "</h1></span>";
      return html;
    },

    addListeners: function() {},

    removeListeners: function() {
      //unbind events
    }
  };

  // The actual plugin constructor
  function Sitemap(element, options) {
    this.element = element;
    this.containerWidth = $(this.element).width();
    this.containerHeight = $(this.element).height();

    this.options = $.extend({}, defaults, options);

    this.windows = {};

    this.data = options.data;
    this.inited = false;
    this.resize_timeout = -1;

    this.init();
  }

  Sitemap.prototype = {
    init: function() {
      if (this.inited === true) {
        return;
      }
      this.inited = true;

      this.view = document.createElement("div");
      this.element.append(this.view);

      this.allNodes = [];

      this.activeNode = this.rootNode = this.initNode(this.data, null);

      for (var i = 0; i < this.allNodes.length; i++) {
        var node = this.allNodes[i];
        this.view.append(node.view);
      }

      this.addListeners();

      this.render();
    },
    initNode: function(data, parentNode) {
      var node = new Node(this, parentNode, data);

      var ref = this;
      $(node.view).click(function() {
        ref.onNodeClicked(node);
      });

      this.allNodes.push(node);

      for (var i = 0; i < data.children.length; i++) {
        var child = data.children[i];
        this.allNodes.push(this.initNode(child, node));
      }
      return node;
    },
    render: function() {
      //Update all the markup within the nodes
      for (var i = 0; i < this.allNodes.length; i++) {
        var node = this.allNodes[i];
        node.render();
      }

      var ringMap = { ids: [] };
      this.activeNode.populateHierarchicalRelationships(0, ringMap);
      this.distributeRings(ringMap);
      // this.distributeRings([
      //   { items: [{ relationship: "root", node: this.activeNode }] },
      //   { items: firstDegreeRelationships }
      // ]);
    },

    onNodeClicked: function(node) {
      this.activeNode = node;
      this.render();
    },

    /**
     * Given a map in this shape:
     * {'ids':[], '0':[], '1':[], ... 'n': []}
     *
     * Distribute these nodes into a set of rings, where the item in the 0th
     * place is at the center, and the items in the nth place are in the outer
     * most ring
     */
    distributeRings: function(ringMap) {
      var rings = [];
      var ctr = 0;
      while (ringMap[ctr]) {
        rings.push(ringMap[ctr]);
        ctr += 1;
      }
      var w = this.containerWidth;
      var h = this.containerHeight;

      var centerX = w / 2;
      var centerY = h / 2;
      var runningRadius = 0;
      var addWobble = false;

      console.log("Ring map", ringMap);
      console.log("going to distribute items into " + rings.length + " rings");

      for (var i = 0; i < rings.length; i++) {
        // console.log(
        //   "Ring " +
        //     i +
        //     " has " +
        //     rings[i].length +
        //     " items. Current radius is " +
        //     runningRadius
        // );
        var ring = rings[i];
        var radius = runningRadius;
        var thetaStep = (Math.PI * 2) / ring.length;
        var currentTheta = 0;
        var wobbleTheta = 0;
        for (var m = 0; m < ring.length; m++) {
          var item = ring[m];
          var node = item;
          var view = node.view;
          var wobbleX = addWobble
            ? Math.cos(currentTheta) * 75 * Math.sin(wobbleTheta)
            : 0;
          var wobbleY = addWobble
            ? Math.sin(currentTheta) * 75 * Math.cos(wobbleTheta)
            : 0;
          var targetX =
            centerX + radius * Math.cos(currentTheta) + wobbleX;
          var targetY =
            centerY + radius * Math.sin(currentTheta) + wobbleY;

          var flagPosition = "flag-up-right";
          if(targetX < centerX && targetY < centerY){
            // top left corner
            flagPosition = i<2? "flag-up-left" : "flag-down-right";
          }else if(targetX < centerX && targetY > centerY){
            // bottom left corner
            flagPosition = i<2? "flag-down-left" : "flag-up-right";
          }else if(targetX > centerX && targetY < centerY){
            // top right corner
            flagPosition = i<2? "flag-up-right" : "flag-down-left";
          }else if(targetX > centerX && targetY > centerY){
            // bottom right corner
            flagPosition = i<2? "flag-down-right" : "flag-up-left";
          }
          $(view).find(".flag").removeClass (function (index, css) {
             return (css.match (/(^|\s)flag-\S+/g) || []).join(' ');
          });
          $(view).find(".flag").addClass(flagPosition);

          var degrees = (360 * currentTheta)/(Math.PI*2);
          $(view).find(".flag-rotated").css("transform","rotate("+degrees+"deg)");

          currentTheta += thetaStep;
          wobbleTheta += 0.5;

          $(view).removeClass (function (index, css) {
             return (css.match (/(^|\s)layer-\S+/g) || []).join(' ');
          });
          $(view).addClass("layer-"+i);


          $(view).animate(
            {
              top: targetY,
              left: targetX
            },
            500
          );
          // view.style.left = targetX + "px";
          // view.style.top = targetY + "px";
        }

        if (i < rings.length - 1) {
          var nodeDiameter = 16;
          var approxRingCircumference = nodeDiameter * rings[i + 1].length;
          var minRadiusPerItems = approxRingCircumference / (2 * Math.PI);
          var maxRadius = 300;
          addWobble = minRadiusPerItems > maxRadius;
          console.log(
            "Given that there are " +
              rings[i + 1].length +
              " items in the next ring, we estimate the needed circumference woudl be " +
              approxRingCircumference +
              " therefor we should use a radius of at least " +
              minRadiusPerItems
          );
          runningRadius += Math.min(
            maxRadius,
            Math.max(75, minRadiusPerItems)
          );
        }
      }
    },

    addListeners: function() {
      //bind events
      var parent_ref = this;

      window.addEventListener('resize', function(){
        //Wait until we are dont gettint resize events so we dont overwhelm the processor
        clearTimeout(parent_ref.resize_timeout)
        parent_ref.resize_timeout = setTimeout(function(){
          parent_ref.containerWidth = $(parent_ref.element).width();
          parent_ref.containerHeight = $(parent_ref.element).height();
          parent_ref.render();
        }, 250);

      });
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
