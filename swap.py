
import argparse
import shutil
import os
from pathlib import Path


def safe_move(src, dst, description="item"):
    """
    Safely move a file with error handling and logging
    
    Args:
        src: Source path
        dst: Destination path
        description: Description of what's being moved for logging
    """
    try:
        shutil.move(str(src), str(dst))
        print(f"Moved {description}: {src.name} -> {dst}")
        return True
    except Exception as e:
        print(f"Error moving {description}: {e}")
        return False


def simple_move_with_backup(source_path, target_dir, backup_dir, dry_run=False):
    """Move files/folders to target with backup of existing items"""
    # Validate source exists and is file or directory
    if not source_path.exists():
        print(f"Error: Source '{source_path}' does not exist")
        return False
    if not (source_path.is_file() or source_path.is_dir()):
        print(f"Error: '{source_path}' is neither a file nor a directory")
        return False
    
    # Validate target directory
    if not target_dir.exists():
        print(f"Error: Target directory '{target_dir}' does not exist")
        return False
    if not target_dir.is_dir():
        print(f"Error: '{target_dir}' is not a directory")
        return False
    
    # Ensure backup directory exists
    backup_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / source_path.name
    
    if target_path.exists():
        # Generate unique backup name
        backup_path = backup_dir / source_path.name
        counter = 1
        while backup_path.exists():
            if source_path.is_file():
                new_name = source_path.stem + "_" + str(counter) + source_path.suffix
            else:
                new_name = source_path.name + "_" + str(counter)
            backup_path = backup_dir / new_name
            counter += 1
        
        action_verb = "Would copy" if dry_run else "Copying"
        item_type = "file" if target_path.is_file() else "directory"
        print(f"{action_verb} existing {item_type} to backup: {target_path.name} -> {backup_path.name}")
        
        if not dry_run:
            try:
                if target_path.is_dir():
                    shutil.copytree(target_path, backup_path)
                else:
                    shutil.copy2(target_path, backup_path)
                print(f"Backed up existing {item_type}: {target_path.name} -> {backup_path.name}")
            except Exception as e:
                print(f"Error backing up existing {item_type}: {e}")
                return False
        
        # Now overwrite the existing file
        print(f"Overwriting existing {item_type} in target")
        if not dry_run:
            if target_path.is_dir():
                shutil.rmtree(target_path)
            else:
                target_path.unlink()
    else:
        print("No existing item to backup")
    
    # Move source to target
    item_type = "file" if source_path.is_file() else "directory"
    if dry_run:
        print(f"Would move {item_type}: {source_path.name} -> {target_path}")
        return True
    return safe_move(source_path, target_path, f"{item_type} to target")


def main():
    parser = argparse.ArgumentParser(
        description='Move files or directories to target directory with backup of existing items'
    )
    parser.add_argument(
        'source_path',
        type=Path,
        help='Path to the file or directory to move'
    )
    parser.add_argument(
        'target_dir',
        type=Path,
        help='Target directory to move the file or folder to'
    )
    parser.add_argument(
        'backup_dir',
        type=Path,
        help='Directory to backup existing files or folders to'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would happen without making any changes'
    )
    args = parser.parse_args()
    
    if args.dry_run:
        print("DRY RUN MODE - No files will be moved\n")
    
    success = simple_move_with_backup(args.source_path, args.target_dir, args.backup_dir, args.dry_run)
    if success:
        print("\nDry run completed successfully" if args.dry_run else "Operation completed successfully")
    else:
        print("Operation failed")


if __name__ == "__main__":
    main()

