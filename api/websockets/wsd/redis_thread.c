#include <syslog.h>
#include <unistd.h>
#include <stdlib.h>
// #include <malloc.h>
#include <pthread.h>
#include <semaphore.h>
#include <string.h>

#include <hiredis/hiredis.h>
#include <hiredis/async.h>
#include <hiredis/adapters/libev.h>

#include "config.h"
#include "redis_thread.h"

int redis_server_connected = 0;
redisAsyncContext *redis_server_obj;

int redis_pubserver_connected = 0;
redisAsyncContext *redis_pubserver_obj;
    
struct thread_arg_struct *redis_srv_args;
ev_timer timeout_watcher;


void myredisOnMessage(redisAsyncContext *c, void *r, void *priv) {
    struct server_params *srv_params = (struct server_params *) priv;
    sem_wait(&srv_params->sem);
    redisReply *reply = r;
    if (reply == NULL) {
        sem_post(&srv_params->sem);
        return;
    }
    if ( reply->type == REDIS_REPLY_ARRAY && reply->elements == 3 ) {
        if ( strcmp( reply->element[0]->str, "subscribe" ) != 0 ) {
            syslog(LOG_INFO, "REDIS: RECV[%s]: %s", 
                reply->element[1]->str,
                reply->element[2]->str
            );
            srv_params->ws_func_all_clients_send_message(srv_params->clients_list_start, reply->element[2]->str);
        }
    }
    sem_post(&srv_params->sem);
}


    
void myredisOnReply(redisAsyncContext *c, void *r, void *priv) {
    redisReply *reply = r;
    if (reply == NULL) {
        syslog(LOG_INFO, "REDIS PUBLISH REPLY: NOTHING");
        return;
    }
    if ( reply->type == REDIS_REPLY_INTEGER) {
        syslog(LOG_INFO, "REDIS PUBLISH REPLY: INTEGER: %lld", reply->integer);
    } else if ( reply->type == REDIS_REPLY_ERROR) {
        syslog(LOG_INFO, "REDIS PUBLISH REPLY: ERROR: %s", reply->str);
    } else if ( reply->type == REDIS_REPLY_STRING) {
        syslog(LOG_INFO, "REDIS PUBLISH REPLY: STRING: %s", reply->str);
    } else if ( reply->type == REDIS_REPLY_STATUS) {
        syslog(LOG_INFO, "REDIS PUBLISH REPLY: STATUS: %s", reply->str);
    } else {
        syslog(LOG_INFO, "REDIS PUBLISH REPLY: %d", reply->type);
    }
    
}


char* escape_string(const char *input, size_t len, int is_soft) {
    // First, count size of result string:
    char *input_ptr = (char*)input;
    size_t counter = 0;
    while ((*input_ptr != '\0') && (size_t)(input_ptr - input) < len) {
        if (is_soft==0 && *input_ptr == '\\') {
            input_ptr+=2;
            counter+=2;
            continue;
        }
        if (*input_ptr == '\"' || *input_ptr == ' ')
            counter++;
        //if (*input_ptr == ' ')
        //    counter+=6;
        input_ptr++;
    }

    // Allocate memory for output:
    size_t final_len = len + counter + 1;
    char *output = (char*)malloc(sizeof(char)*final_len);
    memset(output, 0, final_len);

    // Make output:
    for (size_t i=0, j=0; i<len; i++, j++) {
        if (is_soft==0 && input[i] == '\\') {
            output[j++] = '\\';
            output[j++] = '\\';
            strncpy(output+j, input+i, 2);
            i++;
            j++;
        } else if (input[i] == '\"' || input[i] == ' ') {
            output[j++] = '\\';
            output[j] = input[i];
        //} else if (input[i] == ' ') {
        //    strncpy(output+j, "&nbsp;", 6);
        //    j+=5;
        } else {
            output[j] = input[i];
        }
    }
    output[final_len] = '\0';
    return output;
}


void myredis_publish(const char *message) {
    syslog(LOG_INFO, "REDIS PUBLISH ->: %s", message);
    const char *argv[3];
    argv[0] = "PUBLISH";
    argv[1] = "wsint_channel";
    argv[2] = message;
    size_t lens[3] = { 7, strlen(argv[1]), strlen(argv[2]) };
    int argc = 3;
    redisAsyncCommandArgv(redis_pubserver_obj, myredisOnReply, NULL, argc, argv, lens);
}


void myredisConnectCallback(const redisAsyncContext *c, int status) {
    if (status != REDIS_OK) {
        //ev_break(EV_DEFAULT_ EVBREAK_ALL);
        syslog(LOG_ERR, "REDIS: Connecting to server error: %s", c->errstr);
        redis_server_connected = 0;
    } else {
        redis_server_connected = 1;
        syslog(LOG_INFO, "REDIS: Connected!");
    }
}

void myredisDisconnectCallback(const redisAsyncContext *c, int status) {
            
    //ev_break(EV_DEFAULT_ EVBREAK_ALL);
    if (status != REDIS_OK) {
        syslog(LOG_ERR, "REDIS: Disconnecting from server error: %s", c->errstr);
    } else {
        syslog(LOG_INFO, "REDIS: Disconnected!");
    }
    redis_server_connected = 0;
}


int redis_connect_server(struct server_params *params) {
    syslog(LOG_DEBUG, "REDIS: Connecting to server...");

    redis_server_connected = 1;
    redis_server_obj = redisAsyncConnect("localhost", 6379);
    if (redis_server_obj->err) {
        syslog(LOG_ERR, "REDIS: Connecting to server failed: %s", redis_server_obj->errstr);
        return 1;
    }

    redisLibevAttach(EV_DEFAULT_ redis_server_obj);
    redisAsyncSetConnectCallback(redis_server_obj, myredisConnectCallback);
    redisAsyncSetDisconnectCallback(redis_server_obj, myredisDisconnectCallback);

    redisAsyncCommand(redis_server_obj, myredisOnMessage, params, "SUBSCRIBE unitsd_channel");
    redisAsyncCommand(redis_server_obj, myredisOnMessage, params, "SUBSCRIBE ordersd_channel");
    redisAsyncCommand(redis_server_obj, myredisOnMessage, params, "SUBSCRIBE webapi_channel");
    redisAsyncCommand(redis_server_obj, myredisOnMessage, params, "SUBSCRIBE wsint_channel");

    return 0;
}

void myredisPubConnectCallback(const redisAsyncContext *c, int status) {
    if (status != REDIS_OK) {
        //ev_break(EV_DEFAULT_ EVBREAK_ALL);
        syslog(LOG_ERR, "REDIS PUB: Connecting to server error: %s", c->errstr);
        redis_pubserver_connected = 0;
    } else {
        redis_pubserver_connected = 1;
        syslog(LOG_INFO, "REDIS PUB: Connected!");
    }
}

void myredisPubDisconnectCallback(const redisAsyncContext *c, int status) {
            
    //ev_break(EV_DEFAULT_ EVBREAK_ALL);
    if (status != REDIS_OK) {
        syslog(LOG_ERR, "REDIS PUB: Disconnecting from server error: %s", c->errstr);
    } else {
        syslog(LOG_INFO, "REDIS PUB: Disconnected!");
    }
    redis_pubserver_connected = 0;
}


int redis_pubconnect_server(struct server_params *params) {
    syslog(LOG_DEBUG, "REDIS PUB: Connecting to server...");

    redis_pubserver_connected = 1;
    redis_pubserver_obj = redisAsyncConnect("localhost", 6379);
    if (redis_pubserver_obj->err) {
        syslog(LOG_ERR, "REDIS PUB: Connecting to server failed: %s", redis_pubserver_obj->errstr);
        return 1;
    }

    redisLibevAttach(EV_DEFAULT_ redis_pubserver_obj);
    redisAsyncSetConnectCallback(redis_pubserver_obj, myredisPubConnectCallback);
    redisAsyncSetDisconnectCallback(redis_server_obj, myredisPubDisconnectCallback);
    return 0;
}

static void timeout_cb (struct ev_loop *loop, ev_periodic *w, int revents) {
    sem_wait(&redis_srv_args->server_params->sem);
    if (redis_server_connected == 0) 
        redis_connect_server(redis_srv_args->server_params);
    if (redis_pubserver_connected == 0) 
        redis_pubconnect_server(redis_srv_args->server_params);
    sem_post(&redis_srv_args->server_params->sem);
}



void * redis_evloop_start (void *arguments) {
    struct thread_arg_struct *args = arguments;

    syslog(LOG_INFO, "REDIS: Starting evloop");
    redis_srv_args = args;

    redis_connect_server(redis_srv_args->server_params);

    ev_periodic mtimeout;
    ev_periodic_init (&mtimeout, timeout_cb, 0., 0.5, 0);
    ev_periodic_start (EV_DEFAULT_ &mtimeout);
    ev_loop(EV_DEFAULT_ 0);

    pthread_exit(NULL);
}


