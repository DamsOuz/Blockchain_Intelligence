import os
import re
from typing import Dict, List


DATA_DIR = "data"


def load_source(address: str) -> str:
    path = os.path.join(DATA_DIR, f"{address}_source.sol")

    if not os.path.exists(path):
        raise FileNotFoundError(f"Source file not found for address {address}")

    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def extract_contracts(source: str) -> List[Dict]:
    contracts = []

    contract_pattern = re.compile(r"contract\s+(\w+)(?:\s+is\s+([^{]+))?\s*{", re.MULTILINE)
    for match in contract_pattern.finditer(source):
        name = match.group(1)
        inherits = [x.strip() for x in match.group(2).split(",")] if match.group(2) else []
        contracts.append({"name": name, "inherits": inherits})

    return contracts


def extract_imports(source: str) -> List[str]:
    import_pattern = re.compile(r'import\s+["\']([^"\']+)["\'];')
    return import_pattern.findall(source)


def extract_modifiers(source: str) -> List[str]:
    modifier_pattern = re.compile(r"modifier\s+(\w+)\s*\(")
    return list(set(modifier_pattern.findall(source)))


def extract_functions(source: str) -> List[Dict]:
    func_pattern = re.compile(
        r"(?:function|constructor)\s*(\w*)\s*"
        r"\(([\s\S]*?)\)\s*"
        r"(public|external|internal|private)?\s*"
        r"(view|pure|payable)?\s*"
        r"((?:(?!returns)\w+\s*)*)\s*"
        r"(?:returns\s*\(([^)]*)\))?",
        re.MULTILINE | re.DOTALL,
    )

    functions = []

    for match in func_pattern.finditer(source):
        name = match.group(1).strip() or None
        raw_params = match.group(2).strip()
        visibility = match.group(3) or "public"
        mutability = match.group(4) or "nonpayable"
        modifier_block = match.group(5) or ""
        raw_returns = match.group(6).strip() if match.group(6) else None

        modifiers = [m for m in modifier_block.split() if
                     m not in {"public", "external", "internal", "private", "view", "pure", "payable"}]

        if name is None:
            if "constructor" in match.group(0):
                name = "constructor"
            else:
                name = "fallback"

        params = []
        if raw_params:
            for p in [x.strip() for x in raw_params.split(",") if x.strip()]:
                parts = p.split()
                if len(parts) == 1:
                    # When there is only the type
                    param_type, param_name = parts[0], None
                else:
                    param_type = " ".join(parts[:-1])
                    param_name = parts[-1]
                params.append({"type": param_type, "name": param_name})

        returns = []
        if raw_returns:
            for r in [x.strip() for x in raw_returns.split(",") if x.strip()]:
                parts = r.split()
                if len(parts) == 1:
                    return_type, return_name = parts[0], None
                else:
                    return_type = " ".join(parts[:-1])
                    return_name = parts[-1]
                returns.append({"type": return_type, "name": return_name})

        functions.append({
            "name": name,
            "params": params,
            "visibility": visibility,
            "mutability": mutability,
            "returns": returns,
            "modifiers": modifiers
        })

    return functions


def extract_state_variables(source: str):
    var_pattern = re.compile(
        r"(?:(?:public|private|internal|external)\s+)?(?:constant\s+)?(\w+)\s+(\w+)\s*(?:=\s*[^;]+)?;",
        re.MULTILINE
    )
    variables = []
    for match in var_pattern.finditer(source):
        var_type = match.group(1)
        var_name = match.group(2)
        variables.append({"name": var_name, "type": var_type})
    return variables


def parse_solidity_source(address: str) -> Dict:
    source = load_source(address)

    contracts = extract_contracts(source)
    imports = extract_imports(source)
    modifiers = extract_modifiers(source)
    functions = extract_functions(source)

    return {
        "contracts": contracts,
        "imports": imports,
        "modifiers": modifiers,
        "state_variables": extract_state_variables(source),
        "functions": functions,
    }
