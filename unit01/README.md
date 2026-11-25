# Unit 1 · Genomes, omics and where the data lives

**Syllabus:** introduction to computational genomics, transcriptomics, proteomics, epigenomics, metagenomics and applications; organisation of genetic information in prokaryotic and eukaryotic cells; genome maps and structure; public databases (NCBI GenBank, Expasy, EBI, Ensembl, UCSC, KEGG).

Five lectures of 45–50 minutes. Each opens with a maths question, has at least one interactive slide or game, and ends with a short quiz.

| Lecture | Title | Maths hook | Interactive / game | Notebook |
|---|---|---|---|---|
| 1.1 | What is a genome, to a mathematician? | Strings over {A,C,G,T}, information (bits), expected k-mer counts, geometric ORF lengths | Genome-size guessing game, sequence calculator, k-mer uniqueness slider, random-ORF simulator, exit quiz | Python: GC%, CpG o/e and ORFs in *E. coli* |
| 1.2 | The omics family as data types | Genotype matrices, count normalisation, Poisson vs negative binomial, peptide m/z, binomial proportions, compositional data | Matching game, sequencing-depth slider, mean–variance simulator, "which peptide made this peak?", methylation interval, compositional pitfall, exit quiz | R: a real colorectal-cancer count matrix (library size, CPM/TPM, mean–variance, PCA) |
| 1.3 | How genetic information is organised | Gene density, null models for strand bias (z-score), mod-3 reading frames, counting isoforms, log-normal lengths (mean vs median) | Coding-fraction vote, genome-builder game, exon-skipping explorer, log-normal slider, prokaryote-or-eukaryote cards, exit quiz | Python + Biopython: *E. coli* and yeast GenBank annotation (coding fraction, leading strand, operon gaps) |
| 1.4 | Genome maps | Recombination fraction, Poisson crossovers → Haldane map function (derived in class), additivity, Kosambi and interference | 50 Mb vote, crossover simulator, map-function slider, three-point-cross "gene detective" game, Marey map, exit quiz | R: simulate meioses, estimate r, fit map functions, recover marker order, add interference |
| 1.5 | Public databases | Identifiers and regular expressions, assemblies and lift-over, 0- vs 1-based intervals, relations vs functions (joins) | "One gene, seven names" matching game, accession cards, coordinate ruler, treasure hunt across NCBI/Ensembl/UniProt, exit quiz | Python: query NCBI, Ensembl, UniProt and KEGG APIs; build an ID-mapping table |

**Reading**
- Brown, *Genomes 5*: ch. 1 (genomes, transcriptomes, proteomes), ch. 3 (mapping genomes), ch. 7–8 (eukaryotic and prokaryotic genomes)
- Pevsner, *Bioinformatics and Functional Genomics*: ch. 2 (access to sequence data), ch. 15–19 (genomes across the tree of life)
- Buffalo, *Bioinformatics Data Skills*: ch. 1 (how to learn bioinformatics), ch. 9 (working with range data)
