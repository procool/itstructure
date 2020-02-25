var myWebSockets = function(url, opts) {
    if (!opts)
        opts = {};

    if (!opts['timeout']) 
        opts['timeout'] = 5000;

    if (!opts['ping_timeout']) 
        opts['ping_timeout'] = 10000;

    function randWDclassic(n){  // [ 3 ] random words and digits by the wocabulary
        var s ='', abd ='abcdefghijklmnopqrstuvwxyz0123456789', aL = abd.length;
        while(s.length < n)
            s += abd[Math.random() * aL|0];
        return s;
    } //such as "46c17fkfpl"
            
                

    var baseClass = function() {
        this['url'] = url;
        this["opts"] = opts;
        this.init();
        return this;
    }
    var proto = baseClass.prototype;

    proto.version = '2.0.1';
    proto.init = function() {
        this.ping_timeout = Date.now();
        this.ping_times = 0;
        this.connecting = false;
        this.events = {};
        this.eventsidx = {};
        this.first_message = false;
        this['start_ev_loop']();
    };

    proto._connect = function() {
        if (this.events['connecting'])
        for (var f_id in this.events['connecting']) {
            var f_ = this.events['connecting'][f_id][1];
            if (typeof(f_) != 'function')
                continue;
            f_(null, this);
        }

        var wsaddr = "ws://" + this['url'];
        console.info('WS Connecting to: ' + wsaddr);
        this.first_message = false;
        this['ws'] = new WebSocket(wsaddr);
        this['init_callbacks']();
    };

    proto['connect'] = function() {
        if (this.ws)
            return;
        if (this.connecting)
            return;
        this.connecting = true;
        var this_ = this;

        if (this.events['connecting'])
        for (var f_id in this.events['connecting']) {
            var f_ = this.events['connecting'][f_id][1];
            if (typeof(f_) != 'function')
                continue;
            f_(null, this);
        }


        try {
            this._connect();
        } catch (e) {
            console.error('WS Connecting failed: ' + e);
            this['close']();
            var this_ = this;
            setTimeout(function() {
                this_['connect']();
            }, opts['timeout']);
            this.connecting = false;
        }
    };

    proto['close'] = function() {
        console.info('WS: close()');

        if (this.events['close'])
        for (var f_id in this.events['close']) {
            var f_ = this.events['close'][f_id][1];
            if (typeof(f_) != 'function')
                continue;
                f_(null, this);
            }

        if (this.ws) {
            this.ws.close();
            delete this['ws'];
        }
        this.connecting = false;
        this['ws'] = null;
    }

    proto['init_callbacks'] = function() {
        if (!this['ws'])
            return;

        var this_ = this;
        this['ws'].onmessage = function(event) {
            console.info('WS Message: ' + event.data);

            this_.ping_timeout = Date.now();
            this_.ping_times = 0;

            if (!this_.first_message) {
                this_.first_message = true;
                for (var f_id in this_.events['startrecv']) {
                    var f_ = this_.events['startrecv'][f_id][1];
                    if (typeof(f_) != 'function')
                        continue;
                    f_(mdata, this_);
                }
            }

            if (this_.events['message'])
                for (var f_id in this_.events['message']) {
                    var f_ = this_.events['jsonmessage'][f_id][1];
                    if (typeof(f_) != 'function')
                        continue;
                    f_(event, this_);
                }

            if (this_.events['jsonmessage']) {
                try {
                    var mdata = JSON.parse(event.data);
                    for (var f_id in this_.events['jsonmessage']) {
                        var f_ = this_.events['jsonmessage'][f_id][1];
                        if (typeof(f_) != 'function')
                            continue;
                        f_(mdata, this_);
                    }
                } catch (e) {
                }
            }
        }

        this['ws'].onopen = function(event) {
            setTimeout(function() {
                this_.__onopen(event);
            }, 1000);
            this.connecting = false;
        }

        this.__onopen = function(event) {
            console.info('WS Connection opened!');
            if (this_.events['open'])
                for (var f_id in this_.events['open']) {
                    var f_ = this_.events['open'][f_id][1];
                    if (typeof(f_) != 'function')
                        continue;
                    f_(event, this_);
                }
        }

        this['ws'].onclose = function(event) {
            console.info('WS Connection closed!');
            this['close']();

            // Try to reconnect in 5 seconds
            setTimeout(function() {
                this_['connect']();
            }, opts['timeout']);

            if (this_.events['close'])
                for (var f_id in this_.events['close']) {
                    var f_ = this_.events['jsonmessage'][f_id][1];
                    if (typeof(f_) != 'function')
                        continue;
                    f_(event, this_);
                }
        };

    }

    proto['on'] = function(event, func) {
        if (event != 'message' && event != 'jsonmessage' && event != 'open' && event != 'close' && event != 'startrecv' && event != 'connecting')
            return;

        if (!this.events[event])
            this.events[event] = [];

        current_token = randWDclassic(15);

        //var found = false;
        //for (f_ in this.events[event])
        //    if (f_ == func)
        //        return false;
        this.eventsidx[current_token] = [event, func];
        this.events[event].push([current_token, func]);
        return current_token;
    }

    proto['off'] = function(event, func) {
        if (!this.events[event])
            return false;

        for (var i=0; i<this.events[event].length; i++)
            if (this.events[event][i][1] == func || !func) {
                delete this.eventsidx[this.events[event][i][0]];
                this.events[event].splice(i, 1);
            }
        return true;
    }

    proto['offbyid'] = function(id) {
        if (!this.eventsidx[id])
            return false;
        var event = this.eventsidx[current_token][0];

        for (var i=0; i<this.events[event].length; i++) 
            if (this.events[event][i][0] == id) {
                delete this.eventsidx[id];
                this.events[event].splice(i, 1);
            }
        return true;
    }


    proto._ev_loop = function() {
        // No new messages in opts['ping_timeout'] usecs:
        if (this.ping_timeout + opts['ping_timeout'] < Date.now()) {
            this.ping_timeout = Date.now();
            this.ping_times += 1;
            console.warn('WS: PING Timeout! ' + (this.ws ? this.ws.readyState : ''));
            if ((this.ws && (this.ws.readyState == 0 || this.ws.readyState == 3)) || !this.ws) {
                this['connect']();
            }
        }

        if (this.ping_times >= 3) {
            if (this.ws) {
                console.info('WS: Closing by timeout...');
                this['close']();
            }
            this.ping_times = 0;

        } else if (this.ws && this.ws.readyState == 3) {
            this['close']();
        }
    }

    proto.start_ev_loop = function() {
        var this_ = this;
        setInterval(function() {
            this_._ev_loop();
        }, 100);
    }

    return new baseClass;
}




