/* Windows (mingw-w64) shim for LADR/Prover9: <sys/resource.h> is POSIX-only.
 * Reports clock() as user time and zero system time. Affects only printed timing. */
#ifndef LADR_WIN_SHIM_RESOURCE_H
#define LADR_WIN_SHIM_RESOURCE_H
#include <time.h>
#include <sys/time.h>
#define RUSAGE_SELF 0
struct rusage { struct timeval ru_utime; struct timeval ru_stime; long ru_maxrss; };
static inline int getrusage(int who, struct rusage *r)
{
  long long us = (long long)((double)clock() * 1000000.0 / CLOCKS_PER_SEC);
  (void)who;
  r->ru_utime.tv_sec = (long)(us / 1000000); r->ru_utime.tv_usec = (long)(us % 1000000);
  r->ru_stime.tv_sec = 0; r->ru_stime.tv_usec = 0; r->ru_maxrss = 0;
  return 0;
}
#endif
