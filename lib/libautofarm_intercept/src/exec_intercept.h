//
// Created by Vincent Bode on 06/01/2022.
//

#ifndef CPP_EXEC_INTERCEPT_H
#define CPP_EXEC_INTERCEPT_H

#include "ExecInvocationParam.h"

AutoFarm::ExecInvocationParam tryOutsourceCommand(const AutoFarm::ExecInvocationParam &param);

int call_execvpe(AutoFarm::ExecInvocationParam &newParam);


#endif //CPP_EXEC_INTERCEPT_H
