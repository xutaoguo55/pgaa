#!/bin/bash
# Download Replogle 2022 (GSE146194) for PGAA validation
# ~50GB, requires GEO download tool
echo "Replogle 2022: GSE146194"
echo "Download: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE146194"
echo "Or use: fasterq-dump SRR15005824 SRR15005825 ... (multiple runs)"
echo "After download, run: python scripts/benchmark_replogle2022.py"
