#include <syslog.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <sys/types.h>
#include <arpa/inet.h>
#include <netdb.h>

#include "redis_thread.h"

#include "parson.h"
#include "lists.h"

#include "bb.h"





/*
 * Make request:
 */

int bb_make_request(char *host, int port, char *message, char *answer, size_t answer_size) {
    int sock;

    char ip[INET_ADDRSTRLEN];

    struct sockaddr_in addr;
    struct hostent* raw_host;
    raw_host = gethostbyname(host);
    if (raw_host == NULL) {
        syslog(LOG_ERR, "BB: Error resolve host: %s", host);
        return -1;
    }
    sock = socket(AF_INET, SOCK_STREAM, 0);
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    addr.sin_addr.s_addr=*(unsigned long*)(raw_host->h_addr);

    inet_ntop(AF_INET, &(addr.sin_addr), ip, sizeof(ip));

    syslog(LOG_DEBUG, "BB: Making request[%s:%d] %s: %s", host, port, ip, message);

    if (connect(sock,(struct sockaddr*)&addr, sizeof(addr)) < 0) {
        syslog(LOG_ERR, "BB: Error connect to host %s:%d", host, port);
        return -1;
    }

    int r = send(sock, message, sizeof(char)*strlen(message), 0);
    r = recv(sock, answer, answer_size, 0);
    close(sock);
    if (r < 0) {
        syslog(LOG_ERR, "BB: Error connect to host %s:%d", host, port);
        return -1;
    }
    return 0;
}




char* command_make_json_string(const char *cmd, JSON_Object *root_object, JSON_Value *root_value) {
    json_object_set_string(root_object, "cmd", cmd);
    size_t message_size = json_serialization_size(root_value)+1;

    char *message = (char*)malloc(sizeof(char)*message_size);
    memset(message, '\0', message_size);
    if (JSONSuccess == json_serialize_to_buffer(root_value, message, message_size)) {
        return message;
    }
    free(message);
    return NULL;
}



user_info* bb_check_session(char *host, int port, char *session) {

    size_t answer_size = 8000;
    char answer[answer_size];
    short errno = 0;

    JSON_Value *root_value = json_value_init_object();
    JSON_Object *root_object = json_value_get_object(root_value);
    json_object_set_string(root_object, "session", session);
    char *message = command_make_json_string("session", root_object, root_value);
    json_value_free(root_value);
    if (message != NULL) {

        size_t rq_size = 32 + strlen(message);
        char *request = (char *)malloc(sizeof(char)*(rq_size+1));
        memset(request, '\0', rq_size+1);
        strcpy(request, "BBPROTO/1.0\r\nhello:false\r\n\r\n");
        strcpy(request+28, message);
        strcpy(request+28+strlen(message), "\r\n\r\n");

        if (bb_make_request(host, port, request, answer, answer_size) < 0) {
            syslog(LOG_ERR, "BB: Error session check!");
            errno = 1;
        } 
        free(message);
        free(request);
    }

    // TODO: Process server answer
    syslog(LOG_ERR, "BB: ANSWER: %s", answer);

    JSON_Value *j_root = json_parse_string((const char*) answer);
    if (j_root == NULL) 
        return NULL;

    JSON_Object *j_data = json_value_get_object(j_root);
    int uid = (int) json_object_get_number(j_data, "id");

    if (uid != 0) {
        user_info *user = (user_info *)malloc(sizeof(user_info));
        user->uid = uid;
        user->name = (char*) json_object_get_string(j_data, "name");
        syslog(LOG_DEBUG, "BB: USER UID=%d LOGIN=%s Authorizated!", uid, user->name);
        json_value_free(j_root);
        return user;
    }
    json_value_free(j_root);
    return NULL;
}

