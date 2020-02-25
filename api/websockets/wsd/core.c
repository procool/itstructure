#include <syslog.h>
#include <unistd.h>
#include <stdlib.h>
// #include <malloc.h>
#include <pthread.h>
#include <semaphore.h>
#include <string.h>

#include "config.h"
#include "core.h"
#include "bb.h"

#include "parson.h"



/*
 * Process client sessions:
 */

struct mylist_item *s_core_process_sessions[MAX_SESSIONS_CHECK];


int core_process_sessions(struct server_params *srv_params, int counter) {
    int i;
    for (i=0; i<counter; i++) {
        user_info *user = bb_check_session(srv_params->passport_host, srv_params->passport_port, s_core_process_sessions[i]->client_info->user->session);
        if (user != NULL) {
            syslog(LOG_INFO, "CORE PROCESS SESSION: %s: PASSED! UID: %ld", s_core_process_sessions[i]->client_info->user->session, user->uid);
            s_core_process_sessions[i]->client_info->user->uid=user->uid;
            s_core_process_sessions[i]->client_info->user->name=(char *)malloc(sizeof(char)*strlen(user->name));
            strcpy(s_core_process_sessions[i]->client_info->user->name, user->name);
            // Add user to users list:
            srv_params->userslist_mng_chatanswer(srv_params, s_core_process_sessions[i], 1, 0, "");

            JSON_Value *root_value = json_value_init_object();
            JSON_Object *root_object = json_value_get_object(root_value);
            char *serialized_string = NULL;

            json_object_set_string(root_object, "ident", "webchat");
            json_object_set_string(root_object, "cmd", "connection");
            json_object_set_string(root_object, "error", "Ok");
            json_object_set_number(root_object, "errno", 0);
            json_object_set_number(root_object, "uid", user->uid);
            json_object_set_string(root_object, "login", s_core_process_sessions[i]->client_info->user->name);

            serialized_string = json_serialize_to_string(root_value);
            srv_params->ws_func_client_send_message(s_core_process_sessions[i], serialized_string);
            json_free_serialized_string(serialized_string);
            json_value_free(root_value);
            free(user);


        // Auth failed:
        } else {
            syslog(LOG_INFO, "CORE PROCESS SESSION: [%d] Prepare to close...", s_core_process_sessions[i]->client_info->sock);
            s_core_process_sessions[i]->client_info->close_it = 1; // Close client
            srv_params->userslist_mng_chatanswer(srv_params, s_core_process_sessions[i], 0, 0, ""); // Remove user
        }
    }
    return 0;
}


int core_process_users(struct server_params *srv_params) {
    mylist_item *client_t = srv_params->clients_list_start;

    // Process all users:
    int counter = 0;

    while (client_t != NULL) {
        if (client_t->client_info == NULL) {
            client_t = client_t->next;
            continue;
        }
        if (client_t->client_info->close_it != 0) {
            client_t = client_t->next;
            continue;
        }

        if (client_t->client_info->ws_opened && 
            client_t->client_info->user != NULL && 
            client_t->client_info->user->uid < 0 && 
            client_t->client_info->user->session != NULL &&
            counter < MAX_SESSIONS_CHECK
        ) {
            s_core_process_sessions[counter] = client_t;
            counter += 1;
        }

        /* Load next item */
        client_t = client_t->next;
    }

    // Process user sessions:
    core_process_sessions(srv_params, counter);

    return 0;
}


void * core_loop_start (void *arguments) {
    struct thread_arg_struct *args = arguments;

    if (args->server_params->clients_list_start) {
    }

    do {
        sem_wait(&args->server_params->sem);
        // Process users:
        core_process_users(args->server_params);
        sem_post(&args->server_params->sem);
        usleep(1000000);
    } while (1);

    pthread_exit(NULL);
}


