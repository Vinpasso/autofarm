//
// Created by Vincent Bode on 12/01/2022.
//
#include <iostream>
#include <unistd.h>

int main(int argc, char** argv) {
    if(argc != 2) {
        std::cerr << "Error: Please include function which to invoke." << std::endl;
        return 255;
    }
    auto arg = std::string(argv[1]);

    if(arg == "execv") {
        // Call /bin/false. This should be intercepted
        char* const args[] = {"false", nullptr};
        execv("/bin/false", args);
    } else {
        std::cerr << "Error: function unknown." << std::endl;
        return 255;
    }
}