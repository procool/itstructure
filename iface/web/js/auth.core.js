/*! core.js build:1.0.1, development. Copyright(c) 2019 procool@ New BSD Licensed */

/**
 * CORE of authorization process on itstructure project interface
 * Copyright(c) 2019 procool                ~
 *                                            ~
 * License: New BSD License                c(__)
**/



/*** USAGE 
            
Instance: 
    var instance = AuthCoreJS("#divident", OPTS);

OPTS:
    // No available options supported yet

METHODS:
    // Initialize forms
    init();

*******************/




var AuthCoreJS = function(main_wrapper, opts) {
    if (!opts)
        opts = {};

    var baseClass = function() {
        return this;
    }
    var proto = baseClass.prototype;

    proto.class_prefix = opts["class_prefix"] || "js-auth-";

    var $mwrap = $(main_wrapper);


    proto.acp = function(cls_) {
        return this.class_prefix + cls_;
    }

    proto.init = function() {
        this.now_date = new Date();
        this.init_forms();
        this.init_check_auth();

        setTimeout(function() {
            //console.log(opts["api"].handlers);
            //opts["api"].call_handler("collections:categories_list", {parent: 1}, {}, function(data) {
            //    console.info(data);
            //});
        }, 1000);

        return this;
    }



    proto.init_forms = function() {
        $('.'+this.acp('m')+' .error', $mwrap).html("").hide();
        $('.'+this.acp('m')+' .greeting', $mwrap).show();

        var this_ = this;
        $('.'+this.acp('i-login'), $mwrap).on('keyup', function() {$(this).removeClass("invalid")});
        $('.'+this.acp('i-password'), $mwrap).on('keyup', function() {$(this).removeClass("invalid")});
        $('.'+this.acp('submit'), $mwrap).on("click", function(e) {
            $('.'+this_.acp('m')+' .error', $mwrap).html("").hide();
            $('.'+this_.acp('m')+' .greeting', $mwrap).show();
            var login = $('.'+this_.acp('i-login'), $mwrap).val();
            var passwd = $('.'+this_.acp('i-password'), $mwrap).val();
            if (!login) $('.'+this_.acp('i-login'), $mwrap).addClass("invalid");
            if (!passwd) $('.'+this_.acp('i-password'), $mwrap).addClass("invalid");
            if (!login || !passwd) return;

            opts["api"].check_auth(login, passwd, function(data) {
                if (data["errno"] < 0) {
                    var err_ = data["error"];
                    if (err_ == "wrong_passwd") err_ = "Wrong user or password!";
                    $('.'+this_.acp('m')+' .greeting', $mwrap).hide();
                    $('.'+this_.acp('m')+' .error', $mwrap).html(err_).show();
                    return;
                }
                $.cookie('auth_session', data["session"]);
                $.cookie('auth_uid', data["uid"]);
                $.cookie('auth_login', login);

                this_.init_check_auth();
            });
        });

        $('.'+this.acp('logout'), $mwrap).on("click", function(e) {this_.logout();});

        this.show_inputs();
    }

    proto.logout = function() {
        $.removeCookie('auth_session');
        $.removeCookie('auth_uid');
        $.removeCookie('auth_login');
        // TODO: REMOVE SESSION:
        this.init_check_auth();
        if (opts["on_logout"]) opts["on_logout"]();
    }

    proto.init_check_auth = function() {
        var 
            this_ = this,
            sess  = $.cookie('auth_session'),
            uid   = $.cookie('auth_uid'),
            login = $.cookie('auth_login');

        // Check session:
        if (sess && uid && login) {
            opts["api"].check_session(sess, function(data) {
                if (data["errno"] < 0) this_.logout();
                $.cookie('auth_uid', data["uid"]);
                this_.show_greeting(login);
                if (opts["on_login"]) opts["on_login"]();
            });
        } else {
            this.show_inputs();
        }
    }

    proto.show_inputs = function() {
        $('.'+this.acp('authorized'), $mwrap).hide();
        $('.'+this.acp('inputs'), $mwrap).show();
    }

    proto.show_greeting = function(uname) {
        $('.'+this.acp('authorized'), $mwrap).show();
        $('.'+this.acp('inputs'), $mwrap).hide();
        $('.'+this.acp('f-username'), $mwrap).html(uname);
    }

    return new baseClass;
}
