

void ipv4_dumps(char *ip, char *bytes);
void ipv4_parsen(char *bytes, char *ip, size_t len);
void ipv4_parse(char *bytes, char *ip);
    
int userslist_mng(struct server_params *params, mylist_item *client_t, int add_it, int is_active, char *href);
int userslist_mng_chatanswer(struct server_params *params, mylist_item *client_t, int add_it, int is_active, char *href);



