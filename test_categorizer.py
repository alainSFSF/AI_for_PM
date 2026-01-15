#!/usr/bin/env python3
"""
Test script for the Website Categorizer
Runs categorization on all example files
"""

import glob
from website_categorizer import categorize_from_file


def test_all_examples():
    """Test the categorizer on all example files"""
    print("\n" + "=" * 70)
    print("Website Categorizer - Batch Test")
    print("=" * 70 + "\n")

    example_files = glob.glob("examples/*.txt")

    if not example_files:
        print("No example files found in examples/ directory")
        return

    results = []

    for file_path in example_files:
        print(f"Processing: {file_path}")
        print("-" * 70)

        try:
            result = categorize_from_file(file_path)
            results.append({
                "file": file_path,
                "category": result["category"],
                "confidence": result["confidence"],
                "reasoning": result["reasoning"]
            })

            print(f"✓ Category: {result['category']}")
            print(f"  Confidence: {result['confidence']}")
            print(f"  Reasoning: {result['reasoning']}\n")

        except Exception as e:
            print(f"✗ Error: {e}\n")
            results.append({
                "file": file_path,
                "category": "ERROR",
                "confidence": "N/A",
                "reasoning": str(e)
            })

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70 + "\n")

    for r in results:
        filename = r["file"].split("/")[-1]
        print(f"{filename:30} → {r['category']:20} ({r['confidence']})")

    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    test_all_examples()
