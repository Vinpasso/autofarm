//
// Created by Vincent Bode on 06/01/2022.
//

#include "ExecInvocationParam.h"


void AutoFarm::from_json(const json &j, AutoFarm::ExecInvocationParam &param) {
    j.at("command").get_to(param.command);
    j.at("arguments").get_to(param.arguments);
    j.at("environment").get_to(param.environment);
}

void AutoFarm::to_json(json &j, const AutoFarm::ExecInvocationParam &param) {
    j = json{{"command",   param.command},
             {"arguments", param.arguments},
             {"environment",       param.environment}};
}

std::vector<std::string> AutoFarm::stringPointerStringToVector(char *const stringPointerString[]) {
    std::vector<std::string> result;
    int index = 0;
    while (stringPointerString[index] != nullptr) {
        result.emplace_back(stringPointerString[index]);
        index++;
    }
    return result;
}

std::unique_ptr<char *[]> AutoFarm::vectorToStringPointerString(std::vector<std::string> &input) {
    auto result = std::make_unique<char *[]>(input.size() + 1);
    for (int i = 0; i < input.size(); ++i) {
        result[i] = input[i].data();
    }
    result[input.size()] = nullptr;
    return result;
}

AutoFarm::ExecInvocationParam::ExecInvocationParam(std::string command,
                                                   char *const arguments[],
                                                   char *const environment[]) :
        command(std::move(command)),
        arguments(stringPointerStringToVector(arguments)),
        environment(stringPointerStringToVector(environment)) {}

