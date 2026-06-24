/*
 * st.c
 *
 * Original version downloaded from
 * http://kurage.nimh.nih.gov/meglab/Meg/Stockwell
 *
 * The contents of this file is free and unencumbered software released
 * into the public domain. For more information, please refer to
 * https://unlicense.org
 *
 * Modified for Windows compatibility
 */

// the following two defines are for Windows
#define _CRT_SECURE_NO_WARNINGS
#define _USE_MATH_DEFINES
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <fftw3.h>
#include "st_types.h"

// the following is for Windows
void PyInit_st() {}

char *Wisfile = NULL;
#if defined(WIN32) || defined(_WIN32) || defined(__WIN32__) || defined(__NT__)
	const char *Wistemplate = "%s\.fftwis";
#else
	const char *Wistemplate = "%s/.fftwis";
#endif
#define WISLEN 8
/* Static FFTW plans — kept between calls for performance, but
   must be destroyed before process exit to avoid segfault. */

/* st() plans */
static int st_planlen = 0;
static double *st_g = NULL;
static fftw_plan st_p1 = NULL, st_p2 = NULL;
static fftw_complex *st_h = NULL, *st_H = NULL, *st_G = NULL;

/* ist() plans */
static int ist_planlen = 0;
static fftw_plan ist_p2 = NULL;
static fftw_complex *ist_h = NULL, *ist_H = NULL;

/* hilbert() plans */
static int hilbert_planlen = 0;
static fftw_plan hilbert_p1 = NULL, hilbert_p2 = NULL;
static fftw_complex *hilbert_h = NULL, *hilbert_H = NULL;

#ifdef _MSC_VER
__declspec(dllexport)
#endif
void st_cleanup(void)
{
	if (st_planlen > 0) {
		fftw_destroy_plan(st_p1);
		fftw_destroy_plan(st_p2);
		fftw_free(st_h);
		fftw_free(st_H);
		fftw_free(st_G);
		free(st_g);
		st_planlen = 0;
	}
	if (ist_planlen > 0) {
		fftw_destroy_plan(ist_p2);
		fftw_free(ist_h);
		fftw_free(ist_H);
		ist_planlen = 0;
	}
	if (hilbert_planlen > 0) {
		fftw_destroy_plan(hilbert_p1);
		fftw_destroy_plan(hilbert_p2);
		fftw_free(hilbert_h);
		fftw_free(hilbert_H);
		hilbert_planlen = 0;
	}
	fftw_cleanup();
}
void set_wisfile(void)
{
	const char *home;

	if (Wisfile) return;
	#if defined(WIN32) || defined(_WIN32) || defined(__WIN32__) || defined(__NT__)
        const char *homeDrive = getenv("HOMEDRIVE");
        const char *homePath = getenv("HOMEPATH");
        home = malloc(strlen(homeDrive)+strlen(homePath)+1);
        strcat(home, homeDrive);
        strcat(home, homePath);
	#else
        home = getenv("HOME");
	#endif
	Wisfile = (char *)malloc(strlen(home) + WISLEN + 1);
	sprintf(Wisfile, Wistemplate, home);
}

/* Convert frequencies in Hz into rows of the ST, given sampling rate and
length. */

int st_freq(double f, int len, double srate)
{
	return (int)floor(f * len / srate + .5);
}

static double gauss(int n, int m, double gamma);
static double kazemi(int n, int m, double gamma);

/* Stockwell transform of the real array data. The len argument is the
number of time points, and it need not be a power of two. The lo and hi
arguments specify the range of frequencies to return, in samples. If they are
both zero, they default to lo = 0 and hi = len / 2. The result is
returned in the complex array result, which must be preallocated, with
n rows and len columns, where n is hi - lo + 1. For the default values of
lo and hi, n is len / 2 + 1. */

#ifdef __cplusplus
extern "C"
#endif
#ifdef _MSC_VER
__declspec(dllexport)
#endif
void st(int len, int lo, int hi, double gamma, enum WINDOW window_code, double *data, double *result)
{
	int i, k, n, l2;
	double s, *p;
	static double (*window_function)(int, int, double);
	window_function = &gauss;
	if (window_code == KAZEMI)
	{
		window_function = &kazemi;
	}

	/* Check for frequency defaults. */

	if (lo == 0 && hi == 0) {
		hi = len / 2;
	}

	/* Keep the arrays and plans around from last time, since this
	is a very common case. Reallocate them if they change. */

	if (len != st_planlen && st_planlen > 0) {
		fftw_destroy_plan(st_p1);
		fftw_destroy_plan(st_p2);
		fftw_free(st_h);
		fftw_free(st_H);
		fftw_free(st_G);
		free(st_g);
		st_planlen = 0;
	}

	if (st_planlen == 0) {
		st_planlen = len;
		st_h = fftw_malloc(sizeof(fftw_complex) * len);
		st_H = fftw_malloc(sizeof(fftw_complex) * len);
		st_G = fftw_malloc(sizeof(fftw_complex) * len);
		st_g = (double *)malloc(sizeof(double) * len);
		/* Zero-initialize for safety. */
		memset(st_h, 0, sizeof(fftw_complex) * len);
		memset(st_H, 0, sizeof(fftw_complex) * len);
		memset(st_G, 0, sizeof(fftw_complex) * len);
		memset(st_g, 0, sizeof(double) * len);


		/* Set up the fftw plans. */

		st_p1 = fftw_plan_dft_1d(len, st_h, st_H, FFTW_FORWARD, FFTW_ESTIMATE);
		st_p2 = fftw_plan_dft_1d(len, st_G, st_h, FFTW_BACKWARD, FFTW_ESTIMATE);
	}

	/* Convert the input to complex. Also compute the mean. */

	s = 0.;
	memset(st_h, 0, sizeof(fftw_complex) * len);
	for (i = 0; i < len; i++) {
		st_h[i][0] = data[i];
		s += data[i];
	}
	s /= len;

	/* FFT. */

	fftw_execute(st_p1); /* h -> H */

	/* Hilbert transform. The upper half-circle gets multiplied by
	two, and the lower half-circle gets set to zero.  The real axis
	is left alone. */

	l2 = (len + 1) / 2;
	for (i = 1; i < l2; i++) {
		st_H[i][0] *= 2.;
		st_H[i][1] *= 2.;
	}
	l2 = len / 2 + 1;
	for (i = l2; i < len; i++) {
		st_H[i][0] = 0.;
		st_H[i][1] = 0.;
	}

	/* Fill in rows of the result. */

	p = result;

	/* The row for lo == 0 contains the mean. */

	n = lo;
	if (n == 0) {
		for (i = 0; i < len; i++) {
			*p++ = s;
			*p++ = 0.;
		}
		n++;
	}

	/* Subsequent rows contain the inverse FFT of the spectrum
	multiplied with the FFT of scaled gaussians. */

	while (n <= hi) {

		/* Scale the FFT of the gaussian. Negative frequencies
		wrap around. */

		st_g[0] = (*window_function)(n, 0, gamma);
		l2 = len / 2 + 1;
		for (i = 1; i < l2; i++) {
			st_g[i] = st_g[len - i] = (*window_function)(n, i, gamma);
		}

		k = len - n;
		for (i = 0; i < len; i++) {
			if (k >= len) k -= len;
			s = st_g[k++];
			st_G[i][0] = st_H[i][0] * s;
			st_G[i][1] = st_H[i][1] * s;
		}

		/* Inverse FFT the result to get the next row. */

		fftw_execute(st_p2); /* G -> h */
		for (i = 0; i < len; i++) {
			*p++ = st_h[i][0] / len;
			*p++ = st_h[i][1] / len;
		}

		/* Go to the next row. */

		n++;
	}
}

/* This is the Fourier Transform of a Gaussian. */

static double gauss(int n, int m, double gamma)
{
	return exp(-2. * M_PI * M_PI * m * m * gamma * gamma / (n * n));
}

/* This is the Fourier Transform of a Kazemi window. */
static double kazemi(int n, int m, double gamma)
{
	return 1/(1+((m * m * gamma  / n) * (m * m * gamma  / n)));
}


/* Inverse Stockwell transform. */

#ifdef __cplusplus
extern "C"
#endif
#ifdef _MSC_VER
__declspec(dllexport)
#endif
void ist(int len, int lo, int hi, double *data, double *result)
{
	int i, n, l2;
	double *p;
	double fr, fi, dr, di, ef;

	/* Check for frequency defaults. */

	if (lo == 0 && hi == 0) {
		hi = len / 2;
	}

	/* Keep the arrays and plans around from last time, since this
	is a very common case. Reallocate them if they change. */

	if (len != ist_planlen && ist_planlen > 0) {
		fftw_destroy_plan(ist_p2);
		fftw_free(ist_h);
		fftw_free(ist_H);
		ist_planlen = 0;
	}

	if (ist_planlen == 0) {
		ist_planlen = len;
		ist_h = fftw_malloc(sizeof(fftw_complex) * len);
		ist_H = fftw_malloc(sizeof(fftw_complex) * len);
		memset(ist_h, 0, sizeof(fftw_complex) * len);
		memset(ist_H, 0, sizeof(fftw_complex) * len);


		/* Set up the fftw plans. */

		ist_p2 = fftw_plan_dft_1d(len, ist_H, ist_h, FFTW_BACKWARD, FFTW_ESTIMATE);
	}

	/* Sum the complex array across time, multiplying by
	   complex exponential factor to perform the frequency
	   shift required for the inverse. */

	memset(ist_H, 0, sizeof(fftw_complex) * len);
	p = data;
	for (n = lo; n <= hi; n++) {
		for (i = 0; i < len; i++) {
			double dr, di, ef, fr, fi;
			dr = *p++;
			di = *p++;
			ef = -2 * M_PI * n * i / len;
			fr = cos(ef);
			fi = sin(ef);
			ist_H[n][0] += dr * fr - di * fi;
			ist_H[n][1] += dr * fi + di * fr;
		}
	}

	/* Invert the Hilbert transform. */

	l2 = (len + 1) / 2;
	for (i = 1; i < l2; i++) {
		ist_H[i][0] /= 2.;
		ist_H[i][1] /= 2.;
	}
	l2 = len / 2 + 1;
	for (i = l2; i < len; i++) {
		ist_H[i][0] = ist_H[len - i][0];
		ist_H[i][1] = -ist_H[len - i][1];
	}

	/* Inverse FFT. */

	fftw_execute(ist_p2); /* H -> h */
	p = result;
	for (i = 0; i < len; i++) {
		*p++ = ist_h[i][0] / len;
	}
}

/* This does just the Hilbert transform. */

#ifdef __cplusplus
extern "C"
#endif
#ifdef _MSC_VER
__declspec(dllexport)
#endif
void hilbert(int len, double *data, double *result)
{
	int i, l2;
	double *p;

	/* Keep the arrays and plans around from last time, since this
	is a very common case. Reallocate them if they change. */

	if (len != hilbert_planlen && hilbert_planlen > 0) {
		fftw_destroy_plan(hilbert_p1);
		fftw_destroy_plan(hilbert_p2);
		fftw_free(hilbert_h);
		fftw_free(hilbert_H);
		hilbert_planlen = 0;
	}

	if (hilbert_planlen == 0) {
		hilbert_planlen = len;
		hilbert_h = fftw_malloc(sizeof(fftw_complex) * len);
		hilbert_H = fftw_malloc(sizeof(fftw_complex) * len);
		memset(hilbert_h, 0, sizeof(fftw_complex) * len);
		memset(hilbert_H, 0, sizeof(fftw_complex) * len);


		/* Set up the fftw plans. */

		hilbert_p1 = fftw_plan_dft_1d(len, hilbert_h, hilbert_H, FFTW_FORWARD, FFTW_ESTIMATE);
		hilbert_p2 = fftw_plan_dft_1d(len, hilbert_H, hilbert_h, FFTW_BACKWARD, FFTW_ESTIMATE);
	}

	/* Convert the input to complex. */

	memset(hilbert_h, 0, sizeof(fftw_complex) * len);
	for (i = 0; i < len; i++) {
		hilbert_h[i][0] = data[i];
	}

	/* FFT. */

	fftw_execute(hilbert_p1); /* h -> H */

	/* Hilbert transform. The upper half-circle gets multiplied by
	two, and the lower half-circle gets set to zero.  The real axis
	is left alone. */

	l2 = (len + 1) / 2;
	for (i = 1; i < l2; i++) {
		hilbert_H[i][0] *= 2.;
		hilbert_H[i][1] *= 2.;
	}
	l2 = len / 2 + 1;
	for (i = l2; i < len; i++) {
		hilbert_H[i][0] = 0.;
		hilbert_H[i][1] = 0.;
	}

	/* Inverse FFT. */

	fftw_execute(hilbert_p2); /* H -> h */

	/* Fill in the rows of the result. */

	p = result;
	for (i = 0; i < len; i++) {
		*p++ = hilbert_h[i][0] / len;
		*p++ = hilbert_h[i][1] / len;
	}
}
