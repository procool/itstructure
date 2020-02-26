/*! core.js build:1.0.1, development. Copyright(c) 2020 procool@ New BSD Licensed */

/**
 * CORE of it structure project interface
 * Copyright(c) 2020 procool                ~
 *                                            ~
 * License: New BSD License                c(__)
**/



/*** USAGE 
            
*******************/




var ITCoreJS = function(opts) {
    if (!opts)
        opts = {};

    var $content_wrapper = opts["$content_wrapper"];
    var $menu_wrapper = opts["$menu_wrapper"];

    var baseClass = function() {
        return this;
    }
    var proto = baseClass.prototype;

    proto.class_prefix = opts["class_prefix"] || "core-";

    proto.acp = function(cls_) {
        return this.class_prefix + cls_;
    }

    proto.init = function() {
        this.now_date = new Date();
        this.init_forms();

        return this;
    }


    proto.init_forms = function() {

        if (window.l10n && l10n["window-title"]) document.title = l10n["window-title"];

        this.$menu = $("<div></div>");
        this.$menu.addClass(this.acp("menu-wrapper"));
        var $menu_show = $("<div>M E N U</div>");
        if (window.l10n && l10n["menu-show"]) $menu_show.html(l10n["menu-show"]);
        $menu_show.addClass(this.acp("menu-show"));
        $menu_show.hide();

        var $menu_title = $("<div>MENU</div>");
        if (window.l10n && l10n["menu-title"]) $menu_title.html(l10n["menu-title"]);
        $menu_title.addClass(this.acp("menu-title"));
        this.$menu.append($menu_title);
        
        $menu_wrapper.append(this.$menu);
        $menu_wrapper.append($menu_show);
 
        $content_wrapper.addClass(this.acp("content-wrapper"));

        var $close_bt = $("<div class=\""+this.acp("menu-close")+"\">x</div>");
        this.$menu.append($close_bt);

        var $p_main = this.make_menu_part("main");
        this.make_menu_bt($p_main, "equipment");
        this.make_menu_bt($p_main);
        this.make_menu_bt($p_main, "topology");
        this.make_menu_bt($p_main, "map");
        this.make_menu_bt($p_main);
        this.make_menu_bt($p_main, "areas");
        this.make_menu_bt($p_main, "racks");
        this.make_menu_bt($p_main);
        this.make_menu_bt($p_main, "history");
        this.make_menu_bt($p_main, "wiki");

        var $p_common = this.make_menu_part("common");
        this.make_menu_bt($p_common, "users");
        this.make_menu_bt($p_common, "groups");
        this.make_menu_bt($p_common);
        this.make_menu_bt($p_common, "library");

        var this_ = this;
        //$close_bt.on("click", function(e) {this_.$menu.css("margin-left", "-"+$menu_wrapper.outerWidth()+"px");});
        $close_bt.on("click", function(e) { 
            $close_bt.hide();
            this_.$menu.animate({width:'toggle'}, 100, function() {
                $menu_show.fadeIn("fast");
            }); 
        });
        $menu_show.on("click", function(e) { 
            $menu_show.fadeOut(50);
            this_.$menu.animate({width:'toggle'}, 100, function() {
                $close_bt.show();
            });
        });
        return this;
    }


    // Make some button:
    proto.make_bt = function(ident) {
        var $bt = $("<div class=\""+this.acp("menu-button")+"\"></div>");
        var $bt_a = $("<a></a>");
        $bt_a.prop("href", "#");
        if (window.l10n && l10n[ident]) {
            $bt.html(l10n[ident]);
        } else {
            $bt.html(ident);
        }
        $bt_a.append($bt);
        return $bt_a;
    }

    // Make button in main menu:  
    proto.make_menu_bt = function($part, ident) {
        if (!ident) {
            var $splitter = $("<div class=\""+this.acp("menu-splitter")+"\"></div>");
            $part.append($splitter);
            return $splitter;
        }
        var $bt = this.make_bt("menubutton-"+ident);
        $part.append($bt);
        return $bt;
    }

    // Make part in main menu:
    proto.make_menu_part = function(ident) {
        var $part = $("<div class=\""+this.acp("menu-part-wrapper")+"\"></div>");
        var $part_title = $("<div class=\""+this.acp("menu-part-title")+"\"></div>");
        var $part_items = $("<div class=\""+this.acp("menu-part-items")+"\"></div>");

        if (window.l10n && l10n["menupart-"+ident]) {
            $part_title.html(l10n["menupart-"+ident]);
        } else {
            $part_title.html(ident);
        }

        var this_ = this;

        $part.append($part_title).append($part_items);
        this.$menu.append($part);
        $part_title.on("click", function(e) { $part_items.slideToggle('fast'); });
        return $part_items;
    }


    return new baseClass;
}
