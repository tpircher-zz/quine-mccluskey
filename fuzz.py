import random
import time
from typing import List, Optional, Set, Tuple
from rich.progress import track
import boolean
import sys
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich import print

from quine_mccluskey_tomas789 import simplify

algebra = boolean.BooleanAlgebra()
TRUE, FALSE, NOT, AND, OR, symbol = algebra.definition()


def qmc_to_formula(res: Optional[Set[str]]) -> boolean.Expression:
    if res is None:
        return FALSE
    clauses = []
    for clause in res:
        conjunction = []
        for i, bit in enumerate(clause[::-1]):
            variable = symbol(f"x{i}")
            if bit == "-":
                continue
            if bit == "0":
                conjunction.append(NOT(variable))
            else:
                conjunction.append(variable)
        if conjunction == []:
            continue
        if len(conjunction) == 1:
            clauses.append(conjunction[0])
        else:
            clauses.append(AND(*conjunction))
    if clauses == []:
        return TRUE
    if len(clauses) == 1:
        return clauses[0]
    else:
        return OR(*clauses)


def make_random_fromula(n_bits: int, max_depth: int) -> boolean.Expression:
    weight_map = {
        TRUE: 1,
        FALSE: 1,
        NOT: 2 if max_depth != 0 else 0,
        AND: 3 if max_depth != 0 else 0,
        OR: 3 if max_depth != 0 else 0,
        symbol: 2,
    }
    weight_sum = sum(weight_map.values())
    running_sum = 0
    random_number = random.randint(a=0, b=weight_sum - 1)
    for op, weight in weight_map.items():
        if not (running_sum <= random_number < running_sum + weight):
            running_sum += weight
            continue
        if op == symbol:
            variable_index = random.randint(a=0, b=n_bits - 1)
            variable_name = f"x{variable_index}"
            return symbol(variable_name)
        if op in (TRUE, FALSE):
            return op
        n_operands = 1 if op == NOT else random.randint(a=2, b=5)
        operands = [make_random_fromula(n_bits=n_bits, max_depth=max_depth - 1) for _ in range(n_operands)]
        return op(*operands)
    
    raise Exception("Impossible!")


def formulas_to_ones_and_dontcare(n_bits: int, ones_formula, dontcare_formula):
    ones, dontcare = [], []
    for k in range(2**n_bits):
        assignments = {}
        for i in range(n_bits):
            variable_name = f"x{i}"
            assignments[variable_name] = k & (1 << i) != 0
        value_ones = ones_formula(**assignments)
        value_dontcare = dontcare_formula(**assignments)
        if value_dontcare:
            dontcare.append(k)
            continue
        if value_ones:
            ones.append(k)
    return ones, dontcare


def check_qmc(n_bits: int, ones_formula, dontcare_formula):
    ones, dontcare = formulas_to_ones_and_dontcare(
        n_bits=n_bits, ones_formula=ones_formula, dontcare_formula=dontcare_formula
    )
    res = simplify(ones=ones, dc=dontcare, num_bits=n_bits)
    qmc_formula = qmc_to_formula(res=res)

    problems = []

    for k in range(2**n_bits):
        assignments = {}
        for i in range(n_bits):
            variable_name = f"x{i}"
            assignments[variable_name] = k & (1 << i) != 0
        value_ones = ones_formula(**assignments)
        value_dontcare = dontcare_formula(**assignments)
        value_qmc = qmc_formula(**assignments)
        if value_dontcare:
            continue
        if value_ones != value_qmc:
            problems.append({
                "k": k,
                "value_ones": value_ones,
                "value_qmc": value_qmc,
            })

    if problems == []:
        return
    
    ones_formula_simplified = ones_formula.simplify().simplify()
    dontcare_formula_simplified = dontcare_formula.simplify().simplify()
    qmc_formula_simplified = qmc_formula.simplify().simplify()

    print(f"[red]Found {len(problems)} with a formula.[/red]")
    print(f"Ones: {ones_formula}\n  Ones (simplified): [bold]{ones_formula_simplified}[/bold]")
    print(f"Dont' care: {dontcare_formula}\n  Dont' care (simplified): [bold]{dontcare_formula_simplified}[/bold]")
    print(f"QMC input:\n  ones: {ones}\n  dc: {dontcare}")
    print(f"QMC formula: {qmc_formula}\n  QMC formula (simplified): [bold]{qmc_formula_simplified}[/bold]")
    print(f"QMC result: {res}")
    print(f"Reproduce: python fuzz.py {n_bits} '{ones_formula}' '{dontcare_formula}'")
    print()


def check(n_bits, ones_str, dontcare_str):
    ones_formula = make_random_fromula(n_bits=n_bits, max_depth=2)
    dontcare_formula = make_random_fromula(n_bits=n_bits, max_depth=2)


def main():
    # qmc = QuineMcCluskey()
    # # print(qmc.simplify_los(ones=[], dc=['00', '01', '10', '11']))
    # # print(qmc.simplify_los(ones=['00', '01', '10', '11'], dc=[]))
    # print(qmc.simplify_los(ones=['00', '01', '10'], dc=['11'], num_bits=2))
    # print(qmc.simplify_los(ones=[], dc=['11'], num_bits=2))

    # print(qmc.simplify_los(ones=['00', '01', '10'], dc=[], num_bits=2))
    # print("FALSE", qmc.simplify_los(ones=[], dc=[], num_bits=2))
    # print("TRUE", qmc.simplify_los(ones=['00', '01', '10', '11'], dc=[], num_bits=2))
    # return

    if len(sys.argv) == 4:
        n_bits = int(sys.argv[1])
        ones_formula = algebra.parse(sys.argv[2])
        dontcare_formula = algebra.parse(sys.argv[3])
        has_error = check_qmc(n_bits=n_bits, ones_formula=ones_formula, dontcare_formula=dontcare_formula)
        if has_error:
            sys.exit(1)
        return
    
    
    
    n_bits = 5
    infinity = 9999999999999999999999
    error_counter = 0 
    time_begin = time.time()
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        SpinnerColumn(),
        TimeElapsedColumn()
    ) as progress:
        task = progress.add_task("[green]Testing formulas ...", total=infinity)

        for i in range(infinity):
            ones_formula = make_random_fromula(n_bits=n_bits, max_depth=2)
            dontcare_formula = make_random_fromula(n_bits=n_bits, max_depth=2)
            dontcare_formula = FALSE
            has_error = check_qmc(n_bits=n_bits, ones_formula=ones_formula, dontcare_formula=dontcare_formula)
            if has_error:
                error_counter += 1
            progress.update(task, advance=1)

            if i % 100 == 0 and (time.time() - time_begin) > 10:
                progress.print(f"Checked {i} formulas and found {error_counter} errors.")
                time_begin = time.time()


if __name__ == "__main__":
    main()
