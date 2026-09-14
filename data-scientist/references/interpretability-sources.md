# Interpretability sources

Primary sources inform method choice; none establishes a universal explanation
quality threshold.

| Source | Use |
|---|---|
| Ribeiro, Singh, and Guestrin, “Why Should I Trust You?” (LIME), KDD 2016, https://doi.org/10.1145/2939672.2939778 | Local surrogate explanations and locality assumptions. |
| Lundberg and Lee, “A Unified Approach to Interpreting Model Predictions” (SHAP), NeurIPS 2017, https://proceedings.neurips.cc/paper/2017/hash/8a20a8621978632d76c43dfd28b67767-Abstract.html | Additive attribution framing; implementation and dependence assumptions must be checked. |
| Adebayo et al., “Sanity Checks for Saliency Maps,” NeurIPS 2018, https://papers.nips.cc/paper/8160-sanity-checks-for-saliency-maps | Parameter/data randomization checks for some saliency methods. |
| Molnar, Interpretable Machine Learning, https://christophm.github.io/interpretable-ml-book/ | Living reference for method assumptions and limitations; verify cited methods against original papers. |
| Mitchell et al., “Model Cards for Model Reporting,” FAT* 2019, https://doi.org/10.1145/3287560.3287596 | Documentation of intended use, performance, and subgroup limitations. |
