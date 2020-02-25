#define DEFAULT_HOST "localhost"
#define DEFAULT_PORT 3443

#define MAX_HEADER_LENGTH 10000
#define MAX_BUFF_WRITE 102400
#define MAX_OUTBUFF_SIZE 1048576

#define TPL_INDEX "<html><body>It's Websockets! Use /ws/ handler!</body></html>"
#define TPL_ERR404 "Undefined handler"
#define TPL_ERR500 "Error on opening webSocket connection"

#include <sys/time.h>

/* Server's clients list: */
struct mylist_item clients_list_start;



typedef struct tserver_info {
    int sock;

    /* Client address structure: */
    struct addrinfo *hints;
} tserver_info;





int process_clients();
void ws_all_clients_send_message(struct mylist_item *client_t, char *message);
void ws_client_send_message(struct mylist_item *client_t, char *message);



