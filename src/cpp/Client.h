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
        tcp::socket socket;

    public:
        Client();

        void connect();

        ExecInvocationParam getOutsourceCommand(const ExecInvocationParam &parameters);
    };

}
#endif //CPP_CLIENT_H
