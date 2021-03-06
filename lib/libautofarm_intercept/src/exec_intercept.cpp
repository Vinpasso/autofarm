#include <dlfcn.h>
#include <unistd.h>
#include <cstdarg>
#include "exec_intercept.h"
#include "Client.h"

using execvpe_t_ptr = int (*)(const char *, char *const[], char *const[]);

static execvpe_t_ptr real_execvpe = (execvpe_t_ptr) dlsym(RTLD_NEXT, "execvpe");

// Our current environment to use when no environment specified.
extern char **environ;

[[maybe_unused]] int execve(const char *arg, char *const argv[], char *const envp[]) {
    auto newParam = tryOutsourceCommand(
            AutoFarm::ExecInvocationParam(
                    arg,
                    argv,
                    envp
            )
    );
    return call_execvpe(newParam);
}

[[maybe_unused]] int execv(const char *arg, char *const argv[]) {
    auto newParam = tryOutsourceCommand(
            AutoFarm::ExecInvocationParam(
                    arg,
                    argv,
                    environ
            )
    );
    return call_execvpe(newParam);
}

[[maybe_unused]] int execl(const char *path, const char *arg, ...) {
    va_list list;
    // Not naming last parameter on purpose. We need to include arg
    va_start(list, path);

    char *const *argPointer = va_arg(list, char* const*);
    va_end(list);
    auto newParam = tryOutsourceCommand(
            AutoFarm::ExecInvocationParam(
                    path,
                    argPointer,
                    environ
            )
    );
    return call_execvpe(newParam);
}

[[maybe_unused]] int execlp(const char *file, const char *arg, ...) {
    va_list list;
    // Not naming last parameter on purpose. We need to include arg
    va_start(list, file);

    char *const *argPointer = va_arg(list, char* const*);
    va_end(list);
    auto newParam = tryOutsourceCommand(
            AutoFarm::ExecInvocationParam(
                    file,
                    argPointer,
                    environ
            )
    );
    return call_execvpe(newParam);
}

[[maybe_unused]] int execle(const char *path, const char *arg, ...) {
    // Environment is after the vararg.
    va_list list;
    // Not naming last parameter on purpose. We need to include arg
    va_start(list, path);

    char *const *argPointer = va_arg(list, char* const*);
    char** envPointer;
    while(true) {
        if(va_arg(list, void*) == nullptr) {
            envPointer = va_arg(list, char**);
            break;
        }
    }
    va_end(list);
    auto newParam = tryOutsourceCommand(
            AutoFarm::ExecInvocationParam(
                    path,
                    argPointer,
                    envPointer
            )
    );
    return call_execvpe(newParam);

}

[[maybe_unused]] int execvp(const char *file, char *const argv[]) {
    auto newParam = tryOutsourceCommand(
            AutoFarm::ExecInvocationParam(
                    file,
                    argv,
                    environ
            )
    );
    return call_execvpe(newParam);
}

[[maybe_unused]] int execvpe(const char *file, char *const argv[], char *const envp[]) {
    auto newParam = tryOutsourceCommand(
            AutoFarm::ExecInvocationParam(
                    file,
                    argv,
                    envp
            )
    );
    return call_execvpe(newParam);
}

int call_execvpe(AutoFarm::ExecInvocationParam &newParam) {
    auto arguments = AutoFarm::vectorToStringPointerString(newParam.arguments);
    auto environment = AutoFarm::vectorToStringPointerString(newParam.environment);
    return (*real_execvpe)(
            newParam.command.c_str(),
            arguments.get(),
            environment.get()
    );
}

AutoFarm::ExecInvocationParam tryOutsourceCommand(const AutoFarm::ExecInvocationParam &param) {
    auto localClient = AutoFarm::Client();
    return localClient.getOutsourceCommand(param);
}
