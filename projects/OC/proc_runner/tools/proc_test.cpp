#include "proc_runner.hpp"
#include <iostream>

static void usage() {
    std::cout << "Usage:\n"
              << "  proc_test <program> [args...]\n"
              << "Examples:\n"
              << "  proc_test /bin/echo hello\n"
#ifdef _WIN32
              << "  proc_test cmd /c \"echo hello\"\n"
#endif
              ;
}

int main(int argc, char** argv) {
    if (argc < 2) {
        usage();
        return 2;
    }

    std::string program = argv[1];
    std::vector<std::string> args;
    for (int i = 2; i < argc; ++i) args.emplace_back(argv[i]);

    auto p = proc_runner::spawn(program, args);
    if (!p.has_value() || !p->valid()) {
        std::cerr << "spawn failed\n";
        return 1;
    }

    std::cout << "spawned pid=" << p->pid() << "\n";

    auto r = p->wait();
    if (r.status == proc_runner::WaitStatus::Exited) {
        std::cout << "exited code=" << r.exit_code << "\n";
        return r.exit_code;
    }

    std::cerr << "wait failed\n";
    return 3;
}
