#include <stdlib.h>
// #include <malloc.h>
#include <string.h>
#include <syslog.h>




#include "lists.h"


/*
 * Initializes the first element of the mylist.
 */

int mylist_init(mylist_item *mylist_start) {
    mylist_start->client_info = NULL;
    mylist_start->next = NULL;
    mylist_start->prev = NULL;
    return 0;
}


int mylist_remove_item(mylist_item *item) {
    if (item == NULL) 
        return -1;
    if (item->client_info != NULL) 
        free(item->client_info);
    item->client_info = NULL;

    //if (item->prev != NULL) {
    //    item->prev->next = item->next;
    //    free(item);
    //}
    return 0;
}

	
/*
 * Inserts a new client_info element at the end of the mylist.
 */
int mylist_insert(mylist_item *mylist_start, client_info *element) {
    int exist = 0;
    mylist_item *cur, *prev;

    cur = prev = mylist_start;

    /* Try to find existent element: */
    while (cur != NULL) {
        if (cur->client_info == NULL) {
            cur->client_info = element;
            exist = 1;
            break;
        }
	
        /* Load next item */
        prev = cur;
        cur = cur->next;
    }

    /* Item not found: */
    if (exist == 0) {
        /* Create item: */
        mylist_item *new_item = (mylist_item *)malloc(sizeof(mylist_item));
        new_item->client_info = element;
        new_item->next = NULL;
        new_item->prev = prev;

        /* Append item */
        prev->next = new_item;
        exist = 1;
    }

    if (exist == 1) {
        return 0;
    } else { 
        return -1;
    }
}


/*
 * Removes a client_info element by sock.
 */
int mylist_remove_by_sockfd(mylist_item *mylist_start, int sockfd) {
    mylist_item *cur;
    cur = mylist_start;

    while (cur != NULL) {
        /* Delete client_info data if sockfd matches */
        if (cur->client_info->sock == sockfd) {
            mylist_remove_item(cur);
            break;
        }
	
        /* Load next item */
        cur = cur->next;
    }

    return 0;
}


/*
 * Find a client_info element by sockfd.
 */
mylist_item* mylist_find_by_sockfd(mylist_item *mylist_start, int sockfd) {
    mylist_item *cur;

    cur = mylist_start;
    while (cur != NULL) {
        if (cur->client_info != NULL && cur->client_info->sock == sockfd) 
            return cur;
	
        /* Load next item */
        cur = cur->next;
    }
    return NULL;
}



/*
 * IO buffer: Free
 */
int io_buff_free(io_buffer *buff, int is_init) {
    //syslog(LOG_INFO, "Free client");
    if (is_init == 0 && buff->value != NULL) {
        free(buff->value);
    }
    buff->value = NULL;
    buff->size = 0;
    buff->len = 0;
    return 0;
}




/*
 * Push data to IO buffer
 */

int io_buff_push(io_buffer *buff, char *data, int dlen) {
    int min_buff_size = 1024;

    // First alloc:
    if ((buff->size == 0) || (buff->value == NULL)) {
        buff->size = (dlen+1) * sizeof(char);
        if (buff->size < min_buff_size) {
            buff->size = min_buff_size;
        }
        //syslog(LOG_INFO, "First alloc started, %d", buff->size);
        buff->value = (char*) malloc(buff->size);

    // Realloc:
    } else if (buff->size < (buff->len + dlen + 1)) {
        do {
            buff->size = buff->size*2;
        } while (buff->size <= (buff->len + dlen));
        //syslog(LOG_INFO, "Realloc started, %d > %d", buff->size, dlen);
        buff->value = (char*) realloc(buff->value, buff->size);
    }

    //if (buff->len == 0) {
    //    strncpy(buff->value, data, dlen);
    //    buff->value[dlen] = '\0';
    //} else {
        //strncat(buff->value, data, dlen);
    //}

    //syslog(LOG_INFO, "StrNcpy0: %d + %d, %s", buff->len, dlen, buff->value);
    int i;
    for (i=0; i<dlen; i++) {
        buff->value[(buff->len)+i] = data[i];
    }
    buff->len += dlen;
    buff->value[buff->len] = '\0';
    //syslog(LOG_INFO, "StrNcpy1: %d - %d, %s", buff->len, dlen, buff->value);
    //syslog(LOG_INFO, "StrNcpy: %d", buff->len);
    return 0;
}



/*
 * Get data from IO buffer, returned data would be removed from buffer
 */

int io_buff_get(io_buffer *buff, char *data, int dlen) {
    if (dlen > buff->len) {
        return -1;
    }

    if (data != NULL) {
        strncpy(data, buff->value, dlen);
    }

    memmove(buff->value, buff->value+dlen, sizeof(char)*(buff->len-dlen) );
    memset(buff->value+(buff->len-dlen), 0, sizeof(char) * dlen);
    //buff->value[dlen] = '\0';
    buff->len = buff->len-dlen;

    return 0;
}

