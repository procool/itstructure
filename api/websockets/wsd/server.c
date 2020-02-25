#include <errno.h> 
#include <stdio.h> 
#include <stdlib.h> 
#include <string.h> 
#include <syslog.h>
#include <assert.h>
#include <sys/time.h>
#include <time.h>
#include <stdlib.h>
//#include <malloc.h>

/* TCP Server libs */
#include <netdb.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <fcntl.h> // for open
#include <unistd.h> // for close
#include <arpa/inet.h> // inet_ntop

/* Local includes */
#include "server.h"
#include "config.h"
#include "libsha.h"
#include "ws.h"
#include "redis_thread.h"
#include "users.h"
#include "parson.h"




/* Client address structure: */


struct tserver_info *server_info;



int set_nonblock(int socket) {
    int flags;
    flags = fcntl(socket,F_GETFL,0);
    assert(flags != -1);
    fcntl(socket, F_SETFL, flags | O_NONBLOCK);
    return 0;
}


int init_server(struct server_params *params) {
    int status;
    struct addrinfo *server;
    char port[15];

    server_info = (tserver_info *)malloc(sizeof(tserver_info));

    int len;

    if (params->listenPort == 0)
        params->listenPort = DEFAULT_PORT;

    if (0 == strcmp(params->listenIpAddress, "")) {
        len = strlen((char*)DEFAULT_HOST);
        strncpy(params->listenIpAddress, DEFAULT_HOST, len);
    }

    syslog(LOG_INFO, "Starting server: %s:%d", params->listenIpAddress, params->listenPort);

    snprintf(port, 15, "%d", params->listenPort);

    server_info->sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP); 

    if (-1 == server_info->sock) { 
        syslog(LOG_ERR, "Starting server Failed: %s", strerror(errno));
        close(server_info->sock); 
        exit(EXIT_FAILURE); 
    } 

    /* getaddrinfo(3) hints: */
    server_info->hints = (struct addrinfo*) calloc(1, sizeof(struct addrinfo)); 
    server_info->hints->ai_family = AF_INET;
    server_info->hints->ai_socktype = SOCK_STREAM;
    server_info->hints->ai_protocol = 6; 
    server_info->hints->ai_flags = AI_PASSIVE;

    status = getaddrinfo(params->listenIpAddress, port, server_info->hints, &server); 
    if (0 != status) { 
        syslog(LOG_ERR, "Address error: %s", gai_strerror(status)); 
        fprintf(stderr, "Address error: %s\n", gai_strerror(status));
        free(server_info->hints); 
        close(server_info->sock); 
        exit(EXIT_FAILURE); 
    } 

    if (setsockopt(server_info->sock, SOL_SOCKET, SO_REUSEADDR, &(int){ 1 }, sizeof(int)) < 0) {
        free(server_info->hints);
        close(server_info->sock);
        exit(EXIT_FAILURE);
    }

    if (-1 == bind(server_info->sock, server->ai_addr, server->ai_addrlen)) { 
        syslog(LOG_ERR, "Error on BIND[%s:%d]: %s", params->listenIpAddress, params->listenPort, strerror(errno)); 
        fprintf(stderr, "Error on BIND[%s:%d]: %s\n", params->listenIpAddress, params->listenPort, strerror(errno)); 
        free(server_info->hints); 
        close(server_info->sock); 
        exit(EXIT_FAILURE); 
    } 
    if (-1 == listen(server_info->sock, 128)) { 
        syslog(LOG_ERR, "Error on LISTEN: %s", strerror(errno)); 
        fprintf(stderr, "Error on LISTEN: %s\n", strerror(errno)); 
        free(server_info->hints); 
        close(server_info->sock); 
        exit(EXIT_FAILURE); 
    } 



    /* Set nonblock on server socket: */
    set_nonblock(server_info->sock);

    syslog(LOG_INFO, "Started! Socket: %d", server_info->sock);
    return 0;
}

int start_reactor(struct server_params *params) {
    do {
        sem_wait(&params->sem);

        /* Error on clients processing: */
        if (process_clients(params) < 0) {
            sem_post(&params->sem);
            syslog(LOG_INFO, "Reactor error!");
            return -1;
        }
        sem_post(&params->sem);
        usleep( 10000 );
    } while (1);
    return 0;
}


void * start_server (void *arguments) {
    struct thread_arg_struct *args = arguments;
    struct server_params *params = args->server_params;

    syslog(LOG_INFO, "Starting server...");
    do {
        syslog(LOG_INFO, "Initialization server socket...");
        init_server(params);
        syslog(LOG_INFO, "Starting server reactor...");
        start_reactor(params);

        syslog(LOG_INFO, "Closing server socket...");
        free(server_info->hints); 
        close(server_info->sock); 

        syslog(LOG_INFO, "Sleeping before new server creation iteration...");
        usleep( 10000000 ); // Sleep 10 seconds
    } while (1);
}

int stop_server() {
    syslog(LOG_INFO, "Closing socket...");
    close(server_info->sock);
    return 0;
}

int close_client(struct server_params *params, mylist_item *client_t) {

    // Try to remove client from users list:
    params->userslist_mng_chatanswer(params, client_t, 0, 0, "");

    if (client_t->client_info == NULL)
        return -1;
    syslog(LOG_DEBUG, "Close client[%d]...", client_t->client_info->sock);
    close(client_t->client_info->sock);
    //shutdown(client_t->client_info->sock, 2);
    io_buff_free(client_t->client_info->buffer_read, 0);
    io_buff_free(client_t->client_info->buffer_write, 0);

    if (client_t->client_info->header_readed == 1) {
        free(client_t->client_info->header_data);
    }

    if (client_t->client_info->user != NULL) {
        if (client_t->client_info->user->session != NULL) {
            free(client_t->client_info->user->session);
        }
        free(client_t->client_info->user);
    }

    int si = client_t->client_info->sock;
    free(client_t->client_info->address);
    mylist_remove_item(client_t);
    syslog(LOG_INFO, "Close client %d success!", si);
    return 0;
}


int close_clients(struct server_params *params) {
    syslog(LOG_DEBUG, "Closing all clients...");
    mylist_item *client_t = params->clients_list_start;
    while (client_t != NULL) {
        close_client(params, client_t);
        client_t = client_t->next;
    }
    syslog(LOG_INFO, "All clients are closed!");
    return 0;
}



        
/*
 * INIT WebSockets connection:
 */
int process_client_init_ws(struct server_params *params, mylist_item *client_t) {
    char *p = NULL;

    if ((p = strstr(client_t->client_info->header_data, "Sec-WebSocket-Key:")) != NULL) {
        char resultstr[64] = {0,};
        int i = 0, it = 0;
        for (i = 19; it < 24; i++, it++) {
            resultstr[it] = p[i];
        }
        strcat(resultstr, GUIDKey);

        unsigned char temp[SHA_DIGEST_LENGTH] = {0,};
        SHA1(temp, resultstr, strlen(resultstr));

        ////////////////////////////Base64////////////////////////////////////
        unsigned char key_out[64] = {0,};
        base64_encode(temp, key_out, sizeof(temp));

        syslog(LOG_INFO, "Key_for_client: %s", key_out);

        int len_ = (int) strlen((const char *) response_ws) + 64 + 4;
        char *resp = (char *)malloc(sizeof(char)*(len_+1));
        memset(resp, 0, len_+1);
        resp[len_+1] = '\0';
        snprintf(resp, len_, "%s%s%s", response_ws, key_out, "\r\n\r\n");
        io_buff_push(client_t->client_info->buffer_write, resp, sizeof(char) * strlen(resp));
        free(resp);
        syslog(LOG_DEBUG, "WS started for client");
        client_t->client_info->ws_opened = 1;
        return 0;
    }
    io_buff_push(client_t->client_info->buffer_write, response_500, (int)strlen(response_500));
    io_buff_push(client_t->client_info->buffer_write, TPL_ERR500, (int)strlen(TPL_ERR500));
    return -1;
}



/*
 * Send WebSockets message:
 */

int process_client_ws_sendn_frame(mylist_item *client_t, char *message, size_t message_size, int opcode) {
    int msg_size_len = 1;
    char msg_size[4];

    if (message_size <= 125) {
        msg_size[0] = (char)message_size;
    } else if (message_size > 125 && message_size <= 65535) {
        msg_size[0] = (char) WS_PAYLOAD_LEN16;
        msg_size[1] = (char)(message_size >> 8);
        msg_size[2] = (char)(message_size & 0xff);
        msg_size_len = 3;
    /*
    } else if (message_size > 65535 && message_size < 184467440738 *10000000) {
        msg_size[0] = (char) WS_PAYLOAD_LEN64;
        msg_size[1] = (char)(message_size >> 16);
        msg_size[2] = (char)(message_size >> 8) & 0xff;
        msg_size[3] = (char)message_size & 0xffff;
        msg_size_len = 4;
    */
    } else {
//WS_CONTINUATION_FRAME
    //        char *msg_ = (char *)malloc(sizeof(char)*165535);
     //       memset(msg_, 'A', 165535);

     //       process_client_ws_send_frame(client_t, "Connection opened!", WS_TEXT_FRAME);
     //       process_client_ws_send_frame(client_t, msg_, WS_TEXT_FRAME);

        // Message too big!
        return -1;
    }

    int answer_size = message_size + msg_size_len + 1;
    char *answer = (char *)malloc(sizeof(char)*answer_size);
    memset(answer, '\0', answer_size);
    answer[0] = WS_FIN | opcode;
    memcpy(answer+1, msg_size, sizeof(char)*msg_size_len); 
    memcpy(answer+msg_size_len+1, message, sizeof(char)*message_size); 
    //syslog(LOG_INFO, "WS SEND MESSAGEXX0 SIZE_T: %d SIZE: %d ALLSIZE: %d TEXT: '%s'", (int)msg_size_len, (int)message_size, (int) answer_size, answer);
    //syslog(LOG_INFO, "WS SEND MESSAGEXX1 SENDBUF: %d: %s", client_t->client_info->buffer_write->len, client_t->client_info->buffer_write->value);

    // Send message only if write buffer is not overflow:
    if (client_t->client_info->buffer_write->len <= MAX_OUTBUFF_SIZE)
        io_buff_push(client_t->client_info->buffer_write, answer, answer_size);
    free(answer);
    return 0;
}


int process_client_ws_send_frame(mylist_item *client_t, char *message, int opcode) {
    size_t message_size = strlen((const char*)message);
    return process_client_ws_sendn_frame(client_t, message, message_size, opcode);
}


/* 
 * Send WebSockets message (TEXT):
 */
void ws_client_send_message(mylist_item *client_t, char *message) {
    if (client_t->client_info == NULL || client_t->client_info->close_it == 1) 
        return;

    // Sending message:
    process_client_ws_send_frame(client_t, message, WS_TEXT_FRAME);
}


/*
 * Send WebSockets message (TEXT) to all clients:
 */
void ws_all_clients_send_message(mylist_item *client_t, char *message) {

    const char *j_message = NULL;
    long from_uid=0, to_uid=0;
    int mtype=0;

    // Try to Parse incoming data:
    JSON_Value *j_root = json_parse_string((const char*) message);
    if (j_root != NULL) {
        JSON_Object *j_data = json_value_get_object(j_root);
        j_message = json_object_get_string(j_data, "message");
        mtype = json_object_get_number(j_data, "type");
        from_uid =json_object_dotget_number(j_data, "from.uid");
        to_uid = json_object_dotget_number(j_data, "to.uid");

        if (j_message != NULL) {
            // Private message:
            if (to_uid != 0) {
                syslog(LOG_INFO, "CHAT [UID:%ld] -> UID:%ld: [%d] %s", from_uid, to_uid, mtype, j_message);
            } else {
                syslog(LOG_INFO, "CHAT [UID:%ld] -> PUB: [%d] %s", from_uid, mtype, j_message);
            }
        }
        json_value_free(j_root);
    } 

    while (client_t != NULL) {
        if (client_t->client_info == NULL || client_t->client_info->close_it == 1) {
            client_t = client_t->next;
            continue;
        }

        // Authed user:
        if (client_t->client_info->user != NULL && client_t->client_info->user->uid >= 0) {
            if (to_uid == 0 || (client_t->client_info->user->uid == to_uid)) 
                ws_client_send_message(client_t, message);
        }

        /* Load next item */
        client_t = client_t->next;
    }
}


/*
 * Process WebSockets Message from client:
 */
int process_client_ws_message(struct server_params *params, mylist_item *client_t, char opcode, const char *payload, unsigned int payload_len) {
    syslog(LOG_INFO, "WS RECV MESSAGE, Payload length: %d, text: %s", payload_len, payload);
    //process_client_ws_send_frame(client_t, (char*)payload, WS_TEXT_FRAME);


    const char* pl = payload;
    // New sessin check:
    if (strlen(pl) < 263 && strlen(pl) > 8 && (strstr(pl, "session=")) == pl) {
        syslog(LOG_INFO, "WS RECV SESSION CHECK");
        process_client_ws_send_frame(client_t, "SESSION_CHECK", WS_TEXT_FRAME);
        client_t->client_info->user = (user_info *)malloc(sizeof(user_info));
        client_t->client_info->user->session = (char *)malloc( sizeof(char)*(strlen(pl)-8) );
        strcpy(client_t->client_info->user->session, pl+8);
        client_t->client_info->user->uid = -1;

    // Connection not enstablished:
    } else if (client_t->client_info == NULL || client_t->client_info->user == NULL) {
        ws_client_send_message(client_t, "{\"cmd\":\"connection\",\"errno\":-1,\"error\":\"connection_not_enstablished\"}");

    // Not authorized:
    } else if (client_t->client_info->user->uid <= 0) {
        ws_client_send_message(client_t, "{\"cmd\":\"connection\",\"errno\":-1,\"error\":\"notauthorized\"}");
            
    // Process user WS message as JSON:
    } else if (client_t->client_info->user->name != NULL) {
        int mtype=0;
        const char *j_message = NULL;


        // Try to Parse incoming data:
        JSON_Value *j_root = json_parse_string(payload);
        if (j_root == NULL) {
            // Can not parse JSON:
            return 0;
        }
        JSON_Object *j_data = json_value_get_object(j_root);
        const char *j_cmd = json_object_get_string(j_data, "cmd");

        // No command in message:
        if (j_cmd == NULL){

        // CHAT MESSAGE INCOMING:
        } else if (strncmp(j_cmd, "message", 7) == 0) {
            j_message = json_object_get_string(j_data, "message");
            mtype = json_object_get_number(j_data, "type");
            long from_uid =json_object_dotget_number(j_data, "from.uid");
            long to_uid = json_object_dotget_number(j_data, "to.uid");

            syslog(LOG_INFO, "CHAT [UID:%ld] <- (%d) %s", client_t->client_info->user->uid, mtype, j_message);

            // Update FROM, set uid:
            json_object_dotset_number(j_data, "from.uid", client_t->client_info->user->uid);
            json_object_dotset_string(j_data, "from.login", client_t->client_info->user->name);
            json_object_set_string(j_data, "ident", "webchat");
            size_t message_size = json_serialization_size(j_root)+1;
            char *message = (char*)malloc(sizeof(char)*message_size);
            if (JSONSuccess == json_serialize_to_buffer(j_root, message, message_size)) {
                message[message_size] = '\0';
                myredis_publish(message);
            }
            free(message);


        // Show list of users to client:
        } else if (strncmp(j_cmd, "userslist", 9) == 0) {
            JSON_Value *root_value = json_value_init_object();
            JSON_Object *root_object = json_value_get_object(root_value);
            char *serialized_string = NULL;
            json_object_set_string(root_object, "ident", "webchat");
            json_object_set_string(root_object, "cmd", "userslist");
            json_object_set_string(root_object, "error", "Ok");
            json_object_set_number(root_object, "errno", 0);
            if (params->users_list == NULL) 
                json_object_set_value(root_object, "result", json_parse_string("[]"));
            else
                json_object_set_value(root_object, "result", json_parse_string(params->users_list));
            serialized_string = json_serialize_to_string(root_value);
            ws_client_send_message(client_t, serialized_string);
            json_free_serialized_string(serialized_string);
            json_value_free(root_value);


        // Update client status in userslist:
        } else if (strstr(j_cmd, "status") != NULL) {
            const char *href = json_object_get_string(j_data, "href");
            int is_active = json_object_get_number(j_data, "active");
            params->userslist_mng(params, client_t, 1, is_active, href);

            // WRITE NEW MESSAGE TO CHAT:
            JSON_Value *root_value = json_value_init_object();
            JSON_Object *root_object = json_value_get_object(root_value);
            char *serialized_string = NULL;
            json_object_set_string(root_object, "ident", "webchat");
            json_object_set_string(root_object, "cmd", "user_status");
                        
            json_object_set_string(root_object, "login", client_t->client_info->user->name);
            json_object_set_number(root_object, "errno", 0);
            json_object_set_number(root_object, "uid", client_t->client_info->user->uid);
            json_object_set_number(root_object, "cid", client_t->client_info->sock);
            json_object_set_number(root_object, "active", is_active);
            json_object_set_string(root_object, "href", href);
            json_object_set_string(root_object, "error", "Ok");

            json_object_set_string(root_object, "host", params->listenIpAddress);
            json_object_set_number(root_object, "port", params->listenPort);

            serialized_string = json_serialize_to_string(root_value);
            //params->ws_func_all_clients_send_message(params->clients_list_start, serialized_string);
            myredis_publish(serialized_string);

            json_free_serialized_string(serialized_string);
            json_value_free(root_value);
        }

        json_value_free(j_root);
    }

    return 0;
}


/*
 * Process WebSockets TEXT Frame from client:
 */
int process_client_ws_text_frame(struct server_params *params, mylist_item *client_t, char opcode, unsigned char *payload, unsigned char payload_len) {
    syslog(LOG_DEBUG, "WS RECV TEXT FRAME, Payload length: %d, text: %s", payload_len, payload);

    // PING Frame:
    if (opcode == WS_PING_FRAME) {
        process_client_ws_send_frame(client_t, (char*)payload, WS_PONG_FRAME);
        syslog(LOG_DEBUG, "WS CLIENT %d PING", client_t->client_info->sock);

    } else if(payload_len == 4 && payload[0] == 'p' && payload[1] == 'i' && payload[2] == 'n' && payload[3] == 'g') {
        char ping[] = {0x48, 0x65, 0x6c, 0x6c, 0x6f}; // Ping not masqurated, send this word with PONG answer
        // char ping[] = {'H', 'e', 'l', 'l', 'o'}; // like this
        process_client_ws_send_frame(client_t, ping, WS_TEXT_FRAME);
        syslog(LOG_DEBUG, "WS CLIENT %d PING(MSG)", client_t->client_info->sock);

    // Close connection command:
    } else if (payload_len == 5 && payload[0] == 'c' && payload[1] == 'l' && payload[2] == 'o' && payload[3] == 's' && payload[4] == 'e') {
        syslog(LOG_INFO, "WS CLIENT %d CLOSE", client_t->client_info->sock);
        client_t->client_info->close_it = 1;
    } else if (opcode == WS_TEXT_FRAME) {
        process_client_ws_message(params, client_t, opcode, (const char*)payload, payload_len);
    }

    return 0;
}




        


        
/*
 * Process WebSockets data from client:
 */
int process_client_ws(struct server_params *params, mylist_item *client_t) {

    int cursor = 2;

    // Wait for first readed_count bytes of message:
    if (client_t->client_info->buffer_read->len < 2) 
        return 0;

    char *inbuf = client_t->client_info->buffer_read->value;

    char masking_key[4] = {0,}; // It would be Mask 
    unsigned char payload_len; // Message content length, without spechial bytes, or digits 126 or 127

    char opcode = inbuf[0] & WS_OPCODE; // Frame type

    char b_fin, b_rsv1, b_rsv2, b_rsv3;
    b_fin  = inbuf[0] & WS_FIN;
    b_rsv1 = inbuf[0] & 0x02;
    b_rsv2 = inbuf[0] & 0x04;
    b_rsv3 = inbuf[0] & 0x08;
    payload_len = inbuf[1] & 0x7F;

    syslog(LOG_ERR, "WS INCOMING: (%d bytes) %s", client_t->client_info->buffer_read->len, inbuf);
    syslog(LOG_DEBUG, "WS FIN: 0x%02X", b_fin);
    syslog(LOG_DEBUG, "WS RSV1: 0x%02X", b_rsv1);
    syslog(LOG_DEBUG, "WS RSV2: 0x%02X", b_rsv2);
    syslog(LOG_DEBUG, "WS RSV3: 0x%02X", b_rsv3);
    syslog(LOG_DEBUG, "WS Opcode: 0x%02X", opcode);
    syslog(LOG_DEBUG, "WS Payload Length: %d", payload_len);
    syslog(LOG_DEBUG, "WS[%d] RECV MESSAGE: 0x%02x 0x%02x 0x%02x 0x%02x 0x%02x 0x%02x 0x%02x 0x%02x", client_t->client_info->sock, inbuf[0], inbuf[1], inbuf[2], inbuf[3], inbuf[4], inbuf[5], inbuf[6], inbuf[7]);

    // Close connection code:
    if (opcode == WS_CLOSING_FRAME) {
        syslog(LOG_INFO, "WS RECV opcode - 0x08, close cleant %d", client_t->client_info->sock);
        client_t->client_info->close_it = 1;
        return 0;
    }

    // RECV PONG masqurated
    if (opcode != WS_PONG_FRAME && opcode != WS_TEXT_FRAME) {
        io_buff_push(client_t->client_info->buffer_write, WS_WRONG_MESSAGE, (int)strlen(WS_WRONG_MESSAGE));
        syslog(LOG_ERR, "WS[%d] RECV WRONG MESSAGE! OPCODE: %d", client_t->client_info->sock, opcode);
        syslog(LOG_ERR, "WS[%d] RECV WRONG MESSAGE: 0x%02x 0x%02x 0x%02x 0x%02x 0x%02x", client_t->client_info->sock, inbuf[0], inbuf[1], inbuf[2], inbuf[3], inbuf[4]);
	//client_t->client_info->close_it = 1;
    } else {
        // Wait for needed bytes:
        if (payload_len == 126)
            cursor += 2;
        else if (payload_len == 127)
            cursor += 8;

        cursor += 4; // Mask size

        // Wait for header data:
        if (client_t->client_info->buffer_read->len < cursor) 
            return 0;

        unsigned char payload[SW_BUF] = {0,};

        if (payload_len < 126) {
            masking_key[0] = inbuf[2];
            masking_key[1] = inbuf[3];
            masking_key[2] = inbuf[4];
            masking_key[3] = inbuf[5];

            // Wait for message:
            if (client_t->client_info->buffer_read->len < cursor+payload_len) 
                return 0;
            cursor += payload_len; 

            unsigned int i = 6, pl = 0;
            for(; pl < payload_len; i++, pl++) {
                payload[pl] = inbuf[i]^masking_key[pl % 4];
            }
            process_client_ws_text_frame(params, client_t, opcode, payload, payload_len);

        // Text message:
        } else if (payload_len == 126) {
            unsigned char len16[2] = {0,};
            unsigned int payload_len16 = 0;
            len16[0] = inbuf[2];
            len16[1] = inbuf[3];
            payload_len16 = (len16[0] << 8) | len16[1]; // Getting message length
            syslog(LOG_DEBUG, "WS[%d] RECV LEN: %d, %d: %d", client_t->client_info->sock, len16[0], len16[1], payload_len16);
            syslog(LOG_DEBUG, "WS[%d] RECV MESSAGEX: 0x%02x 0x%02x 0x%02x 0x%02x 0x%02x 0x%02x", client_t->client_info->sock, inbuf[2], inbuf[3], inbuf[4], inbuf[5], inbuf[6], inbuf[7]);

            masking_key[0] = inbuf[4];
            masking_key[1] = inbuf[5];
            masking_key[2] = inbuf[6];
            masking_key[3] = inbuf[7];


            // Wait for message:
            if (client_t->client_info->buffer_read->len < cursor + payload_len16)
                return 0;

            cursor += payload_len16; 

            unsigned int i = 8, pl = 0;
            for(; pl < payload_len16; i++, pl++) {
                payload[pl] = inbuf[i]^masking_key[pl % 4];
            }
            process_client_ws_message(params, client_t, opcode, (const char*) payload, payload_len16);


        // BIG Text message:
        } else if (payload_len == 127) {
/*
            unsigned long long payload_len64 =  (unsigned char)inbuf[2] << 54 |
                            (unsigned char)inbuf[3] << 48 |
                            (unsigned char)inbuf[4] << 40 |
                            (unsigned char)inbuf[5] << 32 |
                            (unsigned char)inbuf[6] << 24 |
                            (unsigned char)inbuf[7] << 16 |
                            (unsigned char)inbuf[8] << 8  |
                            (unsigned char)inbuf[9];
            unsigned long payload_len64 = ((inbuf[2] & 0xFFL) << 56) +
                            ((inbuf[3] & 0xFFL) << 48) +
                            ((inbuf[4] & 0xFFL) << 40) +
                            ((inbuf[5] & 0xFFL) << 32) +
                            ((inbuf[6] & 0xFFL) << 24) +
                            ((inbuf[7] & 0xFFL) << 16) +
                            ((inbuf[8] & 0xFFL) << 8)  +
                            (inbuf[9] << 0);
*/

            size_t payload_len64 = ((size_t)inbuf[2]) << 56;
            payload_len64 |= ((size_t)inbuf[3]) << 48;
            payload_len64 |= ((size_t)inbuf[4]) << 40;
            payload_len64 |= ((size_t)inbuf[5]) << 32;
            payload_len64 |= ((size_t)inbuf[6]) << 24;
            payload_len64 |= ((size_t)inbuf[7]) << 16;
            payload_len64 |= ((size_t)inbuf[8]) << 8;
            payload_len64 |= ((size_t)inbuf[9]);

            cursor += payload_len64; 
 
            masking_key[0] = inbuf[10];
            masking_key[1] = inbuf[11];
            masking_key[2] = inbuf[12];
            masking_key[3] = inbuf[13];

            // Wait for message:
            if (client_t->client_info->buffer_read->len < 14 + payload_len64)
                return 0;

            unsigned char *payload64 = (unsigned char*)malloc(sizeof(unsigned char)*payload_len64);
            unsigned int i = 14, pl = 0;
            for(; pl < payload_len64; i++, pl++) {
                payload64[pl] = inbuf[i]^masking_key[pl % 4];
            }
            process_client_ws_message(params, client_t, opcode, (const char*)payload64, payload_len64);
            free(payload64);
        }
    }

    // Clear readed bytes from incoming data:
    io_buff_get(client_t->client_info->buffer_read, NULL, cursor);
    syslog(LOG_DEBUG, "WS[%d] RECV FREE: %d bytes", client_t->client_info->sock, cursor);

    // Something else to read:
    if (client_t->client_info->buffer_read->len > 0) {
        return 2;
    }
    return 1;
}


/*
 * Process client request headers:
 */
int process_client_header(struct server_params *params, mylist_item *client_t) {
    //syslog(LOG_INFO, "OUTBUFF: %s", client_t->client_info->buffer_read->value);
    //syslog(LOG_INFO, "Processing HEADER: %s", client_t->client_info->header_data);
    //client_t->client_info->header_data

    char *xforwarded = strstr(client_t->client_info->header_data, "X-Forwarded-For:");
    if (xforwarded != NULL) {
        xforwarded = xforwarded+16;
        if (*xforwarded == ' ')
            xforwarded++;
        char *ptr = xforwarded;
        int len_ = 0;
        while(len_ < 16 && (*ptr=='.' || (*ptr>=48 && *ptr<58))) {
            len_++;
            ptr++;
        }
        ipv4_parsen(client_t->client_info->ip, xforwarded, len_);
    }

    if ((strstr(client_t->client_info->header_data, "GET / ")) != NULL) {
        io_buff_push(client_t->client_info->buffer_write, response, (int)strlen(response));
        io_buff_push(client_t->client_info->buffer_write, TPL_INDEX, (int)strlen(TPL_INDEX));
        client_t->client_info->close_it = 1;
    } else if ((strstr(client_t->client_info->header_data, "GET /messages/")) != NULL) {
        if (process_client_init_ws(params, client_t) < 0) {
            return -1;
        // Websockets initializated: 
        } else {
            process_client_ws_send_frame(client_t, "Connection opened!", WS_TEXT_FRAME);
            /*
            // Test messages stack:
            int i;
            //for (i=10; i < 65535; i+=10) {
            for (i=10; i < 6553; i+=10) {
            //for (i=200; i < 300; i+=1) {
                char *msg_ = (char *)malloc(sizeof(char)*i);
                memset(msg_, 'A', i);
                //process_client_ws_send_frame(client_t, msg_, WS_TEXT_FRAME);
                process_client_ws_sendn_frame(client_t, msg_, i, WS_TEXT_FRAME);
                //syslog(LOG_INFO, "Data from client!");
                free(msg_);
            }
            */
            // Test long message:
            //char *msg_ = (char *)malloc(sizeof(char)*65535);
            //memset(msg_, 'A', 65535);
            //process_client_ws_send_frame(client_t, msg_, WS_TEXT_FRAME);
            //free(msg_);
        }
    } else {
        io_buff_push(client_t->client_info->buffer_write, response_404, (int)strlen(response_404));
        io_buff_push(client_t->client_info->buffer_write, TPL_ERR404, (int)strlen(TPL_ERR404));
        client_t->client_info->close_it = 1;
    }
    return 0;
}


/*
 * Reading data from client:
 */
int process_client_read(struct server_params *params, mylist_item *client_t) {
    char buffer[1024];
    char *header_end;

    //syslog(LOG_INFO, "Data from client!");
    /* Read data from stream */
    memset(buffer, 0, 1024);
    int len = recv(client_t->client_info->sock, buffer, sizeof(buffer), 0);

    // No data, closing client:
    if (len < 0) { 
        if (errno == EWOULDBLOCK)
            return 0;
        return -1;
    }

    // EOF:
    if (len == 0) 
        return -1;

    io_buff_push(client_t->client_info->buffer_read, buffer, len);
    syslog(LOG_INFO, "RECV[%d]: (%d/%d) %s", client_t->client_info->sock, len, client_t->client_info->buffer_read->len, buffer);
    //fprintf(stderr, "RECV[%d]: (%d %lu/%d %lu) %s\n\n", client_t->client_info->sock, len, strlen(buffer), client_t->client_info->buffer_read->len, strlen(client_t->client_info->buffer_read->value), buffer);
    //fprintf(stderr, "RECV VALUE:[%d]: %s\n\n", client_t->client_info->sock, client_t->client_info->buffer_read->value);

    // Processing client on WS:
    if (client_t->client_info->ws_opened) {
        // Process data until something to read:
        int res = 2;
        do {
            res = process_client_ws(params, client_t);
            if (res < 0) {
                syslog(LOG_ERR, "PROCESS[%d]: process_client_ws failed!", client_t->client_info->sock);
                client_t->client_info->close_it = 1;
            }
        } while (res == 2);
        return res;
    }

    // Undefined method:
    if(!client_t->client_info->header_readed && client_t->client_info->buffer_read->len > 5 && 
        (strstr(client_t->client_info->buffer_read->value, "GET /")) == NULL) {
        return -1;
    }

    // Header too large:
    if (!client_t->client_info->header_readed && client_t->client_info->buffer_read->len > MAX_HEADER_LENGTH) {
        return -1;
    }

    // Test for header is readed:
    if(!client_t->client_info->header_readed) {
        header_end = strstr(client_t->client_info->buffer_read->value, "\r\n\r\n");
        //syslog(LOG_INFO, "HEADEREND: %s", header_end);
        if (header_end != NULL) {
            client_t->client_info->header_readed = 1;
            int header_len = header_end - client_t->client_info->buffer_read->value;
            client_t->client_info->header_data = (char *)malloc(sizeof(char)*(header_len+1));
            strncpy(client_t->client_info->header_data, client_t->client_info->buffer_read->value, sizeof(char)*header_len); // FIXME
            client_t->client_info->header_data[header_len] = '\0';
            //fprintf(stderr, "HEADER: %lu, %s\n\n", strlen(client_t->client_info->header_data), client_t->client_info->header_data);

            // Cut header from buffer, and store only content if exist:
            int content_len = strlen(client_t->client_info->buffer_read->value) - header_len - 4;
            if (content_len >= 0) {
                char *content_data = (char *)malloc(sizeof(char)*(content_len+1) );
                strncpy(content_data, header_end+4, sizeof(char)*content_len); // FIXME
                io_buff_free(client_t->client_info->buffer_read, 0);
                if (content_len > 0) {
                    io_buff_push(client_t->client_info->buffer_read, content_data, content_len);
                }
                free(content_data);
            }
            //fprintf(stderr, "CONTENT: %d, %s\n\n", client_t->client_info->buffer_read->len, client_t->client_info->buffer_read->value);

            if (process_client_header(params, client_t) < 0) {
                return -1;
            }
        }
    }

    return 0;
}



/*
 * Writing new data to client:
 */
int process_client_write(struct server_params *params, mylist_item *client_t) {
    if (client_t->client_info->buffer_write->len <= 0) {
        return 0;
    }

    int to_write_len = client_t->client_info->buffer_write->len;
    if (client_t->client_info->buffer_write->len > MAX_BUFF_WRITE) 
        to_write_len = MAX_BUFF_WRITE;

    size_t r = send(client_t->client_info->sock, client_t->client_info->buffer_write->value, to_write_len, 0);
    syslog(LOG_DEBUG, "SEND[%d]: %d/%d", client_t->client_info->sock, (int) r, to_write_len);
    //syslog(LOG_DEBUG, "SEND[%d]: %d/%d: %s", client_t->client_info->sock, (int) r, to_write_len, client_t->client_info->buffer_write->value);

    //io_buff_free(client_t->client_info->buffer_write, 0);
    if (r > 0)
        io_buff_get(client_t->client_info->buffer_write, NULL, r);
    
    return 0;
}





/*
 * Client processing:
 */
int process_client(struct server_params *params, mylist_item *client_t) {
    if (client_t->client_info == NULL)
        return 0;
    if (client_t->client_info->close_it == 1) 
        return 0;
    if (client_t->client_info->buffer_read->len <= 0) {
        return 0;
    }
    // Simple echo:
    //io_buff_push(client_t->client_info->buffer_write, client_t->client_info->buffer_read->value, client_t->client_info->buffer_read->len);
    //io_buff_free(client_t->client_info->buffer_read, 0);
    return 0;
}



/*
 * All clients processing:
 */
int process_clients(struct server_params *params) {

    socklen_t clientStructSize = sizeof(struct sockaddr_in); 
    struct sockaddr_in *client;
    char clientIpAddress[16];
    int ret, new_client_sock;
    int sockets_maxfd = server_info->sock;
    struct timeval tv;

    fd_set fdsocks_read, fdsocks_write;

    mylist_item *client_t;

    memset(clientIpAddress, '\0', 16); 


    tv.tv_sec = 0;
    tv.tv_usec = 0;

    FD_ZERO(&fdsocks_read);
    FD_ZERO(&fdsocks_write);
    FD_SET(server_info->sock, &fdsocks_read); // For reading new clients accepts from server socket

    /* SetUp client's sockets for check on read and write by select: */
    client_t = params->clients_list_start;
    while (client_t != NULL) {
        if (client_t->client_info == NULL || client_t->client_info->close_it == 1) {
            client_t = client_t->next;
            continue;
        }

        if (client_t->client_info != NULL) {
            FD_SET(client_t->client_info->sock, &fdsocks_read);
            FD_SET(client_t->client_info->sock, &fdsocks_write);

            if (sockets_maxfd < client_t->client_info->sock) 
                sockets_maxfd = client_t->client_info->sock;
        }

        /* Load next item */
        client_t = client_t->next;
    }

    ret = select(sockets_maxfd+1, &fdsocks_read, &fdsocks_write, (fd_set *)0, &tv);
    if (ret == -1) {
        syslog(LOG_ERR, "Error on select: %s", strerror(errno));
        syslog(LOG_ERR, "MAXFD: %d", sockets_maxfd);
        close_clients(params);
        return -1;
    }
    
    // Nothing to read/write:
    if (ret == 0) {
        return 0;
    }
            

    /* New client: */
    if (FD_ISSET(server_info->sock, &fdsocks_read)) {
        client = (struct sockaddr_in*) calloc(1, sizeof(struct sockaddr_in));
        new_client_sock = accept(server_info->sock, (struct sockaddr *)client, &clientStructSize);
        if (new_client_sock == -1) {
            syslog(LOG_ERR, "Error on accept: %d: %s", errno, strerror(errno));
            free(client);
            //free(server_info->hints);
            //close(server_info->sock);
            //exit(EXIT_FAILURE);
            return 0;
        }
        if (new_client_sock > 1024) {
            syslog(LOG_ERR, "Fucking BSD accept - dont reuse identificators!");
            close(new_client_sock);
            close_clients(params);
            return -1;
        }
        set_nonblock(new_client_sock);

        inet_ntop(AF_INET, &(client->sin_addr), clientIpAddress, sizeof(clientIpAddress)); 
        //syslog(LOG_INFO, "New client: [%s:%d]", clientIpAddress,  ntohs(client->sin_port) );

        /* Prepare client infos in handy structure */
        client_info *ci = (client_info *)malloc(sizeof(client_info));
        syslog(LOG_DEBUG, "Accepting4 new client... %d", (int) new_client_sock);
        ci->sock = new_client_sock;
        ci->close_it = 0;
        ci->ping_timeout = 0;
        ci->crdate = time (NULL);
        ci->lastupdate = ci->crdate;
        ci->address = client;
        ci->header_readed = 0; // Header currently not readed
        ci->ws_opened = 0; // WebSockets stream is not opened
        ipv4_parse(ci->ip, clientIpAddress);

        syslog(LOG_DEBUG, "Accepting5 new client... %d", (int) new_client_sock);
        ci->buffer_read = (io_buffer *)malloc(sizeof(io_buffer));
        ci->buffer_write = (io_buffer *)malloc(sizeof(io_buffer));
        syslog(LOG_DEBUG, "Accepting6 new client... %d", (int) new_client_sock);
        ci->user = NULL;
        io_buff_free(ci->buffer_read, 1);
        io_buff_free(ci->buffer_write, 1);
        syslog(LOG_DEBUG, "Accepting7 new client... %d", (int) new_client_sock);

        mylist_insert(params->clients_list_start, ci);
        syslog(LOG_INFO, "Accepted new client: %d", new_client_sock);
        return 0;
    }

    long int ntime = time (NULL);

    /* Read/Write data from clients: */
    client_t = params->clients_list_start;
    while (client_t != NULL) {
        if (client_t->client_info == NULL) {
            client_t = client_t->next;
            continue;
        }

        if (client_t->client_info->close_it == 1) {
            client_t = client_t->next;
            continue;
        }

        if (client_t->client_info->ws_opened == 0 && client_t->client_info->crdate + WS_TIMEOUT < ntime) {
            client_t->client_info->close_it = 1;
        }

        if (client_t->client_info->ws_opened == 1 && client_t->client_info->ping_timeout + WS_PING_TIMEOUT < ntime) {
            syslog(LOG_INFO, "PING client: %d", client_t->client_info->sock);
            client_t->client_info->ping_timeout = ntime;
            process_client_ws_send_frame(client_t, "PING", WS_TEXT_FRAME);
        }


        /* Something to read: */
        if (client_t->client_info != NULL && FD_ISSET(client_t->client_info->sock, &fdsocks_read)) {
            if (0 > process_client_read(params, client_t)) {
                syslog(LOG_INFO, "PROCESS[%d] EOF", client_t->client_info->sock);
                client_t->client_info->close_it = 1;
            }
        }

        /* Process readed data: */
        if (process_client(params, client_t) < 0) {
            syslog(LOG_INFO, "PROCESS READ[%d] Failed!", client_t->client_info->sock);
            client_t->client_info->close_it = 1;
        }

        /* Something to write: */
        if (client_t->client_info != NULL && FD_ISSET(client_t->client_info->sock, &fdsocks_write)) {
            if (process_client_write(params, client_t) < 0) {
                syslog(LOG_INFO, "PROCESS WRITE[%d] Failed!", client_t->client_info->sock);
                client_t->client_info->close_it = 1;
            } else {
                //client_t->client_info->ping_timeout = ntime;
            }
        }

        /* Close client if need: */
        if (client_t->client_info->close_it == 1) {
            close_client(params, client_t);
        }


        /* Load next item */
        client_t = client_t->next;
    }

    return 0;
}

