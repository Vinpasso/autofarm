#include <dlfcn.h>
#include <unistd.h>
#include "exec_intercept.h"
#include "Client.h"

using execvpe_t_ptr = int (*)(const char *, char *const[], char *const[]);

static execvpe_t_ptr real_execvpe = (execvpe_t_ptr) dlsym(RTLD_NEXT, "execvpe");

// Our current environment to use when no environment specified.
extern char **environ;

std::unique_ptr<AutoFarm::Client> globalClient;

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
    if(!globalClient) {
        globalClient = std::make_unique<AutoFarm::Client>();
    }
    return globalClient->getOutsourceCommand(param);
}
