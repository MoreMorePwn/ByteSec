#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

char *gets(char *s);

void win(void) {
    const char *flag = getenv("BYTESEC_PWN_FLAG");
    if (flag == NULL) {
        flag = "BYTESEC{a18dc4f20b5e9a77}";
    }

    puts("\n[+] Control flow redirected.");
    puts(flag);
    _exit(0);
}

void vuln(void) {
    char name[32];

    puts("The win function exists, but main never calls it.");
    puts("Give the program a name to greet:");
    printf("> ");

    gets(name);

    printf("Hello, %s\n", name);
}

int main(void) {
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);

    puts("ByteSec ret2win starter");
    vuln();
    puts("Normal return path reached.");
    return 0;
}
