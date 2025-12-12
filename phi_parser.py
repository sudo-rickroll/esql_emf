from __future__ import annotations

def parse_phi(path: str) -> dict[str, list[str] | int | str] | None:
    phi: dict[str, list[str] | int | str] = {}
    try:
        with open(path, 'r') as phiInput:
            args: list = []
            argVals: list = []
            for row in phiInput:
                row = row.replace(" ", "").strip()
                args = row.split(":")
                if "," in args[1]:
                    argVals = args[1].split(",")
                elif ";" in args[1]:
                    argVals = args[1].split(";")
                else:
                    argVals = int(args[1]) if args[1].isdigit() else args[1]
                phi[args[0]] = argVals
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


