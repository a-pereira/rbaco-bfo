/* Force-included on Windows builds: map SIGUSR1 (absent on Windows) to SIGBREAK. */
#ifndef LADR_WIN_SHIM_COMPAT_H
#define LADR_WIN_SHIM_COMPAT_H
#include <signal.h>
#ifndef SIGUSR1
#define SIGUSR1 SIGBREAK
#endif
#endif
