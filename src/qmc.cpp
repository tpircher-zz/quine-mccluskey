#include <pybind11/pybind11.h>
#include <sstream>

using namespace pybind11::literals;
int add(int i, int j) {
    return i + j;
}

std::string num2str(int n_bits, int i) {
    std::ostringstream out;
    for (int k = n_bits - 1; k >= 0; --k) {
        out << (((i & (1 << k)) != 0) ? '1' : '0');
    }
    return out.str();
}


PYBIND11_MODULE(_qmc, m) {
    m.doc() = "pybind11 example plugin"; // optional module docstring

    m.def("add", &add, "A function that adds two numbers");
    m.def("num2str", &num2str, "n_bits"_a, "i"_a);
}
