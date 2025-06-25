
# SLR: An Automated Synthesis Framework for Scalable Logical Reasoning

[![Hugging Face](https://img.shields.io/badge/🤗%20Hugging%20Face-Datasets-yellow)](https://huggingface.co/datasets/AIML-TUDA/SLR-Bench)
[![Eval & Reward Model](https://img.shields.io/badge/%F0%9F%A4%96%20Reward%20Model-HF-blueviolet)](https://huggingface.co/spaces/AIML-TUDA/VerifiableRewardsForScalableLogicalReasoning)
[![arXiv](https://img.shields.io/badge/arXiv-2506.15787-b31b1b.svg)](https://arxiv.org/abs/2506.15787)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> **Note:** Source code of the generation pipeline will follow shortly.

> **🆕 June 2024: Reward Model & Evaluation Pipeline Released!**  
> Systematically evaluate model-generated rules via symbolic execution, fully automatic and verifiable. Supports evaluation and RLVR. 👉 [Eval & Reward Demo](https://huggingface.co/spaces/AIML-TUDA/VerifiableRewardsForScalableLogicalReasoning)

--- 
## Overview
**SLR** (*Scalable Logical Reasoning*) is an end-to-end framework for systematic evaluation and training of Large Language Models (LLMs) through Scalable Logical Reasoning. Given a user’s task specification, SLR enables scalable, automated synthesis of inductive reasoning tasks with precisely controlled difficulty. For each task, SLR generates (i) a latent ground-truth rule, (ii) an executable validation program for deterministic, symbolic evaluation, and (iii) an instruction prompt for the reasoning task.
With SLR, we introduce SLR-Bench—a benchmark of over 19,000 prompts across 20 curriculum levels, progressively increasing in relational, arithmetic, and recursive complexity. Large-scale evaluation shows that while modern LLMs can produce syntactically valid rules, they often struggle with correct logical inference. Recent reasoning-focused LLMs perform better but require much more compute, sometimes exceeding 15,000 completion tokens.
Logic-tuning with SLR doubles Llama-3-8B’s accuracy on SLR-Bench, matching Gemini-Flash-Thinking at a fraction of the computational cost. SLR is fully automated, requires no human annotation, ensures dataset novelty, and provides a scalable environment for advancing LLM reasoning capabilities.

---
## Quick start SLR-Bench

### Loading the Dataset
```python
from datasets import load_dataset
# Load SLR-Bench test split
ds = load_dataset("AIML-TUDA/SLR-Bench", "v1-All", split="test")
```
### Evaluate using SLR-Bench
Requires the [`evaluate`](https://huggingface.co/docs/evaluate/) library and a Prolog interpreter installed on your system (e.g., [SWI-Prolog](https://www.swi-prolog.org/)).
Install the required dependencies via:

```bash
pip install evaluate
sudo apt-get install swi-prolog
```

#### Example Usage

```python
from evaluate import load
symbolic_judge = load("AIML-TUDA/VerifiableRewardsForScalableLogicalReasoning")
rules = ds["ground-truth rule"]  # For demo only—use model predictions in practice
references = [
    {
        "validation_program": p,
        "evaluation_config": {
            "positive_predicate": "eastbound",
            "negative_predicate": "westbound"
        }
    } for p in ds["validation program"]
]

results = symbolic_judge.compute(predictions=rules, references=references)
print(results)
```

*Note: For real evaluation, replace `rules` with your model's predicted rules. Here, we use ground-truth rules for demonstration only.*


---



- 🔨 **Automatic Task Generation:** Synthesize new inductive reasoning tasks with controllable complexity, novel logic rules, and natural language prompts—no need for human annotation.
- 🧩 **Programmable & Scalable:** Specify your own logic vocabulary, grammar, rule distributions, and task parameters; supports curriculum-style scaling and out-of-distribution task creation.
- 🧠 **Symbolic, Automated Evaluation:** Deterministically verify LLM outputs via the validation program, not MCQA, LLM judge, or exact matching.
- 📈 **Curriculum Learning:** Use SLR-Bench, a structured 20-level benchmark, for evaluating and training models across a span of logical challenges.
<p align="center">
  <img src="images/main.jpg" alt="SLR Overview" width="800">
</p>

*SLR: End-to-end pipeline for logic task generation, deterministic symbolic evaluation, and logic-based LLM training.*

---


## SLR-Bench: Benchmarking Reasoning at Scale

We instantiate SLR as **SLR-Bench**, an automatically generated reasoning benchmark for LLMs. SLR-Bench comprises 19,000+ prompts spanning 20 curriculum levels, from simple attribute lookups to advanced relational, arithmetic, and recursive tasks.

<p align="center">
  <img src="images/SLR-Bench2.jpg" width="400">
</p>

*SLR-Bench: As logic complexity rises, model accuracy drops—exposing limits of contemporary LLMs and creating new challenges for future models.*



Below is the leaderboard for various LLMs on SLR-Bench (V0.1):
<p align="center">
<img src="images/SLR-Bench.png" width="800">
</p>

*Reasoning LLMs outperform base LLMs on logical accuracy but incur much higher compute requirements. Logic-tuning with SLR dramatically boosts performance for base models at low cost.*

---

## Citation

```bibtex
@misc{helff2025slrautomatedsynthesisframework,
      title={SLR: An Automated Synthesis Framework for Scalable Logical Reasoning}, 
      author={Lukas Helff and Ahmad Omar and Felix Friedrich and Wolfgang Stammer and Antonia Wüst and Tim Woydt and Rupert Mitchell and Patrick Schramowski and Kristian Kersting},
      year={2025},
      eprint={2506.15787},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2506.15787}, 
}
```
