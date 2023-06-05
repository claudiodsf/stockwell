/*
 * sinemodule.c
 *
 * Original version downloaded from
 * http://kurage.nimh.nih.gov/meglab/Meg/Stockwell
 *
 * The contents of this file is free and unencumbered software released
 * into the public domain. For more information, please refer to
 * https://unlicense.org
 *
 */

/* Riedel & Sidorenko sine tapers. */

// the following two defines are for Windows
#define _CRT_SECURE_NO_WARNINGS
#define _USE_MATH_DEFINES
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

// the following is for Windows
void PyInit_sine() {}

/* Compute the kth sine taper. d is an array of length N. */

#ifdef __cplusplus
extern "C"
#endif
#ifdef _MSC_VER
__declspec(dllexport)
#endif
void sine_taper(int k, int N, double *d)
{
    int i;
    double s;

    s = sqrt(2. / (N + 1));
    for (i = 0; i < N; i++) {
        d[i] = s * sin(M_PI * (k + 1) * (i + 1) / (N + 1));
    }
}