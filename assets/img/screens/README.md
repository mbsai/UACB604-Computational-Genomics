# Website screenshots

Annotated screenshots of real database pages, used by the "On the real websites" slides
(Lectures 1.5, 2.4 and 2.5) through `CG.siteTour` in `assets/js/course.js`.
Taken 26 November 2026.

| File | Page | Used in |
|---|---|---|
| `ensembl.jpg` | Ensembl gene page, TP53 (ENSG00000141510) | 1.5 |
| `uniprot.jpg` | UniProt entry P04637 | 1.5 |
| `uniprot_seq.jpg` | UniProt P04637, Sequence section (length, mass) | 1.5 (slide 10) |
| `protparam.jpg` | Expasy ProtParam result for P04637 | 1.5 (slide 10) |
| `kegg_gene.jpg` | KEGG gene entry hsa:7157 (pathway list) | 1.5 (slide 10) |
| `ena_j02482.jpg` | ENA sequence page, φX174 J02482 | 2.4 |
| `bioproject.jpg` | NCBI BioProject PRJNA229998 | 2.5 |
| `runselector.jpg` | NCBI SRA Run Selector, PRJNA229998 | 2.5 |
| `ena_project.jpg` | ENA project page, PRJNA229998 (read files) | 2.5 |

**Optional, taken by hand:** `ncbi_gene.jpg` (NCBI Gene 7157), `ucsc.jpg` (UCSC Genome Browser at TP53, hg38) and `nuccore.jpg` (NCBI Nucleotide NC_001422.1).
These sites ask automated browsers to prove they are human, so they can't be captured by the script. Save a screenshot under one of these names and its tab appears in the slides automatically (no callouts are drawn on hand-taken images).

**Re-taking them** (sites change their layout every year or two):

```bash
python3 assets/img/screens/capture.py    # full-page captures into raw/ (not committed)
python3 assets/img/screens/annotate.py   # crop + numbered callouts -> *.jpg
```

Then check that the boxes in `annotate.py` still sit on the right items.

**Sources and reuse.** NCBI pages are US government works (public domain). ENA and Ensembl (EMBL-EBI) and UniProt content is shared under open terms (UniProt: CC BY 4.0) with attribution; each slide caption names and links the site. Expasy content is shared with attribution. The KEGG gene entry is a screenshot of a text page with attribution; KEGG pathway **map images** are not included because KEGG restricts their reuse. Instead `../kegg_p53_graph.svg` is our own drawing of the p53 pathway made from KEGG's relation data (`../kegg_p53_graph.py`).
