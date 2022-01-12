//
// Created by Vincent Bode on 12/01/2022.
//

#include <gtest/gtest.h>
#include <gmock/gmock.h>
#include "../src/ExecInvocationParam.h"

TEST(ExecInvocationParamTest, JsonTest) {
    // JSON output format by library: no spaces, alphabetic field order.
    const char *request_str = R"({"arguments":["TARGET-COMMAND","TARGET-PARAM"],"command":"TARGET-COMMAND","environment":[]})";
    auto request = json::parse(request_str);

    // Load the request from json
    auto param = request.get<AutoFarm::ExecInvocationParam>();

    ASSERT_EQ(param.command, "TARGET-COMMAND");
    ASSERT_THAT(param.arguments, ::testing::ElementsAre("TARGET-COMMAND", "TARGET-PARAM"));
    ASSERT_THAT(param.environment, ::testing::IsEmpty());

    // Back to JSON
    auto result = request.dump();
    ASSERT_EQ(result, request_str);
}

TEST(ExecInvocationParamTest, StringPointerTest) {
    // Convert char pointer sequence to a vector of strings
    char * test_param[] = {
        "ARG1",
        "ARG2",
        nullptr
    };

    auto result = AutoFarm::stringPointerStringToVector(test_param);
    ASSERT_THAT(result, ::testing::ElementsAre("ARG1", "ARG2"));

    // Convert back
    auto convertBackResult = AutoFarm::vectorToStringPointerString(result);
    ASSERT_STREQ(convertBackResult.get()[0], "ARG1");
    ASSERT_STREQ(convertBackResult.get()[1], "ARG2");
    ASSERT_STREQ(convertBackResult.get()[2], nullptr);

    // Check case that there is no arg
    char *test_param_2[] = {nullptr};
    result = AutoFarm::stringPointerStringToVector(test_param_2);
    ASSERT_THAT(result, ::testing::IsEmpty());
}