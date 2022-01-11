//
// Created by Vincent Bode on 06/01/2022.
//

#ifndef CPP_CLIENT_H
#define CPP_CLIENT_H

#include "asio.hpp"
#include "ExecInvocationParam.h"

using asio::ip::tcp;

namespace AutoFarm {

    class Client {
    private:
        asio::io_context ioContext{};

        tcp::socket socket;

        asio::streambuf request;
        std::ostream requestStream;

        asio::streambuf response;
        std::istream responseStream;
    public:
        Client();

        virtual ~Client();

        void connect();

        ExecInvocationParam getOutsourceCommand(const ExecInvocationParam &parameters);
    };

}
#endif //CPP_CLIENT_H
