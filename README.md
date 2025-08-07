# SEG_IT

A Python utility collection for file processing operations, specifically designed for serial number extraction from JPG files and file management with backup functionality.

## Features

- **Serial Number Extraction**: Extract the first 20 characters from JPG filenames as serial numbers
- **File Management**: Move files between directories with automatic backup of existing files
- **Batch Processing**: Handle single files or entire directories
- **Cross-platform**: Uses pathlib for Windows/Unix compatibility

## Installation

Clone the repository:
```bash
git clone https://github.com/yourusername/SEG_IT.git
cd SEG_IT
```

No additional dependencies required - uses Python standard library only.

## Usage

### Serial Number Extraction (`main.py`)

Extract serial numbers from JPG filenames by taking the first 20 characters of the filename.

```bash
# Process a single JPG file
python main.py image.jpg

# Process all JPG files in a directory
python main.py /path/to/images/

# Process files in the sample directory
python main.py 20250625/
```

**Example Output:**
```
Found 4 JPG files to process...
Processed: SEGUSSG4AW2506043010-2.jpg → Serial: SEGUSSG4AW2506043010
Processed: SEGUSSG4AW2506049685.jpg → Serial: SEGUSSG4AW2506049685
Processed: SEGUSSG4AW2506052225.jpg → Serial: SEGUSSG4AW2506052225
Processed: SEGUSSG4AW2506052340.jpg → Serial: SEGUSSG4AW2506052340

Total unique serials: 4
```

### File Management with Backup (`swap.py`)

Move files to a target directory while automatically backing up any existing files.

```bash
python swap.py <source_file> <target_directory> <backup_directory>
```

**Example:**
```bash
python swap.py document.txt ./active/ ./backup/
```

**What it does:**
1. Creates target and backup directories if they don't exist
2. Moves any existing files in the target directory to the backup directory
3. Handles filename conflicts in backup by adding numbers (e.g., `file_1.txt`, `file_2.txt`)
4. Moves the new file to the target directory

## File Structure

```
SEG_IT/
├── main.py              # Serial number extraction utility
├── swap.py              # File management utility
├── 20250625/            # Sample JPG files for testing
│   ├── SEGUSSG4AW2506043010-2.jpg
│   ├── SEGUSSG4AW2506049685.jpg
│   ├── SEGUSSG4AW2506052225.jpg
│   └── SEGUSSG4AW2506052340.jpg
├── README.md
└── CLAUDE.md            # Development guidance
```

## Requirements

- Python 3.6+
- No external dependencies

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with the sample files in `20250625/`
5. Submit a pull request

## License

This project is open source and available under the MIT License.
