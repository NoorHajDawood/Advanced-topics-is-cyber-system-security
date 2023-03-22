#include <sys/param.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/wait.h>
#include <err.h>
#include <grp.h>
#include <fcntl.h>
#include <netdb.h>
#include <unistd.h>
#include <signal.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define CHILD_NUM 3
static char *PORT = "8080";

typedef struct config {
    char *cmd;
    char **args;
    char *url;
    int uid;
    int gid;
    char *jail;
    int sockfd;
    int pid;
} config;

char jail[] = "/home/noor/Documents/lab2";
char zookd_cmd[] = "zookd";
char zookfs_cmd[] = "zookfs";
char auth_svc_cmd[] = "zoobar/auth-server.py";
config zookd_conf = {zookd_cmd, NULL, NULL, 61011, 61012, jail, -1, -1};
config zooksvc_conf = {zookfs_cmd, NULL, NULL, 61013, 61012, jail, -1, -1};
config auth_svc_conf = {auth_svc_cmd, (char*[]){"/authsvc/sock", NULL}, NULL, 61014, 61012, jail, -1, -1};
config *confs[] = {&zookd_conf, &zooksvc_conf, &auth_svc_conf};

static pid_t launch_svc(int);
char *conf_details(char *, char *);
void keep_alive();

struct sigaction sa;

int main(int argc, char **argv)
{
    if (argc == 2)
        PORT = argv[1];

    int socketPair[2];
    if (socketpair(AF_UNIX, SOCK_STREAM, 0, socketPair))
        err(1, "socketpair");
    zookd_conf.sockfd = socketPair[0];
    zooksvc_conf.sockfd = socketPair[1];

    // memset(&sa, 0, sizeof(sa));
    // sa.sa_handler = keep_alive;
    // sigaction(SIGCHLD, &sa, NULL);

    // signal(SIGCHLD, keep_alive);
    for(int i = 0; i < CHILD_NUM; i++)
        launch_svc(i);
    
    pid_t pid;
    while((pid = wait(NULL)) > 0) {
        for(int i = 0; i < CHILD_NUM; i++) {
            if(confs[i]->pid == pid) {
                launch_svc(i);
                break;
            }
        }
    }
}

void keep_alive() {
    pid_t pid;
    int status;

    while((pid = waitpid(-1, &status, WNOHANG)) != -1) {
        for(int i = 0; i < CHILD_NUM; i++) {
            if(confs[i]->pid == pid) {
                launch_svc(i);
                return;
            }
        }
    }
}

pid_t launch_svc(int child)
{
    pid_t pid;
    char *argv[32] = {0};
    int i = 0, toFree = -1;
    config *conf = confs[child];

    switch (pid = fork())
    {
    case 0:
        break;
    case -1:
        err(1, "fork");
    default:
        conf->pid = pid;
        warnx("%s: pid %d", conf->cmd, pid);
        return pid;
    }

    chdir(conf->jail);
    chroot(conf->jail);
    setuid(conf->uid);
    setgid(conf->gid);

    argv[i++] = conf->cmd;
    for(int j = 0; conf->args && conf->args[j]; j++) {
        argv[i++] = conf->args[j];
    }
    if(conf->sockfd > -1) {
        toFree = i;
        asprintf(&argv[i++], "%d", conf->sockfd);
    }
    if(conf == &zookd_conf) {
        argv[i++] = PORT;
    }

    if(execv(argv[0], argv) == -1)
        err(1, "ERROR execv: %s pid: %d", argv[0], getpid());
    if(toFree != -1) {
        free(argv[toFree]);
    }
    return 0;
}
