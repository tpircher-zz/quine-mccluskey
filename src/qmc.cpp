#include <cassert>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <sstream>
#include <optional>
#include <vector>

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

std::optional<std::string> reduceSimpleXorTerms(const std::string& t1, const std::string& t2) {
    assert(t1.size() == t2.size());
    int difft10 = 0;
    int difft20 = 0;
    std::vector<std::string> ret;
    std::ostringstream out;
    for (std::size_t i = 0; i < t1.size(); ++i) {
        char t1c = t1[i];
        char t2c = t2[i];
        if (t1c == '^' || t2c == '^' || t1c == '~' || t2c == '~') {
            return std::nullopt;
        }
        if (t1c != t2c) {
            out << '^';
            if (t2c == '0') {
                difft10 += 1;
            } else {
                difft20 += 1;
            }
        } else {
            out << t1c;
        }
    }
    if (difft10 == 1 && difft20 == 1) {
        return out.str();
    }
    return std::nullopt;
}



PYBIND11_MODULE(_qmc, m) {
    m.doc() = "pybind11 example plugin"; // optional module docstring

    m.def("add", &add, "A function that adds two numbers");
    m.def("num2str", &num2str, "n_bits"_a, "i"_a);
    m.def("reduce_simple_xor_terms", &reduceSimpleXorTerms, "t1"_a, "t2"_a);
}
