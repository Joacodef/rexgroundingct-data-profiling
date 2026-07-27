import os
import sys
import json
import argparse
import numpy as np
import nibabel as nib
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

BASE_DIR = os.environ.get("BASE_DIR", os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
IMG_DIR = os.environ.get("IMG_RAW_DIR", os.path.join(BASE_DIR, "data/raw/images"))
SEG_DIR = os.environ.get("SEG_RAW_DIR", os.path.join(BASE_DIR, "data/raw/segmentations"))
DATASET_JSON = os.environ.get("DATASET_JSON", os.path.join(BASE_DIR, "data/dataset.json"))


def export_itksnap_masks(scan_name, output_dir):
    """
    Exports ITK-SNAP compatible 3D NIfTI masks from raw 4D segmentation files
    by fixing the identity affine header bug using the CT image's native affine matrix.
    """
    img_path = os.path.join(IMG_DIR, scan_name)
    seg_path = os.path.join(SEG_DIR, scan_name)

    if not os.path.exists(img_path):
        raise FileNotFoundError(f"Raw CT image not found: {img_path}")
    if not os.path.exists(seg_path):
        raise FileNotFoundError(f"Raw segmentation mask not found: {seg_path}")

    os.makedirs(output_dir, exist_ok=True)

    print(f"=" * 60)
    print(f"EXPORTING ITK-SNAP COMPATIBLE MASKS FOR: {scan_name}")
    print(f"=" * 60)

    # 1. Load native CT image and extract real physical affine & header
    ct_nii = nib.load(img_path)
    ct_affine = ct_nii.affine
    ct_header = ct_nii.header
    ct_shape = ct_nii.shape

    print(f"CT Volume Path   : {img_path}")
    print(f"CT Volume Shape  : {ct_shape}")
    print(f"CT Physical Affine:\n{ct_affine}\n")

    # 2. Load 4D segmentation mask
    seg_nii = nib.load(seg_path)
    seg_data = seg_nii.get_fdata()
    raw_affine = seg_nii.affine

    print(f"Raw Mask Path    : {seg_path}")
    print(f"Raw Mask Shape   : {seg_data.shape}")
    print(f"Raw Mask Affine  : {raw_affine[0,0]}, {raw_affine[1,1]}, {raw_affine[2,2]} (Identity Check: {np.allclose(raw_affine, np.eye(4))})")

    # 3. Ensure format is (C, X, Y, Z) or (X, Y, Z, C)
    if seg_data.ndim == 4:
        # Check channel axis
        if seg_data.shape[0] < seg_data.shape[-1] and seg_data.shape[0] <= 32:
            # Channel is first: shape = (C, X, Y, Z)
            num_channels = seg_data.shape[0]
            channels = [seg_data[i] for i in range(num_channels)]
            spatial_shape = seg_data.shape[1:]
        else:
            # Channel is last: shape = (X, Y, Z, C)
            num_channels = seg_data.shape[-1]
            channels = [seg_data[..., i] for i in range(num_channels)]
            spatial_shape = seg_data.shape[:3]
    elif seg_data.ndim == 3:
        num_channels = 1
        channels = [seg_data]
        spatial_shape = seg_data.shape
    else:
        raise ValueError(f"Unsupported mask dimensionality: {seg_data.ndim}D")

    print(f"Detected {num_channels} finding channel(s) with spatial shape {spatial_shape}.")

    # 4. Generate 3D Multi-label Mask (Label 1 = Finding 0, Label 2 = Finding 1, etc.)
    multilabel_3d = np.zeros(spatial_shape, dtype=np.uint16)
    
    # Fill in reverse so lower indices don't overwrite if overlapping, or prioritize later
    for c_idx in range(num_channels):
        binary_mask = (channels[c_idx] > 0)
        voxel_count = np.sum(binary_mask)
        multilabel_3d[binary_mask] = c_idx + 1
        print(f"  Finding Channel {c_idx}: {voxel_count:,} positive voxels -> Assigned Label {c_idx + 1}")

    base_name = scan_name.replace(".nii.gz", "").replace(".nii", "")
    
    # Save combined 3D multi-label mask
    multilabel_filename = f"{base_name}_itksnap_multilabel.nii.gz"
    multilabel_path = os.path.join(output_dir, multilabel_filename)
    
    multilabel_nii = nib.Nifti1Image(multilabel_3d, ct_affine)
    nib.save(multilabel_nii, multilabel_path)
    print(f"\n[SUCCESS] Saved 3D Multi-Label Mask: {multilabel_path}")

    # Save individual 3D binary masks per finding
    saved_binary_paths = []
    for c_idx in range(num_channels):
        binary_mask_3d = (channels[c_idx] > 0).astype(np.uint8)
        binary_filename = f"{base_name}_itksnap_finding_{c_idx}.nii.gz"
        binary_path = os.path.join(output_dir, binary_filename)
        
        binary_nii = nib.Nifti1Image(binary_mask_3d, ct_affine)
        nib.save(binary_nii, binary_path)
        saved_binary_paths.append(binary_path)

    print(f"[SUCCESS] Saved {len(saved_binary_paths)} individual 3D binary finding masks.")

    # 5. Output ITK-SNAP Usage Instructions
    print("\n" + "=" * 60)
    print("HOW TO LOAD IN ITK-SNAP:")
    print("=" * 60)
    print(f"1. Open ITK-SNAP.")
    print(f"2. File -> Open Main Image -> Select raw CT scan:")
    print(f"   {img_path}")
    print(f"3. Segmentation -> Open Segmentation -> Select converted 3D multi-label mask:")
    print(f"   {multilabel_path}")
    print(f"4. (Optional) Alternatively open individual finding overlays from:")
    print(f"   {output_dir}")
    print("=" * 60)

    return multilabel_path, saved_binary_paths


def main():
    parser = argparse.ArgumentParser(description="Export ITK-SNAP compatible 3D NIfTI masks for ReXGroundingCT")
    parser.add_argument("--scan_name", type=str, default=None, help="Name of CT scan file (e.g., train_1935_a_1.nii.gz)")
    parser.add_argument("--output_dir", type=str, default=None, help="Output directory for converted 3D masks")

    args = parser.parse_args()

    # If no scan specified, grab the first scan listed in dataset.json
    if not args.scan_name:
        if os.path.exists(DATASET_JSON):
            with open(DATASET_JSON, "r") as f:
                data = json.load(f)
            train_scans = data.get("train", [])
            # Find a scan with multiple findings (e.g. train_1935_a_1.nii.gz)
            selected_scan = None
            for s in train_scans:
                if len(s.get("findings", {})) > 1:
                    selected_scan = s["name"]
                    break
            if not selected_scan and train_scans:
                selected_scan = train_scans[0]["name"]
            scan_name = selected_scan or "train_1935_a_1.nii.gz"
        else:
            scan_name = "train_1935_a_1.nii.gz"
    else:
        scan_name = args.scan_name

    default_out_dir = os.path.abspath(os.path.dirname(__file__))
    output_dir = args.output_dir or default_out_dir

    export_itksnap_masks(scan_name, output_dir)


if __name__ == "__main__":
    main()
