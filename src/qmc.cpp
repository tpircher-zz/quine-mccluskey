#include <cassert>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <sstream>
#include <optional>
#include <string>
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

std::optional<std::string> reduceSimpleXnorTerms(const std::string& t1, const std::string& t2) {
    int difft10 = 0;
    int difft20 = 0;
    std::ostringstream out;
    for (std::size_t i = 0; i < t1.size(); ++i) {
        char t1c = t1[i];
        char t2c = t2[i];
        if (t1c == '^' || t2c == '^' || t1c == '~' || t2c == '~') {
            return std::nullopt;
        }
        if (t1c != t2c) {
            out << '~';
            if (t2c == '0') {
                difft10 += 1;
            } else {
                difft20 += 1;
            }
        } else {
            out << t1c;
        }
    }
    if ((difft10 == 2 && difft20 == 0) || (difft10 == 0 && difft20 == 2)) {
        return out.str();
    }
    return std::nullopt;
}

std::set<std::string> permutations(const std::string& value, const std::set<std::string>& exclude) {
    std::set<int> exclude_int;
    for (const auto& e : exclude) {
        exclude_int.insert(std::stoi(e, nullptr, 2));
    }
    int n_bits = value.size();
    int n_xor = 0;
    int xor_value = 0;
    int seen_xors = 0;
    for (const auto& c : value) {
        if (c == '^' || c == '~') {
            ++n_xor;
        }
    }
    std::vector<char> res(n_bits, '0');
    int i = 0;
    int direction = 1;
    std::set<std::string> result;
    while (i >= 0) {
        if (value[i] == '0' || value[i] == '1') {
            // binary constant
            res[i] = value[i];
        } else if (value[i] == '-') {
            // dontcare operator
            if (direction == 1) {
                res[i] = '0';
            } else if (res[i] == '0') {
                res[i] = '1';
                direction = 1;
            }
        } else if (value[i] == '^') {
            // XOR operator
            seen_xors += direction;
            if (direction == 1) {
                if (seen_xors == n_xor && xor_value == 0) {
                    res[i] = '1';
                } else {
                    res[i] = '0';
                }
            } else {
                if (res[i] == '0' && seen_xors < n_xor - 1) {
                    res[i] = '1';
                    direction = 1;
                    seen_xors += 1;
                }
            }
            if (res[i] == '1') {
                xor_value = xor_value ^ 1;
            }
        } else if (value[i] == '~') {
            // XNOR operator
            seen_xors += direction;
            if (direction == 1) {
                if (seen_xors == n_xor && xor_value == 1) {
                    res[i] = '1';
                } else {
                    res[i] = '0';
                }
            } else {
                if (res[i] == '0' && seen_xors < n_xor - 1) {
                    res[i] = '1';
                    direction = 1;
                    seen_xors += 1;
                }
            }
            if (res[i] == '1') {
                xor_value = xor_value ^ 1;
            }
        } else {
            // unknown input
            res[i] = '#';
        }

        i += direction;
        if (i == n_bits) {
            direction = -1;
            i = n_bits - 1;
            std::string bitstring(std::begin(res), std::end(res));
            int val = std::stoi(bitstring, nullptr, 2);
            if (exclude_int.find(val) == std::end(exclude_int)) {
                result.insert(bitstring);
            }
        }
    }
    return result;
}

int get_term_rank(const std::string& term, int term_range) {
    int n = 0;
    for (char t : term) {
        switch (t) {
        case '-':
            n += 8;
            break;
        case '^':
            n += 4;
            break;
        case '~':
            n += 2;
            break;
        case '1':
            n += 1;
            break;
        }
    }
    return 4 * term_range + n;
}

PYBIND11_MODULE(_qmc, m) {
    m.doc() = "pybind11 example plugin"; // optional module docstring

    m.def("add", &add, "A function that adds two numbers");
    m.def("num2str", &num2str, "n_bits"_a, "i"_a);
    m.def("reduce_simple_xor_terms", &reduceSimpleXorTerms, "t1"_a, "t2"_a);
    m.def("reduce_simple_xnor_terms", &reduceSimpleXnorTerms, "t1"_a, "t2"_a);
    m.def("permutations", &permutations, "value"_a, "exclude"_a);
    m.def("get_term_rank", &get_term_rank, "term"_a, "term_range"_a);
}
