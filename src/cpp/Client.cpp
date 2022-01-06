//
// Created by Vincent Bode on 06/01/2022.
//

#include <iostream>
#include "Client.h"

asio::io_context ioContext{};

AutoFarm::ExecInvocationParam AutoFarm::Client::getOutsourceCommand(const AutoFarm::ExecInvocationParam &parameters) {
    try {
        if(!socket.is_open()) {
            throw std::runtime_error("Not connected to jobserver.");
        }

        asio::streambuf request;
        std::ostream requestStream(&request);
        requestStream << json(parameters) << "\0";

        asio::write(socket, request);

        asio::streambuf response;
        asio::read_until(socket, response, "\0");
        std::istream responseStream(&response);
        json responseJSON;
        responseStream >> responseJSON;
        return responseJSON.get<AutoFarm::ExecInvocationParam>();
    } catch(std::exception &e) {
        std::cerr << "[AutoFarm] Failed to offload invocation. Reason: " << e.what() << std::endl;
        std::cerr << "[AutoFarm] Falling back to local invocation: " << parameters.command;
        for(const auto &argument : parameters.arguments) {
            std::cerr << " " << argument;
        }
        std::cerr << std::endl;
        return parameters;
    }
}

void AutoFarm::Client::connect() {
    try {
        char *connectAddress = getenv("AUTOFARM_JOBSERVER_HOST");
        if(connectAddress == nullptr) {
            throw std::runtime_error("Missing jobserver host environment variable: AUTOFARM_JOBSERVER_HOST");
        }

        char *connectPort = getenv("AUTOFARM_JOBSERVER_PORT");
        if(connectPort == nullptr) {
            throw std::runtime_error("Missing jobserver port environment variable: AUTOFARM_JOBSERVER_PORT");
        }

        tcp::resolver resolver(ioContext);
        asio::connect(socket, resolver.resolve(connectAddress, connectPort));
    } catch(std::exception &e) {
        std::cerr << "[AutoFarm] Failed to connect to jobserver. Reason: " << e.what() << std::endl;
    }
}

AutoFarm::Client::Client() : socket(tcp::socket(ioContext)) {
    connect();
}
