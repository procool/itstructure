/*! holst.core.js build:1.0.1, development. Copyright(c) 2019 procool@ New BSD Licensed */

/**
 * CORE of drawing interface of istructure project interface
 * Copyright(c) 2019 procool                ~
 *                                            ~
 * License: New BSD License                c(__)
**/



/*** USAGE 
            
*******************/




var HolstCoreJS = function(opts) {
    if (!opts)
        opts = {};

    var $draw_wrapper = opts["$draw_wrapper"];
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
        this.scaled = 1;
        this.now_date = new Date();
        this.init_forms();

        this.snap = Snap(this.$canvas.get(0));

        this.init_page();
        this.objects = {};
        this.objects_last_id = 0;
 
        this.zoomout(0.5);

        return this;
    }



    proto.init_forms = function() {

        var main_width = 300 + opts["size_desktop"][0] + opts["size_mobile"][0];
        this.$canvas = $('<svg style="width: '+main_width+'px; height: 600px; border: 0px;" class="'+this.acp("canvas")+'"></svg>');
        $draw_wrapper.append(this.$canvas);

        var this_ = this;

        return this;
    }


    proto.init_page = function() {
        var 
            x_ = 20,
            y_ = 20;
        var p1xy = opts["size_desktop"];
        var p2xy = opts["size_mobile"];

        this.snap.rect(x_, y_, p1xy[0], p1xy[1]).attr({stroke: "#000", strokeWidth: 1, fill: "#fff"});
        this.snap.rect(x_+p1xy[0]+10, y_, p2xy[0], p2xy[1]).attr({stroke: "#000", strokeWidth: 1, fill: "#fff"});
        //this.$canvas.append("<rect x="2" y="2" width="60" height="60" style="stroke-width: 3px;" stroke="#000000" fill="none"></rect>")
        //this.$canvas.append("<rect x="2" y="2" width="60" height="60" style="stroke-width: 3px;" stroke="#000000" fill="none"></rect>")
    }


    proto.evoffset = function(e) {
        var offset_ = this.$canvas.offset();
        e.pageX -= offset_.left;
        e.pageY -= offset_.top;
    }


    proto.zoom = function(scale, is_out) {
        if (is_out) scale = -1*scale;
        this.scaled += scale;
        
        //this.snap.animate().transform('S'+this.scaled+','+this.scaled+',-550,0');
        
        var dx = parseInt(this.snap.node.clientWidth/2),
            dy = parseInt(this.snap.node.clientHeight/2);
        this.snap.transform('S'+this.scaled+','+this.scaled+',-'+dx+',-'+dy);
        //this.snap.transform('S'+this.scaled+','+this.scaled+',-550,-300');
    }

    proto.zoomin = function(scale) { this.zoom(scale, false); }
    proto.zoomout = function(scale) { this.zoom(scale, true); }




    return new baseClass;
}
