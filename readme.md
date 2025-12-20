# Extended Multi-Feature SQL Queries

This repo extends[^1] the SQL functionality according to the research paper on [Evaluation of Ad Hoc OLAP : In-Place Computation](https://ieeexplore.ieee.org/document/787619).

You can supply the Phi parameters and run the code as
`py generator.py <path to the phi parameter file>` to generate the execution engine.
Using the `--run`flag runs this engine and generates the data.
This will generate the outputs in the "/outputs" folder with the number postfix that you use as in the example phi files.

To run the SQL scripts for testing, you can run
`py sql.py <path to the sql file>`
This will generate the output in the "/outputs" folder with the number prefix as in the example sql files.

[^1]: Credits to Ari for providing the [baseline SQL parsers](https://github.com/ceiphr/cs562-project-demo)