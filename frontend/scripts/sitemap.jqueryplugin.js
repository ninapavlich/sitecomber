import { SVG } from "@svgdotjs/svg.js";

/*!
 * nina@ninalp.com
 *
 *  TODO List:
 * - Add lines between connections
 * - Add ability to visualize links VS hierarchy
 * - Fix linking so you can click on a link without clicking on the node
 * - Add error indicators
 * - Add the ability to deep link to a selection to assist with preserving state
 * - Better visually distinguish broken links
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
    this.hasErrors = this.data.errors.length > 0;

    this.iolinks = {};

    for (var i = 0; i < this.data.incoming.length; i++) {
      var link = this.data.incoming[i];
      if (!(link in this.iolinks)) {
        this.iolinks[link] = {
          incoming: false,
          outgoing: false
        };
      }
      this.iolinks[link].incoming = true;
    }
    for (var i = 0; i < this.data.outgoing.length; i++) {
      var link = this.data.outgoing[i];
      if (!(link in this.iolinks)) {
        this.iolinks[link] = {
          incoming: false,
          outgoing: false
        };
      }
      this.iolinks[link].outgoing = true;
    }

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
      if (this.hasErrors) {
        $(this.view).addClass("errors");
      }
    },
    registerHierarchicalChild: function(child) {
      this.hierarchicalChildren.push(child);
    },

    // populateHierarchicalRelationships: function(currentRing, ringMap) {
    //   if (ringMap.ids.includes(this.id)) {
    //     return;
    //   }
    //
    //   //assuming I am on the currentRing, add all my children to the next layer out. unless they are already in the ring?
    //   ringMap.ids.push(this.id);
    //   if (!ringMap[currentRing]) {
    //     ringMap[currentRing] = [];
    //   }
    //   ringMap[currentRing].push(this);
    //   for (var i = 0; i < this.hierarchicalChildren.length; i++) {
    //     var child = this.hierarchicalChildren[i];
    //     child.populateHierarchicalRelationships(currentRing + 1, ringMap);
    //   }
    //
    //   if (this.parentNode) {
    //     this.parentNode.populateHierarchicalRelationships(
    //       currentRing + 1,
    //       ringMap
    //     );
    //   }
    // },

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
      var html = "<span class='ring'></span>";
      html += "<span class='flag bg-secondary text-light'>";

      var labelSuffix = this.data.children.length === 0 ? "" : "/";
      var label = this.isSite
        ? this.data.url
        : "/" + this.data.path + labelSuffix;
      html += this.data.info_url
        ? "<h1><a href='" + this.data.info_url + "'>" + label + "</a></h1>"
        : "<h1>" + label + "</h1>";
      html += this.data.url
        ? "<h2><a href='" +
          this.data.full_url +
          "' target='_blank' title='Open in new tab'>" +
          this.data.full_url +
          "</a></h2>"
        : "";
      html +=
        this.data.children.length === 0
          ? ""
          : this.data.children.length == 1
          ? "<p>1 child</p>"
          : "<p>" + this.data.children.length + " children</p>";

      for (var i = 0; i < this.data.errors.length; i++) {
        html += "<p>" + this.data.errors[i] + "</p>";
      }
      if (this.data.info_url) {
        html += "<p><a href='" + this.data.info_url + "'>View Details</a></p>";

        // html += "<span class='iolinks'>";
        //
        // for (var url in this.iolinks) {
        //   var incoming = this.iolinks[url].incoming;
        //   var outgoing = this.iolinks[url].outgoing;
        //   var iostr =
        //     (incoming ? "<span>i</span>" : "") +
        //     (outgoing ? "<span>o</span>" : "");
        //
        //   html += "<p data-id='" + url + "'>" + iostr + " " + url + "</p>";
        // }
        //
        // html += "</span>";
      }
      html += "</span>";

      var childCount =
        this.data.children.length > 0
          ? " <span class='count'>(" + this.data.children.length + ")</span>"
          : "";
      html +=
        "<span class='flag-rotated text-light'><h1><span class='truncate'>" +
        label +
        "</span>" +
        childCount +
        "</h1></span>";
      return html;
    },

    addListeners: function() {},

    removeListeners: function() {
      //unbind events
    }
  };

  // The actual plugin constructor
  var LINE_HEIGHT = 18;
  function Sitemap(element, options) {
    this.element = element;
    this.containerWidth = $(this.element).width();
    this.containerHeight = $(this.element).height();

    this.options = $.extend({}, defaults, options);

    this.windows = {};

    this.data = options.data;
    this.inited = false;
    this.resize_timeout = -1;
    this.scroll_timeout = -1;

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
      $(node.view)
        .find(".ring, .flag-rotated")
        .click(function() {
          ref.onNodeClicked(node);
        });

      $(node.view).mouseover(function() {
        ref.positionFlag(node);
      });

      this.allNodes.push(node);

      for (var i = 0; i < data.children.length; i++) {
        var child = data.children[i];
        this.allNodes.push(this.initNode(child, node));
      }
      return node;
    },

    resizeContainer(w, h) {
      this.containerWidth = w;
      this.containerHeight = h;
    },
    render: function() {
      $(this.view).removeClass(function(index, css) {
        return (css.match(/(^|\s)mode-\S+/g) || []).join(" ");
      });
      $(this.view).addClass(this.mode);

      this.positionFlag(this.activeNode);

      //Update all the markup within the nodes
      for (var i = 0; i < this.allNodes.length; i++) {
        var node = this.allNodes[i];
        node.render();
      }

      this.distributeTree(this.rootNode, this.activeNode);
      // this.positionIOLinks();
    },

    onNodeClicked: function(node) {
      if (this.activeNode === node) {
        this.activeNode == this.activeNode.parentNode
          ? this.activeNode.parentNode
          : node;
      } else {
        this.activeNode = node;
      }
      this.render();
    },

    /**
     * Given a map in this shape:
     * {'id', 'children':[ {'id', 'children':[]}], 'parent':{'id', 'children':[]}}
     *
     * Distribute these nodes into a set of tree branches, where the item in the 0th
     * place is at the top, and the items in the nth place are towards the bottom
     */
    distributeTree: function(rootNode) {
      //Resize container height:
      $(this.element).height(
        LINE_HEIGHT * (rootNode.hierarchicalChildren.length + 1)
      );
      this.containerHeight = $(this.element).height();

      var w = this.containerWidth;
      var h = this.containerHeight;
      var centerX = 50;
      var centerY = 0.5 * h;
      $(rootNode.view).animate(
        {
          top: centerY,
          left: centerX
        },
        500
      );

      this.distributeBranch(rootNode, rootNode, centerX, centerY, h);
    },

    /**
     * Given a node with a starting x and y, position all its children
     */
    distributeBranch: function(node, parentNode, x, y) {
      var isActiveNode = node.id === this.activeNode.id;
      var isAncestorOfActiveNode =
        !isActiveNode && this.activeNode.id.includes(node.id);
      var isDirectAncestorOfActiveNode =
        !isActiveNode &&
        this.activeNode.id
          .split("/")
          .slice(0, -1)
          .join("/") === node.id;
      var isDirectDescendentOfActiveNode = this.activeNode.hierarchicalChildren.includes(
        node
      );

      var activePathPieces = this.activeNode.data.full_path.split("/");
      var nodePieces = node.data.full_path.split("/");
      var isAdjacentAncestorOfActiveNode =
        nodePieces.length <= activePathPieces.length &&
        activePathPieces
          .slice(0, 0 - (activePathPieces.length - nodePieces.length) - 1)
          .join("/") === nodePieces.slice(0, -1).join("/");

      var state = "";
      if (isActiveNode) {
        state += "state-active ";
      }
      if (isAncestorOfActiveNode) {
        state += "state-ancestor ";
      }
      if (isDirectAncestorOfActiveNode) {
        state += "state-direct-ancestor ";
      }
      if (isDirectDescendentOfActiveNode) {
        state += "state-descendent ";
      }
      if (isAdjacentAncestorOfActiveNode) {
        state += "state-adjacentdescendent ";
      }
      $(node.view).removeClass(function(index, css) {
        return (css.match(/(^|\s)state-\S+/g) || []).join(" ");
      });
      $(node.view).addClass(state);

      var currentX = x + 250;
      var currentY = this.getStartingY(node, parentNode, y);
      // console.log("y?", y, "currentY? --- ", currentY);

      for (var i = 0; i < node.hierarchicalChildren.length; i++) {
        var item = node.hierarchicalChildren[i];
        var view = item.view;
        var targetX = currentX;
        var targetY = currentY;
        currentY += LINE_HEIGHT;
        $(view).animate(
          {
            top: targetY,
            left: targetX
          },
          500
        );

        this.distributeBranch(item, parentNode, targetX, targetY);
      }

      if (
        (isActiveNode ||
          isDirectDescendentOfActiveNode ||
          isAncestorOfActiveNode) &&
        currentY + LINE_HEIGHT > this.containerHeight
      ) {
        $(this.element).height(currentY + LINE_HEIGHT);
        this.containerHeight = $(this.element).height();
      }
    },

    getStartingY(node, parentNode, y) {
      var isActiveNode = node.id === this.activeNode.id;
      var isAncestorOfActiveNode =
        !isActiveNode && this.activeNode.id.includes(node.id);

      var shouldCenterChildList = isAncestorOfActiveNode;

      if (shouldCenterChildList) {
        var runningY = 0;
        for (var i = 0; i < node.hierarchicalChildren.length; i++) {
          var child = node.hierarchicalChildren[i];

          if (
            child.id === this.activeNode.id ||
            this.activeNode.id.includes(child.id)
          ) {
            return y - runningY;
          }
          runningY += LINE_HEIGHT;
        }
        return y;
      } else {
        var verticalRange = node.hierarchicalChildren.length * LINE_HEIGHT;
        return Math.max(LINE_HEIGHT, y - 0.5 * verticalRange);
      }
    },

    positionIOLinks: function() {
      var centerY = parseInt($(this.activeNode.view).css("top"));
      var centerX = parseInt($(this.activeNode.view).css("left"));
      var incomingLinks = $(this.activeNode.view).find(".incoming p");
      var outgoingLinks = $(this.activeNode.view).find(".outgoing p");

      console.log("incoming? " + incomingLinks.length);
      console.log("outgoing? " + outgoingLinks.length);

      var currentTheta = 1.5 * Math.PI;
      var thetaStep = Math.PI / incomingLinks.length;
      var radius = 200;
      for (var i = 0; i < incomingLinks.length; i++) {
        var view = incomingLinks[i];
        var targetX = centerX + radius * Math.cos(currentTheta);
        var targetY = centerY + radius * Math.sin(currentTheta);
        $(view).animate(
          {
            top: targetY,
            left: targetX
          },
          500
        );
        currentTheta -= currentTheta;
      }
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

      for (var i = 0; i < rings.length; i++) {
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
          var targetX = centerX + radius * Math.cos(currentTheta) + wobbleX;
          var targetY = centerY + radius * Math.sin(currentTheta) + wobbleY;

          var degrees = (360 * currentTheta) / (Math.PI * 2);
          var transform =
            degrees > 90 && degrees < 270
              ? "rotate(" +
                degrees +
                "deg) scaleY(-1) scaleX(-1) translateX(-100%) translateY(-0.5em)"
              : "rotate(" + degrees + "deg) translateY(-0.5em)";
          $(view)
            .find(".flag-rotated")
            .css("transform", transform);

          currentTheta += thetaStep;
          wobbleTheta += 0.5;

          $(view).removeClass(function(index, css) {
            return (css.match(/(^|\s)layer-\S+/g) || []).join(" ");
          });
          $(view).addClass("layer-" + i);

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
          var minRadiusPerItems = this.getApproxRingCircumference(
            rings[i + 1].length
          );
          var minRadius = 100;
          var maxRadius = 300;
          addWobble = minRadiusPerItems > maxRadius;
          runningRadius += Math.min(
            maxRadius,
            Math.max(minRadius, minRadiusPerItems)
          );
        }
      }
    },

    getApproxRingCircumference(totalItems) {
      var nodeDiameter = 16;
      var approxRingCircumference = nodeDiameter * totalItems;
      var minRadiusPerItems = approxRingCircumference / (2 * Math.PI);
      return minRadiusPerItems;
    },

    positionFlag(node) {
      var targetX = node.view.getBoundingClientRect().left;
      var targetY = node.view.getBoundingClientRect().top;
      var midX = this.containerWidth * 0.5;
      var midY = this.containerHeight * 0.5;
      var flagPosition = "flag-up-right";
      // if (targetX < midX && targetY < midY) {
      //   // top left corner
      //   flagPosition = "flag-down-right";
      // } else if (targetX < midX && targetY > midY) {
      //   // bottom left corner
      //   flagPosition = "flag-up-right";
      // } else if (targetX > midX && targetY < midY) {
      //   // top right corner
      //   flagPosition = "flag-down-left";
      // } else if (targetX > midX && targetY > midY) {
      //   // bottom right corner
      //   flagPosition = "flag-up-left";
      // }

      if (targetY < midY) {
        // top left corner
        flagPosition = "flag-down-right";
      } else if (targetY >= midY) {
        // bottom left corner
        flagPosition = "flag-up-right";
      }

      $(node.view)
        .find(".flag")
        .removeClass(function(index, css) {
          return (css.match(/(^|\s)flag-\S+/g) || []).join(" ");
        });
      $(node.view)
        .find(".flag")
        .addClass(flagPosition);
    },

    addListeners: function() {
      //bind events
      var parent_ref = this;

      window.addEventListener("resize", function() {
        //Wait until we are dont gettint resize events so we dont overwhelm the processor
        clearTimeout(parent_ref.resize_timeout);
        parent_ref.resize_timeout = setTimeout(function() {
          parent_ref.resizeContainer(
            $(parent_ref.element).width(),
            $(parent_ref.element).height()
          );
          parent_ref.render();
        }, 250);
      });

      window.addEventListener("scroll", function() {
        //Wait until we are dont gettint resize events so we dont overwhelm the processor
        clearTimeout(parent_ref.scroll_timeout);
        parent_ref.scroll_timeout = setTimeout(function() {
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
