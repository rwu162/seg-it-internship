from pathlib import Path
import argparse


def truncate_first_20(text: str) -> str:
    """Extract first 20 characters from text"""
    return text[:20]


def process_jpg_files(path: Path) -> set:
    """Process JPG files and extract serial numbers"""
    serial_data = set()
    
    
    if path.is_file():
        # Single file
        if path.suffix.lower() in ['.jpg', '.jpeg']:
            serial = truncate_first_20(path.stem)
            serial_data.add(serial)
            print(f"Processed: {path.name} -> Serial: {serial}")
        else:
            print(f"Warning: '{path.name}' is not a JPG file")
    
    elif path.is_dir():
        # Directory of files
        jpg_files = list(path.glob('*.jpg')) + list(path.glob('*.jpeg'))
        jpg_files.extend(path.glob('*.JPG'))
        jpg_files.extend(path.glob('*.JPEG'))
        
        if not jpg_files:
            print("No JPG files found in directory")
            return serial_data
            
        print(f"Found {len(jpg_files)} JPG files to process...")
        
        for filepath in jpg_files:
            serial = truncate_first_20(filepath.stem)
            serial_data.add(serial)
            print(f"Processed: {filepath.name} -> Serial: {serial}")
    
    return serial_data


def main():
    parser = argparse.ArgumentParser(
        description='Extract serial numbers from JPG filenames'
    )
    parser.add_argument(
        'path',
        type=Path,
        help='Path to JPG file or directory containing JPG files'
    )
    
    args = parser.parse_args()
    
    if not args.path.exists():
        print(f"Error: '{args.path}' not found")
        return set()
    
    # Process files
    serial_data = process_jpg_files(args.path)
    
    if serial_data:
        print(f"\nTotal unique serials: {len(serial_data)}")
    else:
        print("No JPG files were processed")
    
    return serial_data


if __name__ == "__main__":
    serial_set = main()