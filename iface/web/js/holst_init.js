$( document ).ready(function() {
    var holst = HolstCoreJS({
        size_desktop: [640,480],
        size_mobile: [240,320],
        $menu_wrapper: $("#holst_menu_items"),
        $draw_wrapper: $("#holst_draw_wrapper")
    }).init();
    
    $("#zoomin").on("click", function(e) { holst.zoomin(0.2); });
    $("#zoomout").on("click", function(e) { holst.zoomout(0.2); });

});

