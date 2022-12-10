#include <cassert>
#include <iterator>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <sstream>
#include <optional>
#include <string>
#include <tuple>
#include <vector>
#include <algorithm>
#include <iostream>

namespace py = pybind11;
using namespace pybind11::literals;

struct ResultWithProfile {
    std::optional<std::set<std::string>> result;
    int profile_cmp = 0;
    int profile_xor = 0;
    int profile_xnor = 0;
};


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

std::set<std::string> getEssentialImplicants(int n_bits, const std::set<std::string>& terms, const std::set<std::string>& dc) {
    std::map<std::string, std::set<std::string>> perms;
    for (const auto& t : terms) {
        for (const auto& p : permutations(t, {})) {
            if (dc.find(p) == std::end(dc)) {
                perms[t].insert(p);
            }
        }
    }
    std::set<std::string> ei_range;
    std::set<std::string> ei;
    std::map<int, std::set<std::string>> groups;
    for (const auto& term : terms) {
        auto n = get_term_rank(term, perms[term].size());
        groups[n].insert(term);
    }
    for (auto it1 = groups.rbegin(); it1 != groups.rend(); ++it1) {
        const auto& t2 = it1->first;
        for (auto it2 = it1->second.rbegin(); it2 != it1->second.rend(); ++it2) {
            const std::string& g = *it2;
            if (!std::includes(std::begin(ei_range), std::end(ei_range), std::begin(perms[g]), std::end(perms[g]))) {
                ei.insert(g);
                ei_range.insert(std::begin(perms[g]), std::end(perms[g]));
            }
        }
    }
    if (ei.empty()) {
        ei = std::set<std::string>({ std::string(n_bits, '-') });
    }
    return ei;
}

std::tuple<std::vector<std::size_t>, std::vector<std::size_t>, std::vector<std::size_t>, std::vector<std::size_t>, std::vector<std::size_t>> getTerms(const std::string& implicant) {
    std::vector<std::size_t> term_ones;
    std::vector<std::size_t> term_zeros;
    std::vector<std::size_t> term_xors;
    std::vector<std::size_t> term_xnors;
    std::vector<std::size_t> term_dcs;
    for (std::size_t i = 0; i < implicant.size(); ++i) {
        switch (implicant[i]) {
        case '1':
            term_ones.push_back(i);
            break;
        case '0':
            term_zeros.push_back(i);
            break;
        case '^':
            term_xors.push_back(i);
            break;
        case '~':
            term_xnors.push_back(i);
            break;
        case '-':
            term_dcs.push_back(i);
            break;
        }
    }

    return std::make_tuple(term_ones, term_zeros, term_xors, term_xnors, term_dcs);
}

double complexity(const std::string& implicant) {
    double ret = 0;
    auto terms = getTerms(implicant);
    ret += 1.00 * std::get<0>(terms).size();
    ret += 1.50 * std::get<1>(terms).size();
    ret += 1.25 * std::get<2>(terms).size();
    ret += 1.75 * std::get<3>(terms).size();
    return ret;
}

std::optional<std::string> combineImplicants(const std::string& a, const std::string& b, const std::set<std::string>& dc) {
    std::set<std::string> permutations_a = permutations(a, dc);
    std::set<std::string> permutations_b = permutations(b, dc);
    std::vector<std::size_t> a_term_dcs = std::get<4>(getTerms(a));
    std::vector<std::size_t> b_term_dcs = std::get<4>(getTerms(b));
    std::vector<char> a_potential(std::begin(a), std::end(a));
    std::vector<char> b_potential(std::begin(b), std::end(b));
    for (auto index : a_term_dcs) {
        a_potential[index] = b[index];
    }
    for (auto index : b_term_dcs) {
        b_potential[index] = a[index];
    }
    std::vector<std::string> valid;
    std::string a_str(std::begin(a_potential), std::end(a_potential));
    std::string b_str(std::begin(b_potential), std::end(b_potential));
    std::set<std::string> u;
    std::set_union(std::begin(permutations_a), std::end(permutations_a), std::begin(permutations_b), std::end(permutations_b), std::inserter(u, std::begin(u)));
    for (const auto& x : { a_str, b_str }) {
        if (permutations(x, dc) == u) {
            valid.push_back(x);
        }
    }
    if (!valid.empty()) {
        auto min_it = std::min_element(
            std::begin(valid), 
            std::end(valid), 
            [](const std::string& lhs, const std::string& rhs) { return complexity(lhs) < complexity(rhs); }
        );
        return *min_it;
    }
    return std::nullopt;
}

std::set<std::string> reduceImplicants(int n_bits, std::set<std::string> implicants, const std::set<std::string>& dc) {
    while (true) {
        bool did_break = false;
        for (auto it1 = implicants.begin(); it1 != implicants.end(); ++it1) {
            auto it2 = it1;
            ++it2;
            for (; it2 != implicants.end(); ++it2) {
                const auto& a = *it1;
                const auto& b = *it2;
                auto replacement = combineImplicants(a, b, dc);
                if (replacement) {
                    implicants.erase(a);
                    implicants.erase(b);
                    implicants.insert(*replacement);
                    did_break = true;
                    break;
                }
            }
        }
        if (!did_break) {
            break;
        }
    }

    std::map<std::string, std::set<std::string>> coverage;
    for (const auto& implicant : implicants) {
        coverage[implicant] = {};
        for (const auto& n : permutations(implicant, {})) {
            if (dc.find(n) == std::end(dc)) {
                coverage[implicant].insert(n);
            }
        }
    }

    while (true) {
        std::vector<std::string> redundant;
        for (auto it = std::begin(coverage); it != std::end(coverage); ++it) {
            const auto& this_implicant = it->first;
            const auto& this_coverage = coverage[this_implicant];
            std::set<std::string> other_coverage;
            for (auto it_inner = std::begin(coverage); it_inner != std::end(coverage); ++it_inner) {
                const auto& other_implicant = it_inner->first;
                if (it_inner == it) {
                    continue;
                }
                other_coverage.insert(std::begin(coverage[other_implicant]), std::end(coverage[other_implicant]));
            }
            bool is_subset = std::includes(std::begin(other_coverage), std::end(other_coverage), std::begin(this_coverage), std::end(this_coverage));
            if (is_subset) {
                redundant.push_back(this_implicant);
            }
        }
        if (!redundant.empty()) {
            auto worst = std::min_element(std::begin(redundant), std::end(redundant), [](const std::string& lhs, const std::string& rhs) { return complexity(lhs) < complexity(rhs); });
            coverage.erase(*worst);
        } else {
            break;
        }
    }
    if (coverage.empty()) {
        coverage[std::string(n_bits, '-')] = {};
    }
    std::set<std::string> result;
    for (const auto& [key, value] : coverage) {
        result.insert(key);
    }
    return result;
}

std::string replate_ith(const std::string& str, std::size_t i, char new_char) {
    if (i == 0) {
        return new_char + str.substr(1);
    }
    return str.substr(0, i) + new_char + str.substr(i + 1);
}

ResultWithProfile getPrimeImplicants(int n_bits, bool use_xor, std::set<std::string> terms) {
    int profile_cmp = 0;
    int profile_xor = 0;
    int profile_xnor = 0;

    int n_groups = n_bits + 1;
    std::set<std::string> marked;

    std::vector<std::set<std::string>> groups_1(n_groups);
    for (const auto& t : terms) {
        int n_bits = 0;
        for (char c : t) {
            if (c == '1') {
                ++n_bits;
            }
        }
        groups_1[n_bits].insert(t);
    }

    if (use_xor) {
        for (std::size_t gi = 0; gi < groups_1.size(); ++gi) {
            const auto& group = groups_1[gi];
            for (const auto& t1 : group) {
                for (const auto& t2 : group) {
                    auto t12 = reduceSimpleXorTerms(t1, t2);
                    if (t12.has_value()) {
                        terms.insert(*t12);
                    }
                }
                if (gi < n_groups - 2) {
                    for (const auto& t2 : groups_1[gi + 2]) {
                        auto t12 = reduceSimpleXnorTerms(t1, t2);
                        if (t12.has_value()) {
                            terms.insert(*t12);
                        }
                    }
                }
            }
        }
    }

    bool done = false;
    std::map<std::tuple<std::size_t, std::size_t, std::size_t>, std::set<std::string>> groups;
    int counter = 0;
    while (!done) {
        ++counter;
        groups.clear();
        for (const auto& t : terms) {
            std::size_t n_ones = 0;
            std::size_t n_xor = 0;
            std::size_t n_xnor = 0;
            for (char c : t) {
                switch (c) {
                case '1':
                    ++n_ones;
                    break;
                case '^':
                    ++n_xor;
                    break;
                case '~':
                    ++n_xnor;
                    break;
                }
            }
            assert(n_xor == 0 || n_xnor == 0);

            auto key = std::make_tuple(n_ones, n_xor, n_xnor);
            groups[key].insert(t);
        }

        terms.clear();
        std::set<std::string> used;

        // Find prime implicants
        for (auto it_group = std::begin(groups); it_group != std::end(groups); ++it_group) {
            const auto& key = it_group->first;
            
            auto key_next = std::make_tuple(std::get<0>(key) + 1, std::get<1>(key), std::get<2>(key));
            
            if (groups.find(key_next) != std::end(groups)) {
                const auto& group_next = groups[key_next];
                for (const auto& t1 : groups[key]) {
                    for (std::size_t i = 0; i < t1.size(); ++i) {
                        const auto& c1 = t1[i];
                        if (c1 == '0') {
                            ++profile_cmp;
                            std::string t2 = replate_ith(t1, i, '1');
                            // print(key, key_next, groups.find(key_next) != std::end(groups), t1, i, t2);
                            if (group_next.find(t2) != std::end(group_next)) {
                                auto t12 = replate_ith(t1, i, '-');
                                used.insert(t1);
                                used.insert(t2);
                                terms.insert(t12);
                            }
                        }
                    }
                }
            }
        }

        // Find XOR combinations
        for (auto it = std::begin(groups); it != std::end(groups); ++it) {
            const auto& key = it->first;
            if (std::get<1>(key) == 0) {
                continue;
            }            
            auto key_complement = std::make_tuple(std::get<0>(key) + 1, std::get<2>(key), std::get<1>(key));
            if (groups.find(key_complement) != std::end(groups)) {
                for (const auto& t1 : groups[key]) {
                    std::string t1_complement = t1;
                    std::replace(std::begin(t1_complement), std::end(t1_complement), '^', '~');
                    for (std::size_t i = 0; i < t1.size(); ++i) {
                        char c1 = t1[i];
                        if (c1 == '0') {
                            ++profile_xor;
                            std::string t2 = replate_ith(t1_complement, i, '1');
                            if (groups[key_complement].find(t2) != std::end(groups[key_complement])) {
                                std::string t12 = replate_ith(t1, i, '^');
                                used.insert(t1);
                                terms.insert(t12);
                            }
                        }
                    }
                }
            }
        }

        // Find XNOR combinations
        for (auto it = std::begin(groups); it != std::end(groups); ++it) {
            const auto& key = it->first;
            if (std::get<2>(key) == 0) {
                continue;
            }
            auto key_complement = std::make_tuple(std::get<0>(key) + 1, std::get<2>(key), std::get<1>(key));
            if (groups.find(key_complement) != std::end(groups)) {
                for (const auto& t1 : groups[key]) {
                    std::string t1_complement = t1;
                    std::replace(std::begin(t1_complement), std::end(t1_complement), '~', '^');
                    for (std::size_t i = 0; i < t1.size(); ++i) {
                        char c1 = t1[i];
                        if (c1 == '0') {
                            ++profile_xnor;
                            std::string t2 = replate_ith(t1_complement, i, '1');
                            if (groups[key_complement].find(t2) != std::end(groups[key_complement])) {
                                std::string t12 = replate_ith(t1, i, '~');
                                used.insert(t1);
                                terms.insert(t12);
                            }
                        }
                    }
                }
            }
        }

        // Add the unused terms to the list of marked terms
        for (auto it = std::begin(groups); it != std::end(groups); ++it) {
            const auto& g = it->second;
            std::set<std::string> diff;
            std::set_difference(std::begin(g), std::end(g), std::begin(used), std::end(used), std::inserter(diff, std::begin(diff)));
            marked.insert(std::begin(diff), std::end(diff));
        }

        if (used.empty()) {
            done = true;
        }
    }

    std::set<std::string> pi = marked;
    for (const auto& [key, g] : groups) {
        pi.insert(std::begin(g), std::end(g));
    }
    
    return ResultWithProfile{.result = pi, .profile_cmp = profile_cmp, .profile_xor = profile_xor, .profile_xnor = profile_xnor};
}

ResultWithProfile simplifyLosWithProfile(const std::vector<std::string>& ones, const std::vector<std::string>& dc, std::optional<int> num_bits, bool use_xor = false) {
    std::set<std::string> terms;
    terms.insert(std::begin(ones), std::end(ones));
    terms.insert(std::begin(dc), std::end(dc));
    if (terms.empty()) {
        return ResultWithProfile{.result = std::nullopt, .profile_cmp = 0, .profile_xor = 0, .profile_xnor = 0};
    }
    std::size_t n_bits;
    if (num_bits.has_value()) {
        n_bits = *num_bits;
    } else {
        std::size_t n_bits_min = 0;
        std::size_t n_bits_max = 0;
        for (auto it = std::begin(terms); it != std::end(terms); ++it) {
            if (it == std::begin(terms)) {
                n_bits_min = it->size();
                n_bits_max = it->size();
            }
            n_bits_min = std::min(n_bits_min, it->size());
            n_bits_max = std::max(n_bits_max, it->size());
        }
        if (n_bits_min != n_bits_max) {
            return ResultWithProfile{.result = std::nullopt, .profile_cmp = 0, .profile_xor = 0, .profile_xnor = 0};
        }
        n_bits = n_bits_min;
    }

    auto prime_implicants = getPrimeImplicants(n_bits, use_xor, terms);
    assert(prime_implicants.result.has_value());
    std::set<std::string> dc_set(std::begin(dc), std::end(dc));
    auto essential_implicants = getEssentialImplicants(n_bits, *prime_implicants.result, dc_set);
    auto reduced_implicants = reduceImplicants(n_bits, essential_implicants, dc_set);

    return ResultWithProfile {
        .result = reduced_implicants,
        .profile_cmp = prime_implicants.profile_cmp,
        .profile_xor = prime_implicants.profile_xor,
        .profile_xnor = prime_implicants.profile_xnor,
    };
}

ResultWithProfile simplifyWithProfile(const std::vector<int>& ones, const std::vector<int>& dc, std::optional<int> num_bits, bool use_xor = false) {
    std::vector<int> terms(ones);
    terms.insert(std::end(terms), std::begin(dc), std::end(dc));
    if (terms.empty()) {
        return ResultWithProfile{.result = std::nullopt, .profile_cmp = 0, .profile_xor = 0, .profile_xnor = 0};
    }

    int n_bits;
    if (num_bits) {
        n_bits = *num_bits;
    } else {
        auto max_term = std::max_element(std::begin(terms), std::end(terms));
        n_bits = int(ceil(log(*max_term) + 1));
    }
    
    std::vector<std::string> ones_processed;
    std::vector<std::string> dc_processed;
    for (const auto& ones_item : ones) {
        ones_processed.push_back(num2str(n_bits, ones_item));
    }
    for (const auto& dc_item : dc) {
        dc_processed.push_back(num2str(n_bits, dc_item));
    }

    return simplifyLosWithProfile(ones_processed, dc_processed, num_bits, use_xor);
}

std::optional<std::set<std::string>> simplify(const std::vector<int>& ones, const std::vector<int>& dc, std::optional<int> num_bits, bool use_xor = false) {
    return simplifyWithProfile(ones, dc, num_bits, use_xor).result;
}

std::optional<std::set<std::string>> simplifyLos(const std::vector<std::string>& ones, const std::vector<std::string>& dc, std::optional<int> num_bits, bool use_xor = false) {
    return simplifyLosWithProfile(ones, dc, num_bits, use_xor).result;
}

PYBIND11_MODULE(_qmc, m) {
    m.doc() = "quine_mccluskey_tomas789 C++ implementation"; // optional module docstring

    py::class_<ResultWithProfile>(m, "R")
        .def_readonly("result", &ResultWithProfile::result)
        .def_readonly("profile_cmp", &ResultWithProfile::profile_cmp)
        .def_readonly("profile_xor", &ResultWithProfile::profile_xor)
        .def_readonly("profile_xnor", &ResultWithProfile::profile_xnor)
        ;

    m.def("num2str", &num2str, "n_bits"_a, "i"_a);
    m.def("reduce_simple_xor_terms", &reduceSimpleXorTerms, "t1"_a, "t2"_a);
    m.def("reduce_simple_xnor_terms", &reduceSimpleXnorTerms, "t1"_a, "t2"_a);
    m.def("permutations", &permutations, "value"_a, "exclude"_a);
    m.def("get_term_rank", &get_term_rank, "term"_a, "term_range"_a);
    m.def("get_essential_implicants", &getEssentialImplicants, "n_bits"_a, "terms"_a, "dc"_a);
    m.def("get_terms", &getTerms, "implicant"_a);
    m.def("complexity", &complexity, "implicant"_a);
    m.def("combine_implicants", &combineImplicants, "a"_a, "b"_a, "dc"_a);
    m.def("reduce_implicants", &reduceImplicants, "n_bits"_a, "implicants"_a, "dc"_a);
    m.def("get_prime_implicants", &getPrimeImplicants, "n_bits"_a, "use_xor"_a, "terms"_a);
    m.def("simplify_los_with_profile", &simplifyLosWithProfile, "ones"_a, "dc"_a, "num_bits"_a, "use_xor"_a);
    m.def("simplify_with_profile", &simplifyWithProfile, "ones"_a, "dc"_a, "num_bits"_a, "use_xor"_a);
    m.def("simplify_los", &simplifyLos, "ones"_a, "dc"_a, "num_bits"_a, "use_xor"_a);
    m.def("simplify", &simplify, "ones"_a, "dc"_a, "num_bits"_a, "use_xor"_a);
}
