#!/usr/bin/env python3
"""
Verify that LlamaIndex is installed and can create a basic index.
Run this script to check your setup before building applications.
"""

import sys
import importlib

REQUIRED_PACKAGES = [
    "llama_index",
    "llama_index.core",
]

OPTIONAL_PACKAGES = [
    "llama_index.llms.openai",
    "llama_index.vector_stores.qdrant",
    "llama_index.embeddings.openai",
    "llama_parse",
    "llama_deploy",
]


def check_package(name: str, required: bool = True) -> bool:
    """Check if a package is importable."""
    try:
        importlib.import_module(name)
        print(f"  [OK] {name}")
        return True
    except ImportError:
        status = "REQUIRED" if required else "optional"
        print(f"  [MISSING] {name} ({status})")
        return not required


def main():
    print("LlamaIndex Setup Check")
    print("=" * 40)

    # Python version
    print(f"\nPython: {sys.version}")
    if sys.version_info < (3, 9):
        print("  [FAIL] Python 3.9+ required")
        sys.exit(1)

    # Core packages
    print("\nCore:")
    all_ok = all(check_package(pkg, required=True) for pkg in REQUIRED_PACKAGES)

    # Optional packages
    print("\nOptional:")
    for pkg in OPTIONAL_PACKAGES:
        check_package(pkg, required=False)

    # Test basic functionality
    print("\nFunctionality test:")
    try:
        from llama_index.core import Document
        from llama_index.core.node_parser import SentenceSplitter

        doc = Document(text="Test document for LlamaIndex setup verification.")
        parser = SentenceSplitter(chunk_size=256, chunk_overlap=20)
        nodes = parser.get_nodes_from_documents([doc])
        print(f"  [OK] Document chunking works ({len(nodes)} nodes)")

        # Test Settings
        from llama_index.core import Settings
        default_chunk = Settings.text_splitter
        print(f"  [OK] Settings accessible")

    except Exception as e:
        print(f"  [FAIL] Basic functionality test failed: {e}")
        all_ok = False

    print("\n" + "=" * 40)
    if all_ok:
        print("Setup check: ALL REQUIRED PACKAGES OK")
    else:
        print("Setup check: SOME REQUIRED PACKAGES MISSING")
        print("Install missing packages with:")
        print("  pip install llama-index-core")
        print("  pip install llama-index-llms-openai")
        sys.exit(1)


if __name__ == "__main__":
    main()
