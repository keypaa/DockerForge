#!/usr/bin/env python3
"""
DockerForge Fine-tuning Script
Fine-tunes Qwen2.5-Coder on Dockerfile generation using Unsloth.

Usage:
    python train.py --data_path ./data/train.json --output_dir ./output

Requirements:
    pip install unsloth[cu128-torch270]
    pip install transformers accelerate peft bitsandbytes
"""

import argparse
import os
import torch
from datasets import load_dataset
from unsloth import FastLanguageModel
from trl import SFTTrainer
from transformers import TrainingArguments, DataCollatorForSeq2Seq
from unsloth import is_bf16_supported

# Configuration
MAX_SEQ_LENGTH = 2048  # Can go up to 4K for Qwen
LORA_R = 32  # LoRA rank (16-64 recommended)
LORA_ALPHA = 32  # LoRA alpha
LORA_DROPOUT = 0.05  # LoRA dropout
TARGET_MODULES = [
    "q_proj",
    "k_proj",
    "v_proj",
    "o_proj",
    "gate_proj",
    "up_proj",
    "down_proj",
]  # Qwen modules


def load_data(data_path: str, format_type: str = "chatml"):
    """Load training data from JSON file.

    Expected format (ChatML):
    [
        {
            "messages": [
                {"role": "user", "content": "Write a Dockerfile for FastAPI"},
                {"role": "assistant", "content": "FROM python:3.11-slim..."}
            ]
        }
    ]
    """
    from datasets import Dataset

    # Load from JSON
    if data_path.endswith(".json"):
        dataset = load_dataset("json", data_path=data_path, split="train")
    elif data_path.endswith(".jsonl"):
        dataset = load_dataset("json", data_path=data_path, split="train")
    else:
        # Try loading as dataset
        dataset = load_dataset(data_path, split="train")

    # If messages column exists, use it, otherwise create from text
    if "messages" not in dataset.column_names:
        # Create messages from prompt/response columns
        def create_messages(example):
            if "prompt" in example and "response" in example:
                example["messages"] = [
                    {"role": "user", "content": example["prompt"]},
                    {"role": "assistant", "content": example["response"]},
                ]
            elif "instruction" in example and "output" in example:
                example["messages"] = [
                    {"role": "user", "content": example["instruction"]},
                    {"role": "assistant", "content": example["output"]},
                ]
            return example

        dataset = dataset.map(create_messages)

    return dataset


def formatting_prompts_func(example):
    """Format examples to ChatML format."""
    texts = []
    for msg in example["messages"]:
        role = msg["role"]
        content = msg["content"]
        # ChatML format
        text = f"<|im_start|>{role}\n{content}<|im_end|>"
        texts.append(text)
    return {"text": texts}


def create_trainer(
    model,
    tokenizer,
    train_dataset,
    eval_dataset=None,
    output_dir="./output",
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    num_train_epochs=3,
    learning_rate=2e-4,
):
    """Create SFTTrainer with optimal settings."""

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        dataset_text_field="text",
        max_seq_length=MAX_SEQ_LENGTH,
        data_collator=DataCollatorForSeq2Seq(tokenizer=tokenizer),
        formatting_func=formatting_prompts_func,
        # LoRA config
        lora_r=LORA_R,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        target_modules=TARGET_MODULES,
        bias="none",
        task_type="CAUSAL_LM",
        # Training args
        per_device_train_batch_size=per_device_train_batch_size,
        per_device_eval_batch_size=per_device_train_batch_size,
        gradient_accumulation_steps=gradient_accumulation_steps,
        warmup_ratio=0.1,
        num_train_epochs=num_train_epochs,
        learning_rate=learning_rate,
        fp16=not is_bf16_supported(),
        bf16=is_bf16_supported(),
        logging_steps=10,
        save_strategy="epoch",
        save_total_limit=2,
        optim="adamw_torch",
        weight_decay=0.01,
        lr_scheduler_type="cosine",
        seed=42,
        output_dir=output_dir,
        report_to="none",  # Change to "wandb" for Weights & Biases
    )

    return trainer


def main():
    parser = argparse.ArgumentParser(
        description="Fine-tune model on Dockerfile generation"
    )
    parser.add_argument(
        "--model_name",
        type=str,
        default="Qwen/Qwen2.5-Coder-7B-Instruct",
        help="Base model to fine-tune",
    )
    parser.add_argument(
        "--max_seq_length",
        type=int,
        default=MAX_SEQ_LENGTH,
        help="Maximum sequence length",
    )
    parser.add_argument(
        "--data_path",
        type=str,
        required=True,
        help="Path to training data (JSON/JSONL)",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./output",
        help="Output directory for model and adapters",
    )
    parser.add_argument(
        "--num_epochs", type=int, default=3, help="Number of training epochs"
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=2,
        help="Per-device batch size (adjust for GPU)",
    )
    parser.add_argument(
        "--gradient_accumulation",
        type=int,
        default=4,
        help="Gradient accumulation steps",
    )
    parser.add_argument(
        "--learning_rate", type=float, default=2e-4, help="Learning rate"
    )
    parser.add_argument(
        "--test_size", type=float, default=0.1, help="Validation split ratio"
    )

    args = parser.parse_args()

    print("=" * 50)
    print("DockerForge Fine-tuning")
    print("=" * 50)
    print(f"Model: {args.model_name}")
    print(f"Data: {args.data_path}")
    print(f"Output: {args.output_dir}")
    print(f"Epochs: {args.num_epochs}")
    print(f"Batch size: {args.batch_size}")
    print(
        f"GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}"
    )
    print("=" * 50)

    # Load model and tokenizer with Unsloth optimizations
    print("\n[1/4] Loading model with Unsloth...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=args.model_name,
        max_seq_length=args.max_seq_length,
        dtype=None,  # Auto-detect (bf16 if supported, else float16)
        load_in_4bit=False,  # Use bf16/fp16 for fine-tuning (use True for inference only)
        trust_remote_code=True,
    )

    # Add LoRA adapters
    print("[2/4] Adding LoRA adapters...")
    model = FastLanguageModel.get_peft_model(
        model,
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        target_modules=TARGET_MODULES,
        bias="none",
        use_gradient_checkpointing="unsloth",  # Reduce memory usage
        use_rslora=False,
        loftq_config=None,
    )

    # Print model info
    model.print_trainable_parameters()

    # Load and prepare data
    print("\n[3/4] Loading and preparing data...")
    full_dataset = load_data(args.data_path)

    # Split train/eval
    if args.test_size > 0:
        split = full_dataset.train_test_split(test_size=args.test_size, seed=42)
        train_dataset = split["train"]
        eval_dataset = split["test"]
    else:
        train_dataset = full_dataset
        eval_dataset = None

    print(f"Train: {len(train_dataset)} examples")
    if eval_dataset:
        print(f"Eval: {len(eval_dataset)} examples")

    # Format data
    train_dataset = train_dataset.map(formatting_prompts_func, batched=True)
    if eval_dataset:
        eval_dataset = eval_dataset.map(formatting_prompts_func, batched=True)

    # Create trainer
    print("\n[4/4] Starting training...")
    trainer = create_trainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        output_dir=args.output_dir,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.gradient_accumulation,
        num_train_epochs=args.num_epochs,
        learning_rate=args.learning_rate,
    )

    # Train
    trainer.train()

    # Save adapter
    print("\n[Saving] Saving adapters...")
    trainer.save_model(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)

    print("\n" + "=" * 50)
    print("Training complete!")
    print(f"Model saved to: {args.output_dir}")
    print("=" * 50)

    # Instructions for next steps
    print("""
Next steps:
1. Merge adapters and export to GGUF:
   python export_gguf.py --adapter_path ./output --output ./dockerforge-model

2. Or use directly with Unsloth:
   from unsloth import FastLanguageModel
   model, tokenizer = FastLanguageModel.from_pretrained(
       model_name="./output",
       load_in_4bit=True,
   )
""")


if __name__ == "__main__":
    main()
