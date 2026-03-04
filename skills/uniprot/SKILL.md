---
name: uniprot
description: >
  Access UniProt for protein sequence and annotation retrieval.
  Use this skill when: (1) Looking up protein sequences by accession,
  (2) Finding functional annotations,
  (3) Getting domain boundaries,
  (4) Finding homologs and variants,
  (5) Cross-referencing to PDB structures.

  For structure retrieval, use pdb.
  For sequence design, use proteinmpnn.
license: MIT
category: utilities
tags: [database, sequence, annotation]
source: https://github.com/adaptyvbio/protein-design-skills
---

# UniProt Database Access

**Note**: Uses UniProt REST API directly. No Modal needed.

## Fetching Sequences

```bash
# FASTA format
curl "https://rest.uniprot.org/uniprotkb/P00533.fasta"

# JSON format with annotations
curl "https://rest.uniprot.org/uniprotkb/P00533.json"
```

```python
import requests

def get_uniprot_sequence(accession):
    url = f"https://rest.uniprot.org/uniprotkb/{accession}.fasta"
    response = requests.get(url)
    if response.ok:
        lines = response.text.strip().split('\n')
        return lines[0], ''.join(lines[1:])
    return None, None

def get_uniprot_entry(accession):
    url = f"https://rest.uniprot.org/uniprotkb/{accession}.json"
    response = requests.get(url)
    return response.json() if response.ok else None
```

## Getting Annotations

### Domain boundaries
```python
def get_domains(accession):
    entry = get_uniprot_entry(accession)
    return [
        {'name': f.get('description', ''),
         'start': f['location']['start']['value'],
         'end': f['location']['end']['value']}
        for f in entry.get('features', [])
        if f['type'] == 'Domain'
    ]
```

### PDB cross-references
```python
def get_pdb_references(accession):
    entry = get_uniprot_entry(accession)
    return [
        {'pdb_id': xref['id']}
        for xref in entry.get('uniProtKBCrossReferences', [])
        if xref['database'] == 'PDB'
    ]
```

## Searching UniProt

```python
def search_uniprot(query, organism=None, limit=10):
    params = {"query": query, "format": "json", "size": limit}
    if organism:
        params["query"] += f" AND organism_id:{organism}"
    response = requests.get("https://rest.uniprot.org/uniprotkb/search", params=params)
    return response.json()['results']

# Search for human EGFR
results = search_uniprot("EGFR", organism=9606)
```

## API Reference

| Endpoint | Description |
|----------|-------------|
| `/uniprotkb/{id}.fasta` | FASTA sequence |
| `/uniprotkb/{id}.json` | Full entry JSON |
| `/uniprotkb/search` | Search entries |

**Next**: Use sequence with `esm` for embeddings or `pdb` for structure.
