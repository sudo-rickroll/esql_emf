from __future__ import annotations
from models import PhiOperator

def parse_phi(path: str) -> PhiOperator | None:
    phi = PhiOperator()

    try:
        with open(path, 'r') as phiInput:
            args: list = []
            argVals: list = []
            for row in phiInput:
                row = row.replace(" ", "").strip()
                args = row.split(":")
                if args[0] == "S":
                    phi.S = args[1].split(",")
                elif args[0] == "n":
                    phi.N = int(args[1])
                elif args[0] == "V":
                    phi.V = args[1].split(",")
                elif args[0] == "F-VECT":
                    phi.F = args[1].split(",")
                elif args[0] == "PRED-LIST":
                    phi.P = args[1].split(";")
                elif args[0] == "HAVING":
                    phi.H = None if args[1] == "NONE" else args[1].split(";")
        return phi
    except Exception as e:
        print(f"A exception occured when parsing the phi operators from input text: {e}")
        return None

# For test   
def main():
    phi = parse_phi("./inputs/phi_1.txt")
    print(phi)

if __name__ == "__main__":
    main()


