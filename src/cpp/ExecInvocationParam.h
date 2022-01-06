//
// Created by Vincent Bode on 06/01/2022.
//

#ifndef CPP_EXECINVOCATIONPARAM_H
#define CPP_EXECINVOCATIONPARAM_H


#include <vector>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

namespace AutoFarm {

    struct ExecInvocationParam {
        std::string command;
        std::vector<std::string> arguments;
        std::vector<std::string> environment;

        ExecInvocationParam() = default;
        ExecInvocationParam(std::string command, char *const arguments[], char *const environment[]);
    };

    void to_json(json &j, const ExecInvocationParam &param);

    void from_json(const json &j, ExecInvocationParam &param);

    // Convert a null terminated "string" of pointers to string to a vector of strings
    std::vector<std::string> stringPointerStringToVector(char *const stringPointerString[]);

    // Convert a vector of strings back to a null terminated "string" of pointers to string
    std::unique_ptr<char *[]> vectorToStringPointerString(std::vector<std::string> &input);
}


#endif //CPP_EXECINVOCATIONPARAM_H
