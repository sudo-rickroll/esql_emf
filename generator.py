"""
Query Processing Engine for EMF Queries
This module generates Python code to execute Extended Multi-Feature queries
based on the Phi operator specification.

"""
import os
import subprocess
import sys
from phi_parser import parse_phi
from models import PhiOperator

def get_aggregate_type(agg_func_name: str) -> str:
    """
    Determine the Python type for an aggregate function result.
    
    Args:
        agg_func_name: Name of aggregate function (e.g., 'sum_1_quant')
        
    Returns:
        Python type as string
    """
    if agg_func_name.split('_')[0] in ['sum', 'count', 'max', 'min']:
        return "0"
    elif agg_func_name.split('_')[0] == 'avg':
        return "0.0"
    return "0"

def generate_mf_struct(phi: PhiOperator) -> str:
    """
    Generate the MFStruct class definition with all necessary fields.
    
    Args:
        phi: PhiOperator object containing query specification
        
    Returns:
        String containing the class definition
    """
    struct_code = "    class MFStruct:\n"
    struct_code += "        def __init__(self):\n"
    
    # Grouping attributes
    for attr in phi.V:
        struct_code += f"            self.{attr} = ''\n"
    
    # Aggregate function fields
    for func in phi.F:
        func_type = func.split('_')[0]  # sum, avg, count, etc. (first part)
        
        if func_type == 'sum':
            struct_code += f"            self.{func} = {get_aggregate_type(func)}\n"
        elif func_type == 'count':
            struct_code += f"            self.{func} = {get_aggregate_type(func)}\n"
        elif func_type == 'avg':
            struct_code += f"            self.{func}_sum = {get_aggregate_type('sum_' + func)}\n"
            struct_code += f"            self.{func}_count = {get_aggregate_type('count_' + func)}\n"
            struct_code += f"            self.{func} = {get_aggregate_type(func)}\n"
        elif func_type == 'max':
            struct_code += f"            self.{func} = float('-inf')\n"
        elif func_type == 'min':
            struct_code += f"            self.{func} = float('inf')\n"
    
    struct_code += "\n"
    return struct_code

def generate_predicate_code(iter:str, predicate: str) -> str:
    """
    Convert predicate string to Python comparison code.
    
    Args:
        iter: Variable that iterates through main table's data 
        predicate: Predicate string (e.g., "1.state='NY' and 1.cust=cust")
        grouping_vars: List of grouping variable names
        
    Returns:
        Python code for the predicate
    
    """
    import re
    pred_code = predicate.strip()
    
    pattern = r'(\d+)\.(\w+)'
    pred_code = re.sub(pattern, rf"{iter}.get('\2')", pred_code)
    
    # Replace single = with == for comparison (but not if already == or >= or <=)
    pred_code = re.sub(r'(?<![<>=!])=(?!=)', '==', pred_code)
    
    return pred_code

def generate_aggregate_scans(mainTableVar:str, hTableVar:str, phi: PhiOperator) -> str:
    """
    Generate the scanning loops for computing aggregate functions.
    
    Args:
        mainTableVar: Variable holding main table's data
        hTableVar: Variable holding H-Table's data
        phi: PhiOperator object containing query specification
        
    Returns:
        String containing the scan loop code
    """
    scan_code = ""
    
    # Group aggregate functions by grouping variable
    # Aggregate format: <function>_<gv_num>_<attribute>
    # Example: count_1_quant, sum_2_quant, avg_3_quant
    agg_by_gv = {}
    for func in phi.F:
        parts = func.split('_')
        if len(parts) >= 2:
            gv_num = int(parts[1])  # Get grouping variable number (second part)
            if gv_num not in agg_by_gv:
                agg_by_gv[gv_num] = []
            agg_by_gv[gv_num].append(func)
    
    # Generate scan for each grouping variable
    for gv_num in sorted(agg_by_gv.keys()):
        predicate = phi.P[gv_num - 1] if gv_num <= len(phi.P) else ""
        pred_code = generate_predicate_code("row", predicate)
        
        scan_code += "    # Scan for grouping variable {}\n".format(gv_num)
        scan_code += f"    {mainTableVar}.scroll(0, mode='absolute')\n\n"
        scan_code += f"    for row in {mainTableVar}:\n"
        scan_code += f"        for pos in range(len({hTableVar})):\n"
        
        # Add local variables for current entry
        for attr in phi.V:
            scan_code += f"            {attr} = {hTableVar}[pos].{attr}\n"
        
        # Add condition check
        scan_code += f"            if {pred_code}:\n"
        
        # Update aggregates for this grouping variable
        for func in agg_by_gv[gv_num]:
            func_parts = func.split('_')
            func_type = func_parts[0]  # sum, avg, count, etc. (first part)
            attr = func_parts[2]  # attribute name (third part)
            
            if func_type == 'sum':
                scan_code += f"                {hTableVar}[pos].{func} += row.get('{attr}')\n"
            elif func_type == 'count':
                scan_code += f"                {hTableVar}[pos].{func} += 1\n"
            elif func_type == 'max':
                scan_code += f"                {hTableVar}[pos].{func} = max({hTableVar}[pos].{func}, row.get('{attr}'))\n"
            elif func_type == 'min':
                scan_code += f"                {hTableVar}[pos].{func} = min({hTableVar}[pos].{func}, row.get('{attr}'))\n"
            elif func_type == 'avg':
                scan_code += f"                {hTableVar}[pos].{func}_sum += row.get('{attr}')\n"
                scan_code += f"                {hTableVar}[pos].{func}_count += 1\n"
                scan_code += f"                if {hTableVar}[pos].{func}_count != 0:\n"
                scan_code += f"                    {hTableVar}[pos].{func} = {hTableVar}[pos].{func}_sum / {hTableVar}[pos].{func}_count\n"
        
        scan_code += "\n"
    
    return scan_code

def generate_having_clause(hTableVar:str, phi: PhiOperator) -> str:
    """
    Generate code for HAVING clause filtering.
    
    Args:
        hTableVar: Name of the H-Table variable
        phi: PhiOperator object containing query specification
        
    Returns:
        String containing HAVING clause code
    """
    if phi.H is None or phi.H.upper() == "NONE":
        return ""
    
    having_code = "    # Apply HAVING clause\n"
    having_condition = phi.H.strip()
    
    # Replace aggregate function names with obj.attribute
    for func in phi.F:
        having_condition = having_condition.replace(func, f"obj.{func}")
    
    having_code += f"    {hTableVar} = [obj for obj in {hTableVar} if {having_condition}]\n\n"
    
    return having_code

def generate_output_code(hTableVar:str, phi: PhiOperator, output_filename: str) -> str:
    """
    Generate code to output results using PrettyTable.
    
    Args:
        hTableVar: H-Table data table variable
        phi: PhiOperator object containing query specification
        
    Returns:
        String containing output code
    """
    code =  "    if not os.path.exists('outputs'):\n"
    code += "        os.makedirs('outputs')\n\n"
    
    
    code += "    headers = " + str(phi.S) + "\n"
    code += "    table_rows = []\n"
    # Loop through data and write rows
    code += f"    for obj in {hTableVar}:\n"
    code += "        row_vals = []\n"
    code += f"        for field in {phi.S}:\n"
    code += "            try:\n"
    code += "                val = getattr(obj, field)\n"
    code += "            except AttributeError:\n"
    # Handle expressions like 'sum_1 / sum_2' using eval
    code += "                try:\n"
    code += "                    val = eval(field, {}, obj.__dict__)\n"
    code += "                except Exception:\n"
    code += "                    val = ''\n"
    code += "            row_vals.append(str(val))\n"
    code += "        table_rows.append(row_vals)\n\n"

    code += f"    output_path = os.path.join('outputs', '{output_filename}')\n"
    code += "    with open(output_path, 'w') as f:\n"
    code += "        f.write(tabulate(table_rows, headers=headers, tablefmt='psql'))\n\n"
    
    code += f"    return len({hTableVar})\n"
    
    return code

def generate_query_code(phi: PhiOperator, output_filename: str) -> str:
    """
    Generate complete Python code for the query processing engine.
    
    Args:
        phi: PhiOperator object containing query specification
        
    Returns:
        Complete Python code as string
    """
    code = """import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from tabulate import tabulate

# DO NOT EDIT THIS FILE, IT IS GENERATED BY generator.py

def query():
    \"\"\"
    Execute the EMF query and return tabulated results in a file.
    \"\"\"
    load_dotenv()

    user = os.getenv('USER')
    password = os.getenv('PASSWORD')
    dbname = os.getenv('DBNAME')
    host = os.getenv('HOST')
    port = os.getenv('PORT')

    conn = psycopg2.connect("dbname="+dbname+" user="+user+" password="+password,
                            cursor_factory=psycopg2.extras.DictCursor, host=host, port=port)
    cur = conn.cursor()
    cur.execute("SELECT * FROM sales")
    
"""
    
    # Add MFStruct definition
    code += generate_mf_struct(phi)

    # Initialize data structure
    code += """    # For entries in the H-Table    
    data = []
"""
    code += """    # To ensure distinct records based on grouping-attributes   
    group_by_map = {}\n
"""
    
    # First scan: populate data with distinct grouping attribute values
    code += "    # First scan: Create entries for distinct grouping attribute values\n"
    code += "    for row in cur:\n"
    
    # Create key from grouping attributes
    key_parts = [f"row.get('{attr}')" for attr in phi.V]
    code += f"        key = ({', '.join(key_parts)})\n"
    code += "        \n"
    code += "        if key not in group_by_map:\n"
    code += "            entry = MFStruct()\n"
    
    # Set grouping attribute values
    for attr in phi.V:
        code += f"            entry.{attr} = row.get('{attr}')\n"
    #code += f"            print(\"attr: \", entry.{attr})\n"
    
    code += "            data.append(entry)\n"
    code += "            group_by_map[key] = len(data) - 1\n\n"

    # Generate aggregate computation scans
    code += generate_aggregate_scans("cur", "data", phi)
    
    # Apply HAVING clause
    code += generate_having_clause("data", phi)

    # Generate output
    code += generate_output_code("data", phi, output_filename)
    
    # Main execution
    code += """
if __name__ == "__main__":
    print(query())
"""
    
    return code

def main():
    """
    Main function to generate and optionally execute the query processing engine.
    """
    if len(sys.argv) < 2:
        print("Usage: python generator.py <input_file> [--run]")
        print("  <input_file>: Path to Phi operator specification file")
        print("  --run: Optional flag to execute generated code immediately")
        sys.exit(1)
    
    input_file = sys.argv[1]
    should_run = len(sys.argv) > 2 and sys.argv[2] == "--run"
    
    # Parse Phi operator from input file
    print(f"Parsing Phi operator from {input_file}...")
    phi = parse_phi(input_file)
    
    if phi is None:
        print("Error: Failed to parse Phi operator")
        sys.exit(1)
    
    print("Successfully parsed Phi operator:")
    print(f"  Grouping attributes: {phi.V}")
    print(f"  Number of grouping variables: {phi.N}")
    print(f"  Aggregate functions: {phi.F}")
    print(f"  Select attributes: {phi.S}")
    
    # Generate query code
    print("\nGenerating query processing code...")
    basename = os.path.basename(input_file)
    output_filename = basename
    code = generate_query_code(phi, output_filename)
    
    # Write to file
    output_file = "_generated.py"
    with open(output_file, "w") as f:
        f.write(code)
    
    print(f"Generated code written to {output_file}")
    
    # Execute if requested
    if should_run:
        print("\nExecuting generated code...")
        subprocess.run([sys.executable, output_file])

if __name__ == "__main__":
    main()
