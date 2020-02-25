#include <errno.h> 
#include <stdio.h> 
#include <stdlib.h> 
#include <string.h> 
#include <syslog.h>
#include <sys/time.h>
#include <stdlib.h>
//#include <malloc.h>

/* TCP Server libs */

/* Local includes */
#include "config.h"
#include "parson.h"




    
void ipv4_dumps(char *ip, char *bytes) {
    sprintf(ip, "%d.%d.%d.%d", (int)(bytes[0] & 0xff), (int)(bytes[1] & 0xff), (int)(bytes[2] & 0xff), (int)(bytes[3] & 0xff));
}

void ipv4_parsen(char *bytes, char *ip, size_t len) {
    char *ptr = (char*)ip;
    int counter=0, val=0;
    while (ptr-ip <= len && counter < 4) {
        if (*ptr == '.' || *ptr == '\0') {
            bytes[counter] = (char) (val & 0xff);
            val=0;
            counter++;
        } else if (ptr[0] >= 48 && ptr[0] < 58) {
            val = val*10 + ptr[0]-48;
        }
        ptr++;
    }
    bytes[counter]='\0';
}
    
void ipv4_parse(char *bytes, char *ip) {
    ipv4_parsen(bytes, ip, strlen(ip));
}
    

JSON_Value* userslist_get_root(struct server_params *params) {
    //JSON_Value *root_value = json_parse_string(params->users_list);
    //if (root_value == NULL)
    //    root_value = json_parse_string("[]");
    JSON_Value *root_value = params->users_json;
    return root_value;
}


/*
 * Find/remove user
 * Search/remove first record in list, other items whould be removed
 * uid: user id
 * cid_remove: client id(socket id) to remove
 *    >  0: find and remove by clientid
 *    == 0: remove user at all; 
 *    <  0: just find user
 */
JSON_Object* userslist_getrm_user(struct server_params *params, JSON_Array *users, long uid, int cid_remove) {
    // Found first user, remove others:
    int found = 0;
    JSON_Object *j_user, *result = NULL, *j_client;
    for (int i=0; i<json_array_get_count(users); i++) {
        j_user = json_array_get_object(users, i);
        int uid_ = json_object_get_number(j_user, "uid");
        const char *host_ = json_object_get_string(j_user, "host");
        int port_ = json_object_get_number(j_user, "port");

        if (strncmp(host_, params->listenIpAddress, strlen(host_)) == 0 && port_ == params->listenPort && uid == uid_) {
            // First founded:
            if (found == 0 && cid_remove < 0) {
                result = j_user;
                found = 1;
            // Remove:
            } else {
                int client_count = 0; // User will be removed if client_count == 0
                                      // if cid_remove == 0 or if cid_remove > 0  but it's a last client

                // First founded, remove by client id:
                if (found == 0 && cid_remove > 0) {
                    JSON_Array *clients = json_object_get_array(j_user, "clients");
                    for (int j=0; j<json_array_get_count(clients); j++) {
                        j_client = json_array_get_object(clients, j);
                        int cid_ = json_object_get_number(j_client, "id");
                        if (cid_ == cid_remove)
                            json_array_remove(clients, j);
                    }
                    client_count = json_array_get_count(clients);
                } 

                if (client_count == 0) {
                    json_array_remove(users, i);
                    i--;

                // Removed client, but user have other clients:
                } else if (found == 0) {
                    result = j_user;
                    found = 1;
                }
            }
        }
    }
    return result;
}




/*
 * USERS LIST MANAGER
 * add_it == 0: Remove user from list(by client_t->client_info->sock
 * add_it == 1: Add/Update user in list, set parameters for client:
 * href: iser current location href(browser)
 * is_active: user looks on the page or browsing somewear else
 */


int userslist_mng(struct server_params *params, mylist_item *client_t, int add_it, int is_active, char *href) {

    if (client_t->client_info == NULL || client_t->client_info->user == NULL)
        return -1;

    char *login = client_t->client_info->user->name;

    long uid = client_t->client_info->user->uid;
    if (uid < 0)
        return -1;
        
    JSON_Value *root_value = userslist_get_root(params);
    JSON_Array *users = json_value_get_array(root_value);

    // We should remove user by clientid anyway, but we will add it back if add_it == 1
    JSON_Object *j_user = userslist_getrm_user(params, users, uid, client_t->client_info->sock);

    int clients_count = 0;

    // Set user parameters:
    if (add_it == 1) {
        // User is not exist, create:
        if (j_user == NULL) {
            JSON_Value *j_user_root = json_value_init_object();
            j_user = json_value_get_object(j_user_root);
            // Set clients array:
            json_object_set_value(j_user, "clients", json_parse_string("[]"));
            json_array_append_value(users, j_user_root);
        }

        json_object_set_string(j_user, "name", login);
        json_object_set_string(j_user, "host", params->listenIpAddress);
        json_object_set_number(j_user, "port", params->listenPort);
        json_object_set_number(j_user, "uid", uid);

        // Set client(id: client_t->client_info->sock) parameters: id, ip, href, is_active
        JSON_Value *j_client_root = json_value_init_object();
        JSON_Object *j_client = json_value_get_object(j_client_root);
        json_object_set_number(j_client, "id", client_t->client_info->sock);
        json_object_set_number(j_client, "active", is_active);
        json_object_set_string(j_client, "href", href);

        char ip[16] = {'\0'};
        ipv4_dumps(ip, client_t->client_info->ip);
        json_object_set_string(j_client, "ip", ip);
         
        // Append client to userSet:
        JSON_Array *clients = json_object_get_array(j_user, "clients");
        json_array_append_value(clients, j_client_root);
        clients_count = json_array_get_count(clients);

    } else if (j_user != NULL) {
        JSON_Array *clients = json_object_get_array(j_user, "clients");
        clients_count = json_array_get_count(clients);
    }


    // Save dump as JSON string:
    // clear old data:
    if (params->users_list != NULL)
        free(params->users_list);

    syslog(LOG_INFO, "USERSLIST CHANGED0: %s", params->users_list);
    // Count size of new value and set it:
    size_t new_size = json_serialization_size(root_value)+1;
    params->users_list = (char*)malloc(sizeof(char)*new_size);
    if (JSONSuccess == json_serialize_to_buffer(root_value, params->users_list, new_size)) {
        params->users_list[new_size] = '\0';
        syslog(LOG_INFO, "USERSLIST CHANGED1: %s", params->users_list);
        syslog(LOG_INFO, "USERSLIST CHANGED[COUNT=%zu]: SIZE: %zu", json_array_get_count(users), new_size);
    } else {
        syslog(LOG_ERR, "USERSLIST CHANGED, CANT WRITE! [COUNT=%zu]: SIZE: %zu", json_array_get_count(users), new_size);
    }


    // On user removed:
    if (clients_count == 0) {
        return 0;

    // On client disconnected:
    } else if (add_it == 0 && clients_count > 0) {
        return 1;

    // On new user login:
    } else if (add_it == 1 && clients_count == 1) {
        return 2;

    // On new user append:
    } else if (add_it == 1 && clients_count > 1) {
        return 3;
    }

    return -2;
}
    


int userslist_mng_chatanswer(struct server_params *params, mylist_item *client_t, int add_it, int is_active, char *href) {
    int state = userslist_mng(params, client_t, add_it, is_active, href);

    if (state < 0)
        return state;

    // WRITE NEW MESSAGE TO CHAT:
    JSON_Value *root_value = json_value_init_object();
    JSON_Object *root_object = json_value_get_object(root_value);
    char *serialized_string = NULL;
    json_object_set_string(root_object, "ident", "webchat");
    json_object_set_string(root_object, "cmd", "userslist_changed");
    json_object_set_string(root_object, "login", client_t->client_info->user->name);
    json_object_set_number(root_object, "errno", 0);
    json_object_set_number(root_object, "uid", client_t->client_info->user->uid);

    // On user removed:
    if (state == 0) {
        json_object_set_string(root_object, "error", "quit");
        serialized_string = json_serialize_to_string(root_value);
        params->ws_func_all_clients_send_message(params->clients_list_start, serialized_string);

    // On client disconnected:
    } else if (state == 1) {
        json_object_set_string(root_object, "error", "disconnected");
        serialized_string = json_serialize_to_string(root_value);
        params->ws_func_all_clients_send_message(params->clients_list_start, serialized_string);


    // On new user login:
    } else if (state == 2) {
        json_object_set_string(root_object, "error", "login");
        serialized_string = json_serialize_to_string(root_value);
        params->ws_func_all_clients_send_message(params->clients_list_start, serialized_string);


    // On new user append:
    } else if (state == 3) {
        json_object_set_string(root_object, "error", "connected");
        serialized_string = json_serialize_to_string(root_value);
        params->ws_func_all_clients_send_message(params->clients_list_start, serialized_string);
    }

    json_free_serialized_string(serialized_string);
    json_value_free(root_value);

    return state;
}
