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
	FILE *wisdom;
	static int planlen = 0;
	static double *g;
	static fftw_plan p1, p2;
	static fftw_complex *h, *H, *G;
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

	if (len != planlen && planlen > 0) {
		fftw_destroy_plan(p1);
		fftw_destroy_plan(p2);
		fftw_free(h);
		fftw_free(H);
		fftw_free(G);
		free(g);
		planlen = 0;
	}

	if (planlen == 0) {
		planlen = len;
		h = fftw_malloc(sizeof(fftw_complex) * len);
		H = fftw_malloc(sizeof(fftw_complex) * len);
		G = fftw_malloc(sizeof(fftw_complex) * len);
		g = (double *)malloc(sizeof(double) * len);

		/* Get any accumulated wisdom. */

		set_wisfile();
		wisdom = fopen(Wisfile, "r");
		if (wisdom) {
			fftw_import_wisdom_from_file(wisdom);
			fclose(wisdom);
		}

		/* Set up the fftw plans. */

		p1 = fftw_plan_dft_1d(len, h, H, FFTW_FORWARD, FFTW_MEASURE);
		p2 = fftw_plan_dft_1d(len, G, h, FFTW_BACKWARD, FFTW_MEASURE);

		/* Save the wisdom. */

		wisdom = fopen(Wisfile, "w");
		if (wisdom) {
			fftw_export_wisdom_to_file(wisdom);
			fclose(wisdom);
		}
	}

	/* Convert the input to complex. Also compute the mean. */

	s = 0.;
	memset(h, 0, sizeof(fftw_complex) * len);
	for (i = 0; i < len; i++) {
		h[i][0] = data[i];
		s += data[i];
	}
	s /= len;

	/* FFT. */

	fftw_execute(p1); /* h -> H */

	/* Hilbert transform. The upper half-circle gets multiplied by
	two, and the lower half-circle gets set to zero.  The real axis
	is left alone. */

	l2 = (len + 1) / 2;
	for (i = 1; i < l2; i++) {
		H[i][0] *= 2.;
		H[i][1] *= 2.;
	}
	l2 = len / 2 + 1;
	for (i = l2; i < len; i++) {
		H[i][0] = 0.;
		H[i][1] = 0.;
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

		g[0] = (*window_function)(n, 0, gamma);
		l2 = len / 2 + 1;
		for (i = 1; i < l2; i++) {
			g[i] = g[len - i] = (*window_function)(n, i, gamma);
		}

		for (i = 0; i < len; i++) {
			s = g[i];
			k = n + i;
			if (k >= len) k -= len;
			G[i][0] = H[k][0] * s;
			G[i][1] = H[k][1] * s;
		}

		/* Inverse FFT the result to get the next row. */

		fftw_execute(p2); /* G -> h */
		for (i = 0; i < len; i++) {
			*p++ = h[i][0] / len;
			*p++ = h[i][1] / len;
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
	FILE *wisdom;
	static int planlen = 0;
	static fftw_plan p2;
	static fftw_complex *h, *H;

	/* Check for frequency defaults. */

	if (lo == 0 && hi == 0) {
		hi = len / 2;
	}

	/* Keep the arrays and plans around from last time, since this
	is a very common case. Reallocate them if they change. */

	if (len != planlen && planlen > 0) {
		fftw_destroy_plan(p2);
		fftw_free(h);
		fftw_free(H);
		planlen = 0;
	}

	if (planlen == 0) {
		planlen = len;
		h = fftw_malloc(sizeof(fftw_complex) * len);
		H = fftw_malloc(sizeof(fftw_complex) * len);

		/* Get any accumulated wisdom. */

		set_wisfile();
		wisdom = fopen(Wisfile, "r");
		if (wisdom) {
			fftw_import_wisdom_from_file(wisdom);
			fclose(wisdom);
		}

		/* Set up the fftw plans. */

		p2 = fftw_plan_dft_1d(len, H, h, FFTW_BACKWARD, FFTW_MEASURE);

		/* Save the wisdom. */

		wisdom = fopen(Wisfile, "w");
		if (wisdom) {
			fftw_export_wisdom_to_file(wisdom);
			fclose(wisdom);
		}
	}

	/* Sum the complex array across time. */

	memset(H, 0, sizeof(fftw_complex) * len);
	p = data;
	for (n = lo; n <= hi; n++) {
		for (i = 0; i < len; i++) {
			H[n][0] += *p++;
			H[n][1] += *p++;
		}
	}

	/* Invert the Hilbert transform. */

	l2 = (len + 1) / 2;
	for (i = 1; i < l2; i++) {
		H[i][0] /= 2.;
		H[i][1] /= 2.;
	}
	l2 = len / 2 + 1;
	for (i = l2; i < len; i++) {
		H[i][0] = H[len - i][0];
		H[i][1] = -H[len - i][1];
	}

	/* Inverse FFT. */

	fftw_execute(p2); /* H -> h */
	p = result;
	for (i = 0; i < len; i++) {
		*p++ = h[i][0] / len;
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
	FILE *wisdom;
	static int planlen = 0;
	static fftw_plan p1, p2;
	static fftw_complex *h, *H;

	/* Keep the arrays and plans around from last time, since this
	is a very common case. Reallocate them if they change. */

	if (len != planlen && planlen > 0) {
		fftw_destroy_plan(p1);
		fftw_destroy_plan(p2);
		fftw_free(h);
		fftw_free(H);
		planlen = 0;
	}

	if (planlen == 0) {
		planlen = len;
		h = fftw_malloc(sizeof(fftw_complex) * len);
		H = fftw_malloc(sizeof(fftw_complex) * len);

		/* Get any accumulated wisdom. */

		set_wisfile();
		wisdom = fopen(Wisfile, "r");
		if (wisdom) {
			fftw_import_wisdom_from_file(wisdom);
			fclose(wisdom);
		}

		/* Set up the fftw plans. */

		p1 = fftw_plan_dft_1d(len, h, H, FFTW_FORWARD, FFTW_MEASURE);
		p2 = fftw_plan_dft_1d(len, H, h, FFTW_BACKWARD, FFTW_MEASURE);

		/* Save the wisdom. */

		wisdom = fopen(Wisfile, "w");
		if (wisdom) {
			fftw_export_wisdom_to_file(wisdom);
			fclose(wisdom);
		}
	}

	/* Convert the input to complex. */

	memset(h, 0, sizeof(fftw_complex) * len);
	for (i = 0; i < len; i++) {
		h[i][0] = data[i];
	}

	/* FFT. */

	fftw_execute(p1); /* h -> H */

	/* Hilbert transform. The upper half-circle gets multiplied by
	two, and the lower half-circle gets set to zero.  The real axis
	is left alone. */

	l2 = (len + 1) / 2;
	for (i = 1; i < l2; i++) {
		H[i][0] *= 2.;
		H[i][1] *= 2.;
	}
	l2 = len / 2 + 1;
	for (i = l2; i < len; i++) {
		H[i][0] = 0.;
		H[i][1] = 0.;
	}

	/* Inverse FFT. */

	fftw_execute(p2); /* H -> h */

	/* Fill in the rows of the result. */

	p = result;
	for (i = 0; i < len; i++) {
		*p++ = h[i][0] / len;
		*p++ = h[i][1] / len;
	}
}
