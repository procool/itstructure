var authobj = null;
var apiobj = null;
var mws = null;
$( document ).ready(function() {

    var bug = myBug($("body"), {fadein: 5000, fadeout: 500, debug: 0}).start().start_random_mouse_running();
/*
    mws = myWebSockets(iface_urls["ws"], {});
    mws.on('open', function(data) {
    });
    mws.connect();
*/


/*
    // Correct local time by webSockets:
    mws.on('jsonmessage', function(data) {
        mWs.connected = true;
        if (data['TIME_UTC']) {
        }
    });
*/



    //apiobj = APICoreJS(iface_urls["api"], {}).init();
/*
    authobj = AuthCoreJS("#auth_core_wrapper", {
        api: apiobj,
        on_login: function() {
            console.info("WS: sending session: " + $.cookie('auth_session'));
            mws.ws.send("session="+$.cookie('auth_session'));
        },
        on_logout: function() {
            console.info("WS: closing on logout");
            //mws.close();
        }
    }).init();
*/

    
    var core = ITCoreJS({
        $content_wrapper: $("#content_wrapper"),
        $menu_wrapper: $("#mainmenu_wrapper")
    }).init();

});

