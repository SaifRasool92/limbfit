"""
Phase 6 fine-tuning is skipped because:
- sentence-transformers requires PyTorch >= 2.5 but 2.2.2 is installed
- No network available to install updated PyTorch

The baseline ChromaDB DefaultEmbeddingFunction (all-MiniLM-L6-v2 via onnxruntime)
is used instead. This note is recorded in docs/MODEL_CARD.md under Limitations.
"""
print("Fine-tuning skipped: PyTorch version incompatible with sentence-transformers.")
print("Using ChromaDB DefaultEmbeddingFunction (all-MiniLM-L6-v2, ONNX) as the embedder.")
print("See docs/MODEL_CARD.md for details.")
