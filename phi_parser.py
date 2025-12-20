from __future__ import annotations
from models import PhiOperator

def parse_phi(path: str) -> PhiOperator | None:
    """
    Generate code to parse phi.txt file
    
    Args:
        path: path to the phi.txt file
        
    Returns:
        String Phi Data structure
    """
    phi = PhiOperator()

    try:
        with open(path, 'r') as phiInput:
            args: list = []
            argVals: list = []
            for row in phiInput:
                row = row.strip()
                if not row:
                    continue
                args = row.split(":", 1)
                if len(args) < 2: continue
                
                key = args[0].strip()
                val = args[1].strip()

                if key == "S":
                    phi.S = [x.strip() for x in val.split(",")]
                elif key == "n":
                    phi.N = int(val)
                elif key == "V":
                    phi.V = [x.strip() for x in val.split(",")]
                elif key == "F-VECT":
                    phi.F = [x.strip() for x in val.split(",")]
                elif key == "PRED-LIST":
                    # Split by semicolon for different scans
                    phi.P = [x.strip() for x in val.split(";")]
                elif key == "HAVING":
                    phi.H = None if val.lower() == "none" else val
        return phi
    except Exception as e:
        print(f"A exception occured when parsing the phi operators from input text: {e}")
        return None


