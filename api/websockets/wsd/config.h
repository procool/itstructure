#include <semaphore.h>

#include "parson.h"
#include "lists.h"


#define _confFilePathLength 1024
#define _WDPathLength 1024

#define _portDigits 6
#define _addressLength 16
#define _dirLength 32


struct global_params {
    char confFile[_confFilePathLength]; /* config file path */
    int verbosity; /* verbose level */
    char workDir[_WDPathLength];
};

struct server_params {
    int listenPort;
    char *listenIpAddress;

    char *passport_host;
    int passport_port;

    mylist_item *clients_list_start;
    sem_t sem;

    void 
        (*ws_func_all_clients_send_message)(),
        (*ws_func_client_send_message)();
        
    int (*userslist_mng)();
    int (*userslist_mng_chatanswer)();

    char *users_list;
    JSON_Value *users_json;


};

struct thread_arg_struct {
    struct server_params *server_params;
};

