import subprocess
from typing import Dict


def flatten_contract_data(contract_data: Dict) -> Dict:
    if "source_analysis" in contract_data:
        source = contract_data["source_analysis"]
        flat = {
            "address": contract_data.get("address"),
            "contracts": source.get("contracts", []),
            "imports": source.get("imports", []),
            "modifiers": source.get("modifiers", []),
            "functions": source.get("functions", []),
            "state_variables": source.get("state_variables", []),
        }
        return flat
    return contract_data


def detect_contract_type(contract_data: Dict) -> str:
    names = [c["name"].lower() for c in contract_data.get("contracts", [])]
    funcs = [func["name"].lower() for func in contract_data.get("functions", [])]

    if any("transfer" in func for func in funcs) or any("erc20" in n for n in names):
        return "ERC20-like (token contract)"
    elif any("delegate" in func or "upgrade" in func for func in funcs):
        return "proxy or upgradeable contract"
    elif any("vault" in n for n in names):
        return "vault-like contract"
    else:
        return "generic smart contract"


def preprocess_access_info(contract_data: Dict) -> Dict:
    for func in contract_data.get("functions", []):
        modifiers = [modifier.lower() for modifier in func.get("modifiers", [])]
        vis = func.get("visibility", "default").lower()

        if any(modifier in modifiers for modifier in ["ifadmin", "onlyowner", "owneronly"]):
            func["access"] = "restricted"
            func["access_role"] = "admin" if "ifadmin" in modifiers else "owner"
        elif vis in {"public", "external"} or func["name"].lower() in {"fallback", "receive"}:
            func["access"] = "public"
        else:
            func["access"] = "internal"
    return contract_data


def summarize_contract_data(contract_data: Dict) -> str:
    contract_type = detect_contract_type(contract_data)
    contracts = contract_data.get("contracts", [])
    modifiers = contract_data.get("modifiers", [])
    functions = contract_data.get("functions", [])

    summary = [f"Detected contract type: {contract_type}", ""]

    if contracts:
        summary.append("Contracts:")
        for c in contracts:
            inherits = ", ".join(c.get("inherits", [])) or "None"
            summary.append(f" - {c['name']} (inherits: {inherits})")

    if modifiers:
        summary.append("\nModifiers:")
        for modifier in modifiers:
            if modifier.lower() in {"ifadmin", "onlyowner"}:
                summary.append(f" - {modifier}: restricts access to admin/owner only")
            else:
                summary.append(f" - {modifier}")

    if functions:
        summary.append("\nFunctions:")
        for func in functions:
            mods = ", ".join(func.get("modifiers", [])) or "None"
            params = ", ".join([f"{p['type']} {p['name'] or ''}".strip() for p in func.get("params", [])]) or "None"
            returns = ", ".join([r["type"] for r in func.get("returns", [])]) or "None"
            summary.append(
                f" - {func['name']} ({params}) [{func['visibility']}, {func['mutability']}, access={func.get('access', '?')}, modifiers={mods}, returns={returns}]"
            )

    if "state_variables" in contract_data:
        summary.append("\nState variables:")
        for v in contract_data["state_variables"]:
            if "admin" in v["name"].lower():
                v["semantic_role"] = "admin_storage"
                summary.append(f" - {v['type']} {v['name']} {v['semantic_role']}")
            elif "implement" in v["name"].lower():
                v["semantic_role"] = "implementation_storage"
                summary.append(f" - {v['type']} {v['name']} {v['semantic_role']}")
            else:
                summary.append(f" - {v['type']} {v['name']}")

    return "\n".join(summary)


def simple_rule_based_answer(question: str, contract_data: Dict) -> str:
    q = question.lower()
    functions = contract_data.get("functions", [])

    if "admin" in q:
        admin_funcs = [func["name"] for func in functions if func.get("access") == "restricted"]
        return (
            f"Functions restricted to admin or owner: {', '.join(admin_funcs)}"
            if admin_funcs else "No admin-restricted functions found."
        )

    if "public" in q or "anyone" in q:
        public_funcs = [func["name"] for func in functions
                        if func.get("access") == "public" and func["name"].lower() not in {"constructor"}]
        return f"Functions callable by anyone: {', '.join(public_funcs)}" if public_funcs else "No public functions found."

    if "view" in q:
        view_funcs = [func["name"] for func in functions if func.get("mutability") == "view"]
        return f"Read-only (view) functions: {', '.join(view_funcs)}" if view_funcs else "No view functions found."

    if "event" in q and "transfer" in q:
        events = [e.get("name", "").lower() for e in contract_data.get("events", [])]
        if "transfer" in events:
            return "The contract emits the 'Transfer' event when tokens are transferred."
        else:
            return "This contract does not emit a 'Transfer' event."

    return None


def llm_answer(question: str, contract_data: Dict) -> str:
    contract_data = flatten_contract_data(contract_data)
    contract_data = preprocess_access_info(contract_data)
    summary = summarize_contract_data(contract_data)
    prompt = f"""
You are a professional blockchain smart contract auditor.
You have access to the parsed source code and ABI of a contract, summarized below.

Before answering, think carefully about:
- The type of contract (proxy, ERC20, etc.)
- The access level of each function (restricted, public, internal). 
Treat any function with access="public", and any fallback or receive function as callable by anyone.
- The meaning of modifiers (e.g., ifAdmin = admin-only, onlyOwner = owner-only). 
If a function includes modifiers such as 'ifAdmin' or 'onlyOwner', clearly state that only admins or owners can perform that action.
When answering questions about who can perform an action, use the 'access_role' field when available.
- The actual events declared or emitted in this contract (not assumed)
- If a variable is labeled as 'admin_storage', it means the contract stores admin information on-chain.

Question: {question}

Contract summary:
{summary}

Answer in one or two short sentences, without unnecessary explanation.
If the contract does not explicitly handle the requested behavior, say "Not enough information".
Do not speculate.
"""

    try:
        result = subprocess.run(
            ["ollama", "run", "phi3"],
            input=prompt,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return f"Ollama error: {result.stderr.strip()}"
        return result.stdout.strip()

    except FileNotFoundError:
        return "Ollama is not installed"
    except Exception as e:
        return f"Error running local model: {e}"


def answer_question(question: str, contract_data: Dict) -> str:
    contract_data = flatten_contract_data(contract_data)
    contract_data = preprocess_access_info(contract_data)
    rule_based = simple_rule_based_answer(question, contract_data)
    if rule_based:
        return rule_based
    return llm_answer(question, contract_data)
