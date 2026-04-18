#!/usr/bin/env python3
"""
Export fine-tuned model to GGUF format for local inference.

Usage:
    python export_gguf.py --adapter_path ./output --output ./dockerforge-model

Requirements:
    pip install unsloth
"""

import argparse
import os
from unsloth import FastLanguageModel
from transformers import AutoTokenizer


def export_to_gguf(
    adapter_path: str,
    output_path: str,
    quantization_method: str = "q4_k_m",
    merge_and_unload: bool = True,
):
    """Export LoRA adapter to GGUF format.

    Args:
        adapter_path: Path to saved LoRA adapters
        output_path: Output GGUF file path
        quantization_method: Q4_K_M, Q5_K_M, Q8_0, F16
        merge_and_unload: Whether to merge adapters into base model
    """
    print("=" * 50)
    print("Exporting to GGUF")
    print("=" * 50)
    print(f"Adapter: {adapter_path}")
    print(f"Output: {output_path}")
    print(f"Quantization: {quantization_method}")
    print()

    # Check available methods
    if quantization_method not in ["q4_k_m", "q5_k_m", "q8_0", "f16", "q4_0", "q5_0"]:
        print(f"Warning: {quantization_method} may not be optimal")

    # Method mapping for save_pretrained_gguf
    # Supported: q4_k_m, q5_k_m, q8_0, f16

    # Load model with adapters
    print("[1/3] Loading model with adapters...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=adapter_path,
        max_seq_length=2048,
        load_in_4bit=False,
        dtype=None,
    )

    print("[2/3] Exporting to GGUF...")
    # This saves both merged model and quantized GGUF
    model.save_pretrained_gguf(
        output_path,
        quantization_method=quantization_method,
        tokenizer=tokenizer,
    )

    print("[3/3] Done!")
    print()
    print(f"✅ Model saved to: {output_path}")
    print()
    print("File sizes:")
    for f in os.listdir(output_path):
        size = os.path.getsize(os.path.join(output_path, f)) / (1024 * 1024)
        print(f"  {f}: {size:.1f} MB")

    print()
    print("=" * 50)
    print("Usage with llama.cpp:")
    print(
        f"  ./llama-cli -m {output_path}/model.gguf -p 'Write a Dockerfile for FastAPI'"
    )
    print()
    print("Usage with Ollama:")
    print(f"  ollama create dockerforge -f Modelfile")
    print(f"  # Then copy model.gguf to Ollama models directory")
    print("=" * 50)


def merge_only(adapter_path: str, output_path: str):
    """Merge adapters into base model without quantization."""
    print("[1/2] Loading model with adapters...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=adapter_path,
        max_seq_length=2048,
        load_in_4bit=False,
    )

    print("[2/2] Merging adapters...")
    merged_model = model.merge_and_unload()

    print(f"Saving merged model to {output_path}...")
    merged_model.save_pretrained(output_path)
    tokenizer.save_pretrained(output_path)

    print("✅ Done! Model merged and saved.")


def main():
    parser = argparse.ArgumentParser(description="Export fine-tuned model to GGUF")
    parser.add_argument(
        "--adapter_path",
        type=str,
        required=True,
        help="Path to LoRA adapters from training",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="./dockerforge-model",
        help="Output GGUF directory",
    )
    parser.add_argument(
        "--quantization",
        type=str,
        default="q4_k_m",
        choices=["q4_k_m", "q5_k_m", "q8_0", "f16"],
        help="Quantization method",
    )
    parser.add_argument(
        "--merge_only", action="store_true", help="Only merge, don't quantize"
    )

    args = parser.parse_args()

    if args.merge_only:
        merge_only(args.adapter_path, args.output)
    else:
        export_to_gguf(
            adapter_path=args.adapter_path,
            output_path=args.output,
            quantization_method=args.quantization,
        )


if __name__ == "__main__":
    main()
