"""
Download MIMIC-IV dataset from Kaggle using kagglehub.

This script downloads the akshaybe/updated-mimic-iv dataset which contains:
- ICU stays data
- Patient demographics
- Vital signs (chartevents)
- Laboratory results (labevents)
- Diagnoses (ICD codes)

Usage:
    python scripts/download_data.py
    python scripts/download_data.py --output-dir /path/to/data
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional

try:
    import kagglehub
except ImportError:
    print("Error: kagglehub not installed. Install with: pip install kagglehub")
    sys.exit(1)


def download_mimic_iv(output_dir: Optional[str] = None) -> Path:
    """
    Download MIMIC-IV dataset from Kaggle.

    Args:
        output_dir: Optional custom output directory.
                   If None, uses kagglehub default cache location.

    Returns:
        Path to the downloaded dataset directory
    """
    print("=" * 80)
    print("MIMIC-IV Dataset Download")
    print("=" * 80)
    print("\nDataset: akshaybe/updated-mimic-iv")
    print("Source: Kaggle")
    print("\nThis dataset contains:")
    print("  - ICU stays information")
    print("  - Patient demographics")
    print("  - Vital signs (heart rate, blood pressure, temperature, etc.)")
    print("  - Laboratory results (WBC, lactate, creatinine, etc.)")
    print("  - Diagnoses (ICD-10 codes)")
    print("\n" + "=" * 80)

    # Download dataset
    print("\n[1/3] Downloading dataset from Kaggle...")
    try:
        path = kagglehub.dataset_download("akshaybe/updated-mimic-iv")
        print(f"✓ Download complete!")
        print(f"  Location: {path}")
    except Exception as e:
        print(f"✗ Download failed: {str(e)}")
        print("\nTroubleshooting:")
        print("  1. Make sure you have Kaggle credentials configured")
        print("     Run: kaggle --version")
        print("  2. Set up Kaggle API token:")
        print("     - Go to https://www.kaggle.com/settings")
        print("     - Create new API token (downloads kaggle.json)")
        print("     - Place kaggle.json in ~/.kaggle/")
        print("  3. Ensure you have internet connection")
        sys.exit(1)

    dataset_path = Path(path)

    # Verify dataset structure
    print("\n[2/3] Verifying dataset structure...")
    expected_files = [
        "icustays.csv",
        "patients.csv",
        "admissions.csv",
        "chartevents.csv",
        "labevents.csv",
        "diagnoses_icd.csv"
    ]

    found_files = []
    missing_files = []

    for file in expected_files:
        file_path = dataset_path / file
        if file_path.exists():
            size_mb = file_path.stat().st_size / (1024 * 1024)
            found_files.append((file, size_mb))
            print(f"  ✓ {file:<25} ({size_mb:,.1f} MB)")
        else:
            missing_files.append(file)
            print(f"  ✗ {file:<25} (NOT FOUND)")

    if missing_files:
        print(f"\n⚠ Warning: {len(missing_files)} expected files not found")
        print("   Missing files:", ", ".join(missing_files))
        print("   Dataset may be incomplete or have different structure")

    # Copy to custom output directory if specified
    if output_dir:
        print(f"\n[3/3] Copying to custom directory: {output_dir}")
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        import shutil
        for file, _ in found_files:
            src = dataset_path / file
            dst = output_path / file
            print(f"  Copying {file}...")
            shutil.copy2(src, dst)

        dataset_path = output_path
        print("  ✓ Copy complete!")
    else:
        print("\n[3/3] Using kagglehub cache location (no copy needed)")

    # Summary
    print("\n" + "=" * 80)
    print("DOWNLOAD SUMMARY")
    print("=" * 80)
    print(f"Dataset location: {dataset_path}")
    print(f"Files found: {len(found_files)}")
    total_size = sum(size for _, size in found_files)
    print(f"Total size: {total_size:,.1f} MB ({total_size/1024:.2f} GB)")

    print("\nNext steps:")
    print("  1. Verify data integrity:")
    print(f"     python scripts/verify_data.py --data-path {dataset_path}")
    print("  2. Ingest data into PostgreSQL:")
    print(f"     python scripts/ingest_mimic_iv.py --data-path {dataset_path}")
    print("=" * 80)

    return dataset_path


def main():
    parser = argparse.ArgumentParser(
        description="Download MIMIC-IV dataset from Kaggle",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download to default location
  python scripts/download_data.py

  # Download to custom directory
  python scripts/download_data.py --output-dir ./data/mimic_iv

  # Check download without re-downloading
  python scripts/download_data.py --check-only
        """
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        help="Custom output directory (optional, uses kagglehub cache if not specified)"
    )

    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check if dataset exists, don't download"
    )

    args = parser.parse_args()

    if args.check_only:
        print("Check-only mode not implemented yet")
        print("Just run without --check-only to download")
        return

    try:
        dataset_path = download_mimic_iv(args.output_dir)

        # Save path to config file for other scripts
        config_dir = Path(__file__).parent.parent / "config"
        config_dir.mkdir(exist_ok=True)

        config_file = config_dir / "data_path.txt"
        with open(config_file, "w") as f:
            f.write(str(dataset_path))

        print(f"\n✓ Dataset path saved to: {config_file}")

    except KeyboardInterrupt:
        print("\n\n⚠ Download interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
