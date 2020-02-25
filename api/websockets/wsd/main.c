#include <stdio.h> 
#include <string.h>
#include <stdlib.h> 
#include <dlfcn.h> 
#include <getopt.h>
#include <pthread.h>
#include <semaphore.h>

/* Daemonization libs */
#include <fcntl.h> 
#include <errno.h> 
#include <unistd.h> 
#include <syslog.h> 
#include <sys/types.h> 
#include <sys/stat.h> 
#include <signal.h>

/* TCP Server libs */
#include <netdb.h> 
#include <netinet/in.h> 
#include <sys/socket.h> 

/* Local includes */
#include "config.h"
#include "main.h"
#include "server.h"
#include "core.h"
#include "redis_thread.h"

 
void printUsage(FILE *stream, int exitStatus) {
    fprintf(stderr, "HELPER!\n");
    exit(exitStatus); 
}


//extern int start_server(struct server_params *params);
extern void * start_server(void *params);
extern int * stop_server();
extern void * core_loop_start(void *params);
extern void * redis_evloop_start(void *params);
//extern int redis_connect_thread_start(struct server_params *params);
extern int userslist_mng(struct server_params *params, mylist_item *client_t, int add_it, int is_active, char *href);
extern int userslist_mng_chatanswer(struct server_params *params, mylist_item *client_t, int add_it, int is_active, char *href);





void signal_handler(int sig) {
    switch(sig) {
        case SIGHUP:
            syslog(LOG_INFO, "SIGNAL: %d: Reloading...", sig);
            break;
        case SIGTERM:
            syslog(LOG_INFO, "SIGNAL: %d: Quit...", sig);
            stop_server();
            exit(EXIT_SUCCESS); 
            break;
        case SIGUSR1:
            syslog(LOG_INFO, "SIGNAL: %d: do nothing...", sig);
            break;
        case SIGUSR2:
            syslog(LOG_INFO, "SIGNAL: %d: do nothing...", sig);
            break;
        default:
            break;
    }
}


int main(int argc, char** argv) { 

    struct global_params gp;

    /* Defaults: */
    strncpy(gp.confFile, "main.conf\0", 10); // FIXME
    gp.verbosity = 0;

    /* Command line arguments variables: */
    char* const short_options = "hc:v:p:H:P:i:";
    int next_option, len;
    struct option long_options[] = {
        { "help",         0,  NULL,   'h'},
        { "config",       1,  NULL,   'c'},
        { "verbosity",    1,  NULL,   'v'},
        { "host",         1,  NULL,   'H'},
        { "port",         1,  NULL,   'p'},
        { "passport",     1,  NULL,   'P'},
        { "interactive",  0,  NULL,   'i'},
        { NULL,           0,  NULL,   0 }
    };

    /* Daemonization variables: */
    pid_t pid;
    char *daemon_name = "mywsd";
    int is_interactive = 0;


    /* SERVER Variables: */
    struct server_params *srv_prms = (struct server_params *) calloc(1, sizeof(struct server_params));
    srv_prms->listenIpAddress = (char*) calloc(1, _addressLength);

    do {
        next_option = getopt_long(argc, (char**)argv, short_options, long_options, NULL);
        switch(next_option) {
            case 'h':
                printUsage(stdout, EXIT_SUCCESS);
                break;
            case 'i':
                is_interactive = 1;
                break;
            case 'c':
                len = strlen((char*)optarg);
                if (_confFilePathLength > len) {
                    memset(&gp.confFile, '\0', len + 1);
    	            strncpy(gp.confFile, optarg, len);
    	        }
                break;
            case 'p':
                len = strlen((char*)optarg);
                if (_portDigits > len) {
                    srv_prms->listenPort = atoi(optarg);
                }
                break;
            case 'H':
                len = strlen((char*)optarg);
                if (_addressLength > len) {
                    strncpy(srv_prms->listenIpAddress, optarg, len);
                }
                break;

            // Passport
            case 'P':
                len = strlen((char*)optarg);
                char *pe = strstr(optarg, ":");
                int host_len = pe-optarg;
                if (host_len > 0) {
                    srv_prms->passport_host = (char*) calloc(1, host_len);
                    strncpy(srv_prms->passport_host, optarg, host_len);
                    srv_prms->passport_port = atoi(optarg+host_len+1);
                }
                break;

            case 'v':
                if ((0 <= atoi(optarg)) && (9 >= atoi(optarg))) {
                    gp.verbosity = atoi(optarg);
                }
                break;
            case '?':
                printUsage(stdout, EXIT_SUCCESS);
            case -1 :
                break;
            default :
                exit(EXIT_SUCCESS);
        }
    } while (next_option != -1);


    if (srv_prms->passport_host == NULL) {
        fprintf(stderr, "You should specifie --passport HOST:PORT\n");
        exit(EXIT_FAILURE); 
    }

    fprintf(stderr, "Using passport backend: %s:%d\n", srv_prms->passport_host, srv_prms->passport_port);

    /**************************/
    /* Daemonization process: */

    if (is_interactive == 0) {
        pid = fork();
        if (pid < 0) { 
            fprintf(stderr, "Parent: Can't fork! %s\n", strerror(errno));
            exit(EXIT_FAILURE); 
        } 
    
        if (pid > 0) { 
            /* Is a parent process, should exit */
            fprintf(stdout, "Daemon started with pid: %d\n", pid);
            exit(EXIT_SUCCESS); 
        } 

        /* Close standart descriptors: */
        close(STDOUT_FILENO);
        close(STDERR_FILENO);
    }


    /* Close standart descriptors: */
    close(STDIN_FILENO); 

    /* Change working directory: */
    char dir[] = ".";
    if ((chdir(dir)) < 0) {
        fprintf(stderr, "Can't chdir [%s]!: %s\n", dir, strerror(errno));
        exit(EXIT_FAILURE);
    }

    
    /* Connect to syslog: */ 
    openlog(daemon_name, LOG_PID, LOG_LOCAL0);
    syslog(LOG_DEBUG, "Standart pipes are closed!");

    /* Working with handlers: */
    signal(SIGCHLD, SIG_IGN);
    signal(SIGTSTP, SIG_IGN);
    signal(SIGTTOU, SIG_IGN);
    signal(SIGTTIN, SIG_IGN);
    signal(SIGPIPE, SIG_IGN);
    signal(SIGHUP, signal_handler);
    signal(SIGTERM, signal_handler);
    signal(SIGUSR1, signal_handler);
    signal(SIGUSR2, signal_handler);
 

    /* Initialize clients list */
    mylist_init(&clients_list_start);
    srv_prms->clients_list_start = &clients_list_start;

    srv_prms->ws_func_all_clients_send_message = (void (*)())ws_all_clients_send_message;
    srv_prms->ws_func_client_send_message = (void (*)())ws_client_send_message;
    srv_prms->userslist_mng = (int (*)())userslist_mng;
    srv_prms->userslist_mng_chatanswer = (int (*)())userslist_mng_chatanswer;
    srv_prms->users_json = json_parse_string("[]");


    

    sem_init(&srv_prms->sem, 0, 1);

    pthread_t thread1;
    pthread_t thread2;
    pthread_t thread3;

    struct thread_arg_struct thread_args;
    thread_args.server_params = srv_prms;

    pthread_create(&thread3, NULL, &start_server, (void *)&thread_args);
    pthread_create(&thread2, NULL, &redis_evloop_start, (void *)&thread_args);
    pthread_create(&thread1, NULL, &core_loop_start, (void *)&thread_args);
 
    pthread_join(thread1, NULL);
    pthread_join(thread2, NULL);
    pthread_join(thread3, NULL);

    pthread_detach(thread1);
    pthread_detach(thread2);
    pthread_detach(thread3);
    sem_destroy(&srv_prms->sem);

    syslog(LOG_DEBUG, "exit"); 
    closelog(); /* Disconnect from syslog */
    exit(EXIT_SUCCESS); 
}


