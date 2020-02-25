#include <sys/time.h>
#include <netinet/in.h>


typedef struct user_info {
    char *session;    // User Session id
    char *name;       // User login
    long int uid;     // User id
} user_info;


typedef struct io_buffer {
    char *value;   // Buffer data
    int len;       // Real length of data
    int size;      // Allocated size
} io_buffer;

typedef struct client_info {
    int sock;
    int close_it;
    int header_readed;
    int ws_opened;
    char *header_data;
    char ip[5];
    char ip6[17];
    //char nickname[20];
    long int crdate;
    long int lastupdate;
    long int ping_timeout;
    struct sockaddr_in *address;
    struct io_buffer *buffer_read;
    struct io_buffer *buffer_write;
    struct user_info *user;
} client_info;


typedef struct mylist_item {
    struct client_info *client_info;
    struct mylist_item *prev;
    struct mylist_item *next;
} mylist_item;

int mylist_init(mylist_item *mylist_start);
int mylist_remove_item(mylist_item *item);
int mylist_insert(mylist_item *mylist_start, client_info *element);
int mylist_remove_by_sockfd(mylist_item *mylist_start, int sockfd);
mylist_item* mylist_find_by_sockfd(mylist_item *mylist_start, int sockfd);

int io_buff_free(io_buffer *buff, int is_init);
int io_buff_push(io_buffer *buff, char *data, int dlen);
int io_buff_get(io_buffer *buff, char *data, int dlen);

