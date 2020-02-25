/*
    jQuery mysuggest plugin

    $(selector).mysuggest(opts);

    $(selector).mysuggest({
        interval: 300, // test for suggest not often then once in interval(ms)

        minlength: 3,  // minimal length of input value need for search

        results_width: 50, // width of results wrapper in pixels. default == field width

        exactmatch: false, // Clear selected_setts, if input field changed after selection;

        // Get suggestions by input value:
        get_results: function($elem, instance, callback) {
            // When results are coming call callback:
            callback(results);

            // Or
            return []; // returns results array imidiatly
        },

        // Do something on item select:
        on_complete: function($elem, event, event_type, instance) {
            // event_type can be: 'click' or 'select'
        },

        on_hide: function($elem, instance) {
        },

        on_show: function($elem, instance) {
        },

        // Do something on keyup:
        on_keyup: function($elem, event, instance) {
        }

        // Do something on input clearing:
        on_clear: function($elem, event, event_type, instance) {
        },

        // Do something on input marked as empty:
        on_empty: function($elem, event, event_type, instance) {
        },

    });

    Instance methods:
    show($elem): show results
    hide($elem): hide results
    blur($elem): blur without test for complete
    item = make_item(text, display, settings): Make new results item for results array

*/


(function($) {

    var suggestCore = function(opts) {
        if (!opts)
            opts = {};
    
        var baseClass = function() {
            this["opts"] = opts;
            this.init();
            return this;
        }
        var proto = baseClass.prototype;
    
        proto.class_prefix = opts["class_prefix"] || 'jquery_suggest_js_';
        proto.version = '2.0.1';
    

        proto.init = function() {
            console.log('Init mySuggest Core...');
            this.now_date = new Date();
            this.inputs = [];
        };

        proto.init_setts = function(setts) {
            if (!setts) setts = {};

            // Init elem settings:
            setts.search_results = [];
            setts.search_results_count = 0;
            setts.search_results_displayed = [];
            setts.search_text = '';
            setts.selected_result_setts = null;

            return setts;
        }

        proto.init_elem = function($elem, opts_) {
            var setts = this.init_setts();

            this.inputs.push([$elem, setts]);

            // Init elem DOM wrapper and results window:

            // Move input element into wrapper:
            var $wrapper = $('<div class="'+this.class_prefix+'_wrapper"></div>');
            $elem.before($wrapper);
            $elem.detach();
            $wrapper.append($elem);
            $elem.focus();

            // Make results div:
            var $results = $('<div class="'+this.class_prefix+'_results"></div>');
            $wrapper.append($results);
            setts.$results = $results;
            this['hide']($elem);

            var this_ = this;
            $elem.on('click touch', function(e) {
	        //e.preventDefault();
                this_['show']($elem, opts_);
            }).on('blur', function(e) {
                if (setts.is_blured)
                    setts.is_blured = false;
                else
                setTimeout(function() {
                    if (!$elem.is( ":focus" )) {
                        this_['hide']($elem);
                        this_.test_for_complete($elem, opts_, 'blur');
                    }
                }, 300);
            });
            return setts;
        };


        // Find input settings by $JQ input elem:
        proto['get_elem'] = function($elem) {
            for (var i in this.inputs)
                if (this.inputs[i][0].get(0) == $elem.get(0))
                    return this.inputs[i][1];
        };

        // Find Selected item settings by $JQ input elem:
        proto['get_selected_setts'] = function($elem) {
            var rsetts = this['get_elem']($elem);
            if (!rsetts || !rsetts.selected_result_setts || !rsetts.selected_result_setts.setts)
                return;
            return rsetts.selected_result_setts.setts;
        };


        // Get selected item:
        proto.get_selected = function($elem, setts) {
            if (!setts) setts = this['get_elem']($elem);
            return $('.'+this.class_prefix+'_result_wrap_selected', setts.$results).first();
        };


        // Get selected item settings:
        proto._get_selected_setts = function($elem, $selected, setts) {
            if (!setts) setts = this['get_elem']($elem);
            var rsetts = null;
            for (var i in setts.search_results_displayed)
                if (setts.search_results_displayed[i][0].get(0) == $selected.get(0))
                    rsetts = setts.search_results_displayed[i][1];
            return rsetts;
        }



        // Hide results:
        proto['hide'] = function($elem) {
            this['get_elem']($elem).$results.css('display', 'none');
        };


        // Show results:
        proto['show'] = function($elem, opts_) {
            var setts = this['get_elem']($elem);
            if (setts.search_results_count <= 0)
                return this['hide']($elem);

            var this_ = this;
            var results_width = opts_['results_width'] || $elem.width();
            results_width += 'px';
            setts.$results.css('width', results_width);
            //setts.$results.css('width', $elem.outerWidth(false)+'px');
            setts.$results.css('display', 'block');
            $(document).on('click', function(e) {
                if ($(e.target).parents().hasClass(this_.class_prefix+'_wrapper')) 
                    return;
                this_['hide']($elem);
                //$elem.focus();
            });
            $elem.focus();
        };


        // Blur without any actions:
        proto['blur'] = function($elem) {
            var setts = this['get_elem']($elem);
            setts.is_blured = true;
            $elem.blur();
        };


        // Process input key events:
        proto.check_event = function($elem, event, opts_) {
            if (event.keyCode) 
                code = event.keyCode;
            else
                code = -1;

            var setts = this['get_elem']($elem);
            var this_ = this;

            var result_hover = function($selected) {
                if (!$selected.get(0))
                    return false;
                $('.'+this_.class_prefix+'_result_wrap', setts.$results).removeClass(this_.class_prefix+'_result_wrap_selected');
                $selected.addClass(this_.class_prefix+'_result_wrap_selected');
                var rsetts = this_._get_selected_setts($elem, $selected, setts);
                if (rsetts) {
                    $elem.val(rsetts['text']);
                    setts.search_text = rsetts['text'];
                    setts.selected_result_setts = rsetts;
                }
                return true;
            };

            // Select result, hide other results and put result into input field:
            var result_select = function($selected) {
                var $selected = this_.get_selected($elem, setts);

                // Settings of selected result:
                var rsetts = this_._get_selected_setts($elem, $selected, setts);
                if (rsetts) {
                    $elem.val(rsetts['text']);
                    setts.search_text = rsetts['text'];
                    setts.selected_result_setts = rsetts;
                }

                this_['hide']($elem);
                this_.test_for_complete($elem, opts_, 'select');
            };

            //console.warn('XXX: ' + code);
            switch(code) {
                case 38:
                    //console.debug('UP');
                    this['show']($elem, opts_);

                    var $selected = this_.get_selected($elem, setts);
                    // No next elements or no selected element:
                    if (!result_hover($selected.prev())) {
                        $selected = $('.'+this_.class_prefix+'_result_wrap', setts.$results).last();
                        result_hover($selected); 
                    }
                    event.preventDefault();
                    break;

                case 40:
                    //console.debug('DOWN');
                    this['show']($elem, opts_);

                    var $selected = this_.get_selected($elem, setts);
                    // No next elements or no selected element:
                    if (!result_hover($selected.next())) {
                        $selected = $('.'+this_.class_prefix+'_result_wrap', setts.$results).first();
                        result_hover($selected);
                    }
                    event.preventDefault();
                    break;
                case 37:
                    //console.debug('LEFT');
                    break;
                case 39:
                    //console.debug('RIGHT');
                    result_select();
                    break;
                case 13:
                    //console.debug('ENTER');
                    result_select();
                    break;
                case 9:
                    //console.debug('TAB');
                    result_select();
                    break;
                case 27:
                    //console.debug('ESC');
                    this['hide']($elem);
                    event.preventDefault();
                    break;
                case 32:
                    //console.debug('SPACE');
                    break;
                default:
                    break;
            }
            
        }



        proto.call_on_event = function(event, $elem, opts_, setts, event_type) {
            var ev = 'on_' + event;
            if (!opts_[ev] || typeof(opts_[ev]) != 'function')  
                return;
            opts_[ev]($elem, setts, event_type, this);
        }

        proto.test_for_complete = function($elem, opts_, event_type) {
            var setts = this['get_elem']($elem);
            this['hide']($elem);
            return this.call_on_event('complete', $elem, opts_, setts, event_type);
        }


        proto.clear_input = function(clear_it, $elem, opts_, setts) {
            this.init_setts(setts);
            this['hide']($elem);
            if (clear_it)
                $elem.val('');
            return this.call_on_event('clear', $elem, opts_, setts);
        }


        // Search in input element (with checks):
        proto.search = function($elem, event, opts_) {
            var minlength = opts_['minlength'];
            if (!minlength && minlength != 0)
                minlength = 3;
            var setts = this['get_elem']($elem);

            if (!setts)
                setts = this.init_elem($elem, opts_);

            if (event)
                this.check_event($elem, event, opts_);

            if ($elem.val().length < minlength || $elem.val().length == 0) {
                this.clear_input(false, $elem, opts_, setts);
                if ($elem.val() != setts.search_text) {
                    setts.search_text = $elem.val();
                    return this.call_on_event('empty', $elem, opts_, setts);
                }
                return;
            }

            // Input field not changed:
            if ($elem.val() == setts.search_text)
                return;

            // Clear selected settings on any changes in input field:
            if (opts_['exactmatch'])
                this.clear_input(false, $elem, opts_, setts);
            
            setts.search_text = $elem.val();

            // If testing for complete in progress, do nothing:
            if (setts.status == 1) 
                return;

            // Another search in progress:
            if (setts.search_status == 2)
                return;

            if (!opts_['get_results'] || typeof(opts_['get_results']) != 'function') {
                return;
            }

            var this_ = this;
            var process_ = function(results) {
                this_.process_results($elem, setts, opts_, results);
            }
            var results = opts_['get_results']($elem, this, process_);
            if (results)
                process_(results);
        };


        proto['make_item'] = function(text_, display, settings) {
            return {
                'text': text_,
                'display': display,
                'setts': settings
            }
        };


        // Process results items:
        proto.process_results = function($elem, setts, opts_, results) {
            setts.search_results = results;
            setts.search_results_count += results.length;
            this.show_results($elem, setts, opts_);
        };


        // Show results in results wrapper:
        proto.show_results = function($elem, setts, opts_) {
            setts.$results.empty();

            var this_ = this;
            var make_$result = function(rsetts) {
                var display = rsetts['display'];
                var $result = $('<div class="'+this_.class_prefix+'_result_wrap"></div>');
                if (typeof(display) == 'string')
                    $result.html(display);
                else if (typeof(display) == 'object')
                    $result.append(display);

                $result.on('mouseover', function(e) {
                    $('.'+this_.class_prefix+'_result_wrap', setts.$results).removeClass(this_.class_prefix+'_result_wrap_selected');
                    $result.addClass(this_.class_prefix+'_result_wrap_selected');
                }).on('mouseout', function(e){
                    $result.removeClass(this_.class_prefix+'_result_wrap_selected');
                });

                $result.click('click', function(e) {
                    this_['hide']($elem, opts_);
                    $elem.val(rsetts['text']);
                    setts.selected_result_setts = rsetts;
                    this_.test_for_complete($elem, opts_, 'select');
                    $elem.focus();
                });

                return $result;
            }


            var process_result_item = function(rsetts) {
                var $result = make_$result(rsetts);
                //$result.addClass(this_.class_prefix+'_result_engine');
                setts.$results.append($result);
                setts.search_results_displayed.push([$result, rsetts]);
                rsetts['$'] = $result;
            };

            setts.search_results_displayed = [];
            for (var rid in setts.search_results) 
                process_result_item(setts.search_results[rid]);
            
            this['show']($elem, opts_);
        };

        return new baseClass;
    };

    var suggestcore = suggestCore();

    jQuery.fn.mysuggest = function(options) {

        options = $.extend({
            interval: 0
        }, options);

        function throttle(func, ms) {
            var isThrottled = false,
                savedArgs,
                savedThis;
        
            function wrapper() {
                if (isThrottled) { // (2)
                    savedArgs = arguments;
                    savedThis = this;
                    return;
                }
        
                func.apply(this, arguments); // (1)
                isThrottled = true;
                setTimeout(function() {
                    isThrottled = false; // (3)
                    if (savedArgs) {
                        wrapper.apply(savedThis, savedArgs);
                        savedArgs = savedThis = null;
                    }
                }, ms);
            }
            return wrapper;
        }

      
        var run_ = function(e, $this) {
            if (!e) var e = window.event;
            suggestcore.search($this, e, options);
            //e.preventDefault();
        };

        var trun_ = options.interval > 0 ? throttle(run_, options.interval) : run_;

        var init = function() {
            var $this = $(this);
            $this.prop('autocomplete', 'off');
            $this.on('keyup', function(e) {
                trun_(e, $this);
            });
            trun_(null, $this);
            $this.focus();
        };

        if (options['get_selected_setts']) {
            return suggestcore['get_selected_setts']($(this));
        }

        if (options['get_core']) {
            return suggestcore;
        }

        return this.each(init);
        
    };

})(jQuery);
