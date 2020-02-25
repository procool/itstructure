/*! core.js build:1.0.1, development. Copyright(c) 2019 procool@ New BSD Licensed */

/**
 * CORE of API callbacks on draftdesign project interface
 * Copyright(c) 2019 procool                ~
 *                                            ~
 * License: New BSD License                c(__)
**/



/*** USAGE 
            
Instance: 
    var instance = APICoreJS(OPTS);

OPTS:
    // No available options supported yet

METHODS:
    // Initialize forms
    init();

*******************/




var APICoreJS = function(api_url, opts) {
    if (!opts)
        opts = {};

    var baseClass = function() {
        return this;
    }
    var proto = baseClass.prototype;

    proto.init = function() {
        this.now_date = new Date();
        this.initialized = false;
        this.handlers = {};
        this.get_handlers();
        return this;
    }

    proto.check_session = function(session, callback) {
        this.call_handler("auth:session", {}, {"session": session}, callback);
    }
    proto.check_auth = function(login, passwd, callback) {
        this.call_handler("auth:auth", {}, {"username": login, "password": passwd}, callback);
    }


    proto.get_handlers = function(callback) {
        var this_ = this;
        if (!callback) callback = function (data) {
            //console.log("API: HANDLERS DATA: ");
            var store_handler = function (i) {
                var item = data["handlers"][i];
                var ident = item[0] + ':' + item[1];
                this_.handlers[ident] = item[2];
                //console.log(ident + ' : ' + this_.handlers[ident]);
            }
            for (var i in data["handlers"])
                store_handler(i);
            this_.initialized = true;
        }
        this._call_handler("/handlers/", {}, callback);
    }


    proto.call_handler = function(handler, setts, params, callback, delayed) {
        if (!this.initialized) {
            if (!delayed) delayed = 0;
            if (delayed > 3) {
                console.error("API: Failed on calling handler "+handler+": still not initialized!");
                return;
            }
            var this_ = this;
            setTimeout(function() {
                this_.call_handler(handler, setts, params, callback, delayed+1); 
            }, 300);
            return;
        }

        var kwargs = {};
        if (setts["parent"]) kwargs["string:parentid"] = setts["parent"];
        if (setts["pk"]) kwargs["int:pk"] = setts["pk"];
        if (setts["pk_s"]) kwargs["string:pk"] = setts["pk_s"];
        handler = this.make_handler(handler, kwargs);
        return this._call_handler(handler, params, callback);
    }

    proto.make_handler = function(handler, kwargs) {
        var hl = this.handlers[handler];
        for (i in kwargs) 
            hl = hl.replace("<"+i+">", kwargs[i]);
        return hl;
    }

    proto._call_handler = function(handler, params, callback) {
        var url = api_url;

        if (!handler) {
            console.error("No handler found! Available handlers is:");
            console.error(this.handlers);
        }

        // Absolute url:
        if (handler.charAt(0) == "/") {
            url += handler
        // Reference:
        } else {
            url += this.handlers[handler];
        }
        if (!params) params = {};
        var $get_obj = $.post(url, params, function(data, textStatus) {
            callback(data);
        }, 'json');
    }



    return new baseClass;
}
