from typing import Dict
import json


def print_summary(parsed: Dict):
    print(json.dumps(parsed, indent=2))