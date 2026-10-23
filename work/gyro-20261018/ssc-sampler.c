// SPDX-License-Identifier: GPL-3.0-or-later
// ThorDS motion sampling through libssc. SSC units: m/s^2 and rad/s.
#include <glib.h>
#include <glib-unix.h>
#include <libssc/libssc-sensor-accelerometer.h>
#include <libssc/libssc-sensor-gyroscope.h>
#include <math.h>
#include <stdio.h>

static GMainLoop *loop;
static void accel_cb(SSCSensorAccelerometer *s, float x, float y, float z, void *p) {
    (void)s; (void)p;
    if (isfinite(x) && isfinite(y) && isfinite(z))
        printf("A %.9g %.9g %.9g\n", x, y, z);
}
static void gyro_cb(SSCSensorGyroscope *s, float x, float y, float z, void *p) {
    (void)s; (void)p;
    // Discard the firmware's initial full-scale placeholder samples.
    if (isfinite(x) && isfinite(y) && isfinite(z) &&
        !(fabsf(x) > 34.9f && fabsf(y) > 34.9f && fabsf(z) > 34.9f))
        printf("G %.9g %.9g %.9g\n", x, y, z);
}
static gboolean stop_cb(void *p) {
    (void)p; g_main_loop_quit(loop); return G_SOURCE_REMOVE;
}
int main(void) {
    GError *error = NULL;
    setvbuf(stdout, NULL, _IOLBF, 0);
    SSCSensorAccelerometer *a = ssc_sensor_accelerometer_new_sync(NULL, &error);
    if (!a) goto fail;
    SSCSensorGyroscope *g = ssc_sensor_gyroscope_new_sync(NULL, &error);
    if (!g) goto fail;
    g_object_set(a, SSC_SENSOR_SAMPLE_RATE, 60.f, NULL);
    g_object_set(g, SSC_SENSOR_SAMPLE_RATE, 60.f, NULL);
    g_signal_connect(a, "measurement", G_CALLBACK(accel_cb), NULL);
    g_signal_connect(g, "measurement", G_CALLBACK(gyro_cb), NULL);
    if (!ssc_sensor_accelerometer_open_sync(a, NULL, &error)) goto fail;
    if (!ssc_sensor_gyroscope_open_sync(g, NULL, &error)) {
        ssc_sensor_accelerometer_close_sync(a, NULL, NULL); goto fail;
    }
    loop = g_main_loop_new(NULL, FALSE);
    g_unix_signal_add(SIGTERM, stop_cb, NULL);
    g_unix_signal_add(SIGINT, stop_cb, NULL);
    g_main_loop_run(loop);
    ssc_sensor_gyroscope_close_sync(g, NULL, NULL);
    ssc_sensor_accelerometer_close_sync(a, NULL, NULL);
    g_object_unref(g); g_object_unref(a); g_main_loop_unref(loop);
    return 0;
fail:
    fprintf(stderr, "SSC motion unavailable: %s\n", error ? error->message : "unknown error");
    g_clear_error(&error); return 1;
}
