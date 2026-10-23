#include <dlfcn.h>
#include <stdint.h>
#include <stdio.h>

typedef struct { uint8_t data[16]; } SDL_JoystickGUID;

int main(void) {
    void *lib = dlopen("libSDL2-2.0.so.0", RTLD_NOW);
    if (!lib) {
        fprintf(stderr, "%s\n", dlerror());
        return 1;
    }
    int (*init)(uint32_t) = dlsym(lib, "SDL_Init");
    int (*count)(void) = dlsym(lib, "SDL_NumJoysticks");
    const char *(*name)(int) = dlsym(lib, "SDL_JoystickNameForIndex");
    SDL_JoystickGUID (*guid)(int) = dlsym(lib, "SDL_JoystickGetDeviceGUID");
    void (*guid_string)(SDL_JoystickGUID, char *, int) = dlsym(lib, "SDL_JoystickGetGUIDString");
    void (*quit)(void) = dlsym(lib, "SDL_Quit");
    if (!init || !count || !name || !guid || !guid_string || !quit || init(0x200) != 0)
        return 2;
    for (int i = 0; i < count(); ++i) {
        char text[64] = {0};
        guid_string(guid(i), text, sizeof(text));
        printf("%d\t%s\t%s\n", i, text, name(i));
    }
    quit();
    return 0;
}
