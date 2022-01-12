//
// Created by Vincent Bode on 12/01/2022.
//

#include <gtest/gtest.h>
#include <gmock/gmock.h>
#include <thread>
#include <asio.hpp>
#include "../src/ExecInvocationParam.h"

TEST(InterceptTest, ProxyOk) {
    auto retcode = system("./autofarm_intercept_test_invoke_exec execv");
    auto exitcode = WEXITSTATUS(retcode);

    // Default return code of /bin/false
    ASSERT_EQ(exitcode, 1);
}

TEST(InterceptTest, MissingVarFallbackOk) {
    auto retcode = system("LD_PRELOAD=$PWD/libautofarm_intercept.so ./autofarm_intercept_test_invoke_exec execv");
    auto exitcode = WEXITSTATUS(retcode);

    // Still default return code of /bin/false
    ASSERT_EQ(exitcode, 1);
}

TEST(InterceptTest, Execv) {
    asio::io_context ioContext{};
    asio::ip::tcp::endpoint endpoint(asio::ip::make_address("127.0.0.1"), 6754);
    asio::ip::tcp::acceptor acceptor(ioContext);

    acceptor.open(endpoint.protocol());
    acceptor.bind(endpoint);
    acceptor.listen();

    auto serverThread = std::thread([&acceptor]() {
        auto connection = acceptor.accept();
        auto streambuf = asio::streambuf();
        auto outStream = std::ostream(&streambuf);

        outStream << R"({ "command": "true", "arguments": ["true"], "environment": [] })";
        outStream << '\0';

        asio::write(connection, streambuf);

    });

    auto retcode = system("LD_PRELOAD=$PWD/libautofarm_intercept.so "
                          "AUTOFARM_JOBSERVER_HOST=127.0.0.1 "
                          "AUTOFARM_JOBSERVER_PORT=6754 "
                          "./autofarm_intercept_test_invoke_exec execv");
    auto exitcode = WEXITSTATUS(retcode);

    // Should now have been patched to /bin/true
    ASSERT_EQ(exitcode, 0);

    serverThread.join();
}