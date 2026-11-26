# Unit 2 · Sequencing technologies, file formats and data retrieval

**Syllabus:** first- and second-generation sequencing (Sanger, Illumina); long-read and linked-read sequencing (Nanopore, PacBio, TELL-Seq); sequence formats (FASTA, GenBank, EMBL, XML, FASTQ, fast5); NCBI SRA, BioProject, accessions; data retrieval using wget, FTP, FileZilla and scripts.

Five lectures of 45–50 minutes.

| Lecture | Title | Maths hook | Interactive / game | Notebook |
|---|---|---|---|---|
| 2.1 | Sanger sequencing | Geometric fragment lengths, Phred scores, optimum ddNTP ratio by calculus | Termination simulator, "read the trace" game, Phred slider, exit quiz | Python: simulate chain termination and electropherograms on φX174 |
| 2.2 | Illumina short reads | Coverage, phasing decay and half-life, expected errors, paired-end overlap | "Call the base" game, phasing slider, live FASTQ decoder, paired-end and throughput calculators, exit quiz | Python: stream 20,000 real read pairs (SRR1039508); quality, N, expected errors |
| 2.3 | Long and linked reads | Binomial majority vote (HiFi), N50, birthday problem (barcodes) | HiFi consensus slider, nanopore squiggle simulator, barcode-collision slider, "pick the technology" game, exit quiz | Python: real Nanopore reads (DRR242229), N50, consensus and collision simulations |
| 2.4 | Sequence file formats | ASCII / Phred+33 encoding, file-size arithmetic | Real φX174 records in every format, "decode the quality" and "name that format" games, FASTQ size calculator, exit quiz | R: read φX174 as FASTA, GenBank, EMBL, XML and real FASTQ with base R |
| 2.5 | Finding and downloading data | Bits vs bytes, download time, hash functions | Accession-ladder game, "which command?" game, download-time calculator, live MD5 checksum, exit quiz | Python + shell: ENA API, wget a real run, verify MD5 |

**Reading**
- Brown, *Genomes 5*: ch. 4 (sequencing genomes)
- Pevsner, *Bioinformatics and Functional Genomics*: ch. 2 (access to sequence data), ch. 9 (next-generation sequence data)
- Buffalo, *Bioinformatics Data Skills*: ch. 2 (project organisation), ch. 6 (bioinformatics data: downloading, checksums), ch. 10 (sequence data)
