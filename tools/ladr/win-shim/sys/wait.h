/* Windows shim: fork/pipe/wait are used only by forking_search(), which prover9 never calls. Stubs fail loudly. */
#ifndef LADR_WIN_SHIM_WAIT_H
#define LADR_WIN_SHIM_WAIT_H
#define WIFEXITED(s) 1
#define WEXITSTATUS(s) (s)
static inline int wait(int *s) { if (s) *s = 0; return -1; }
static inline int fork(void) { return -1; }
static inline int pipe(int fd[2]) { (void)fd; return -1; }
#endif
