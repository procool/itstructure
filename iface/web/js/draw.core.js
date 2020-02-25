/*! core.js build:1.0.1, development. Copyright(c) 2019 procool@ New BSD Licensed */

/**
 * CORE of drawing interface of draftdesign project interface
 * Copyright(c) 2019 procool                ~
 *                                            ~
 * License: New BSD License                c(__)
**/



/*** USAGE 
            
Instance: 
    var instance = DrawCoreJS("#divident", OPTS);

OPTS:
    // No available options supported yet

METHODS:
    // Initialize forms
    init();

*******************/




var DrawCoreJS = function(main_wrapper, opts) {
    if (!opts)
        opts = {};

    if (!opts["menu"]) 
        opts["menu"] = [
            {
                "ident": "cursor",
                "imgoffset": "0px 0px",
                "selected": true
            },
            { 
                "ident": "path",
                "imgoffset": "0px -45px",
                "svg": "<path d=\"M 10 10 100 10\" stroke=\"black\"/ fill=\"none\">"
            },
            {
                "ident": "line",
                "imgoffset": "0px -87px",
                "init": function(e) { return this.snap.line(e.pageX, e.pageY, e.pageX+5, e.pageY).attr({stroke: "#000", strokeWidth: 3}); },
                "mmove": function(e, obj) { obj.attr({"x2": e.pageX, "y2": e.pageY}); }
            },
            {
                "ident": "rect",
                "imgoffset": "-1px -132px",
                "init": function(e) { return this.snap.rect(e.pageX, e.pageY, 5, 5).attr({stroke: "#000", strokeWidth: 3, fill: "none"}); },
                "mmove": function(e, obj) { 
                    var setts = {}, 
                        x = parseInt(obj.attr("x")), w = parseInt(obj.attr("width")),
                        y = parseInt(obj.attr("y")), h = parseInt(obj.attr("height"));
                    if (e.pageX >= x && (e.pageX > x + w || e.pageX-x > x + w - e.pageX)) {
                        setts["width"] = e.pageX-x;
                    } else { 
                        setts["width"] = w + x - e.pageX;
                        setts["x"] = e.pageX; 
                    }

                    if (e.pageY >= y && (e.pageY > y + h || e.pageY-y > y + h - e.pageY)) {
                        setts["height"] = e.pageY-y;
                    } else { 
                        setts["height"] = h + y - e.pageY;
                        setts["y"] = e.pageY;
                    }
                    obj.attr(setts);
                }
            },
            {
                "ident": "circle",
                "imgoffset": "0px -348px",
                "init": function(e) { return this.snap.circle(e.pageX, e.pageY, 5).attr({stroke: "#000", strokeWidth: 3, fill: "none"}); },
                "mmove": function(e, obj) { 
                    var setts = {}, 
                        x = parseInt(obj.attr("cx")), r = parseInt(obj.attr("r")),
                        y = parseInt(obj.attr("cy"));
                    setts["r"] = parseInt(Math.sqrt((e.pageX-x)**2 + (e.pageY-y)**2));
                    obj.attr(setts);
                }
            },
            {
                "ident": "ellipse",
                "imgoffset": "0px -175px",
                "init": function(e) { return this.snap.ellipse(e.pageX, e.pageY, 5, 5).attr({stroke: "#000", strokeWidth: 3, fill: "none"}); },
                "mmove": function(e, obj) {
                    var setts = {}, 
                        x = parseInt(obj.attr("cx")), rx = parseInt(obj.attr("rx")),
                        y = parseInt(obj.attr("cy")), ry = parseInt(obj.attr("ry"));
                    setts["rx"] = Math.abs(e.pageX-x);
                    setts["ry"] = Math.abs(e.pageY-y);
                    obj.attr(setts);
                }
            },
            {
                "ident": "polyline",
                "imgoffset": "0px -217px",
                "svg": "<polyline points=\"10,10 50,100 100,100 140,10\" stroke=\"red\" stroke-width=\"3\" />"
            },
            {
                "ident": "text",
                "imgoffset": "0px -303px",
                "svg": "<polyline points=\"10,10 50,100 100,100 140,10\" stroke=\"red\" stroke-width=\"3\" />"
            }
        ];

    var baseClass = function() {
        return this;
    }
    var proto = baseClass.prototype;

    proto.class_prefix = opts["class_prefix"] || "core-";

    var $mainwrapper = $(main_wrapper);


    proto.acp = function(cls_) {
        return this.class_prefix + cls_;
    }

    proto.init = function() {
        this.now_date = new Date();
        this.init_forms();

        this.snap = Snap(this.$canvas.get(0));

        this.objects = {};
        this.objects_last_id = 0;

        return this;
    }



    proto.init_forms = function() {

        // Draw left menu: ------------------------------------------------
        this.$menu = $('<div class="'+this.acp("menu")+'"></div>');

        // left menu buttons:
        for (var item in opts["menu"]) 
            this.make_menu_button(item);

        this.$canvas = $('<svg style="width: 800px; height: 300px;" class="'+this.acp("canvas")+'"></svg>');
        $mainwrapper.append(this.$menu);
        $mainwrapper.append(this.$canvas);

        var this_ = this;

        // On canvas clicked, draw selected object:
        this.$canvas.on("mousedown", function(e) {
            if (!this_.menu_selected || !this_.menu_selected.bt["mmove"] || !this_.menu_selected.bt["init"])
                return;
            this_.evoffset(e);
            //this_.objects[this_.objects_last_id] = this_.menu_selected.bt["init"].apply(this_, [e]);
            obj_ = this_.menu_selected.bt["init"].apply(this_, [e]);
            this_.objects_last_id += 1;
            this_.objects[this_.objects_last_id] = obj_;

            var mmove = function(e_) {
                this_.evoffset(e_);
                this_.menu_selected.bt["mmove"].apply(this_, [e_, obj_]);
            }
            var mup = function(e_) {
                $(document).off("mousemove", mmove);
                $(document).off("mouseup", mup);
            }
            $(document).on("mousemove", mmove);
            $(document).on("mouseup", mup);
        });
        return this;
    }


    proto.menu_button_select = function(bt, $bt) {
        if (this.menu_selected)
            this.menu_selected.$.removeClass("selected");
        this.menu_selected = {
            "bt": bt,
            "$": $bt,
        };
        this.menu_selected.$.addClass("selected");
    }

    proto.make_menu_button = function(item) {
        var bt = opts["menu"][item];
        var $bt = $('<div class="button"></div>');
        $bt.css("background-position", bt["imgoffset"]);
        $bt.attr("title", bt["ident"]);
        if (bt["selected"]) this.menu_button_select(bt, $bt);
        this.$menu.append($bt);

        var this_ = this;
/*
        var mouse_move_event = function(e) {
            e = e || window.event;
            console.log(e.pageX + ' ' + e.pageY);
            this_.menu_clicked.$.css({"left": e.pageX + "px", "top": e.pageY + "px"});
        }

        var clear_event = function(e) {
            $(document).off('mousemove', mouse_move_event);
            $(document).off('mouseup', clear_event);
            $(document).off('click', clear_event);
            if (!this_.menu_clicked) return;

            var offset_ = this_.$canvas.offset();
            e.pageX -= offset_.left;
            e.pageY -= offset_.top;
            if (this_.menu_clicked.bt.cb)
                this_.menu_clicked.bt.cb.apply(this_, [e]);

            this_.menu_clicked.$.remove();
            this_.menu_clicked = null;

            // todo: draw svg object in canvas on last coordinates
            // fixme: setup element in SVG format in opts.menu
        }

        $bt.on('mousedown', function(e) {
            e = e || window.event;
            this_.menu_clicked = {
                "bt": bt,
                "$bt": $bt,
                "$": $bt.clone()
            };
            this_.menu_clicked.$.css({"left": e.pageX + "px", "top": e.pageY + "px"});
            this_.menu_clicked.$.addClass("dragged-wrapper");
            this_.$menu.append(this_.menu_clicked.$);
            $(document).on('mousemove', mouse_move_event);
            $(document).on('mouseup', clear_event);
            $(document).on('click', clear_event);
        });
*/
        $bt.on('click', function(e) {
            this_.menu_button_select(bt, $bt);
        });
    }


    proto.evoffset = function(e) {
        var offset_ = this.$canvas.offset();
        e.pageX -= offset_.left;
        e.pageY -= offset_.top;
    }





    return new baseClass;
}
