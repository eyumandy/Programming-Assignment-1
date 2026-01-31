# Gale-Shapley Stable Matching

**Team Members:** Yumandy Espinosa
**UFID:** 12856052

## How to Run

**Matcher:**
```bash
python src/matcher.py data/example.in
```

**Verifier:**
```bash
python src/verifier.py data/example.in output.txt
```

**Scalability testing (Part C):**
```bash
python tests/scalability_test.py
```
Generates graphs and timing data for n = 1, 2, 4, ..., 512.

## Part C Results

I measured running time by timing each algorithm call over 3 trials and averaging. Both the matcher and verifier show O(n²) growth—when problem size doubles, time roughly quadruples. For small n (≤64), Python startup overhead keeps time flat around 0.035s. Once we hit n=128+, the quadratic trend becomes obvious: n=128 takes 0.04s, n=256 takes 0.06s, and n=512 takes 0.21s.
See graphs in results/scalability_graphs.png showing this trend clearly.

## Assumptions

- Input files are well-formed
- Equal number of hospitals and students
- Complete preference lists (everyone ranks everyone)
- Python 3.x installed
- matplotlib needed for Part C graphs: `pip install matplotlib`
