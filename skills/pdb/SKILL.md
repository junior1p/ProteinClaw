---
name: pdb
description: >
  Fetch and analyze protein structures from RCSB PDB. Use this skill when:
  (1) Need to download a structure by PDB ID,
  (2) Search for similar structures,
  (3) Prepare target for binder design,
  (4) Extract specific chains or domains,
  (5) Get structure metadata.

  For sequence lookup, use uniprot.
  For binder design workflow, use binder-design.
license: MIT
category: utilities
tags: [database, structure, fetch]
source: https://github.com/adaptyvbio/protein-design-skills
---

# PDB Database Access

**Note**: Uses RCSB PDB web API directly. No Modal needed.

## Fetching Structures

```bash
# Download PDB file
curl -o 1alu.pdb "https://files.rcsb.org/download/1ALU.pdb"

# Download mmCIF
curl -o 1alu.cif "https://files.rcsb.org/download/1ALU.cif"
```

```python
import requests

def fetch_pdb(pdb_id: str, format: str = "pdb") -> str:
    url = f"https://files.rcsb.org/download/{pdb_id}.{format}"
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def fetch_fasta(pdb_id: str) -> str:
    return requests.get(f"https://www.rcsb.org/fasta/entry/{pdb_id}").text
```

## Structure Preparation

### Extract chain
```python
from Bio.PDB import PDBParser, PDBIO, Select

class ChainSelect(Select):
    def __init__(self, chain_id):
        self.chain_id = chain_id
    def accept_chain(self, chain):
        return chain.id == self.chain_id

parser = PDBParser()
structure = parser.get_structure("protein", "1abc.pdb")
io = PDBIO()
io.set_structure(structure)
io.save("chain_A.pdb", ChainSelect("A"))
```

### Find interface residues
```python
def find_interface_residues(pdb_file, chain_a, chain_b, distance=4.0):
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("complex", pdb_file)
    interface_a, interface_b = set(), set()
    for res_a in structure[0][chain_a].get_residues():
        for res_b in structure[0][chain_b].get_residues():
            for atom_a in res_a.get_atoms():
                for atom_b in res_b.get_atoms():
                    if atom_a - atom_b < distance:
                        interface_a.add(res_a.id[1])
                        interface_b.add(res_b.id[1])
    return interface_a, interface_b
```

## RCSB Search API

```python
import requests

query = {
    "query": {"type": "terminal", "service": "full_text",
              "parameters": {"value": "EGFR kinase domain"}},
    "return_type": "entry"
}
results = requests.post("https://search.rcsb.org/rcsbsearch/v2/query", json=query).json()
```

## Target Preparation Checklist

1. Download structure: `curl -o target.pdb "https://files.rcsb.org/download/XXXX.pdb"`
2. Identify target chain
3. Remove waters and ligands (if needed)
4. Trim to binding region + buffer
5. Identify potential hotspots

**Next**: Use structure with `boltzgen` or `bindcraft` for design.
