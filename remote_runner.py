import paramiko
import argparse
import getpass
from pathlib import Path
import sys


class RemoteRunner:
    """SSH-based remote execution wrapper for SEG_IT utilities"""
    
    def __init__(self, hostname, username, password=None, port=22):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port
        self.ssh_client = None
        self.sftp_client = None
    
    def connect(self):
        """Establish SSH connection"""
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddHostKey())
            
            if not self.password:
                self.password = getpass.getpass(f"Password for {self.username}@{self.hostname}: ")
            
            self.ssh_client.connect(
                hostname=self.hostname,
                username=self.username,
                password=self.password,
                port=self.port,
                timeout=30
            )
            
            self.sftp_client = self.ssh_client.open_sftp()
            print(f"Connected to {self.hostname}")
            return True
            
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Close SSH connection"""
        if self.sftp_client:
            self.sftp_client.close()
        if self.ssh_client:
            self.ssh_client.close()
        print("Disconnected")
    
    def execute_command(self, command):
        """Execute command on remote server"""
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
            exit_code = stdout.channel.recv_exit_status()
            
            if exit_code != 0:
                print(f"Command failed with exit code {exit_code}")
                if error:
                    print(f"Error: {error}")
                return None
            
            return output
            
        except Exception as e:
            print(f"Command execution failed: {e}")
            return None
    
    def upload_script(self, local_script, remote_path):
        """Upload local script to remote server"""
        try:
            self.sftp_client.put(local_script, remote_path)
            print(f"Uploaded {local_script} to {remote_path}")
            return True
        except Exception as e:
            print(f"Upload failed: {e}")
            return False
    
    def remote_serial_extraction(self, remote_path, upload_scripts=False):
        """Run serial number extraction on remote server"""
        remote_script_path = "/tmp/main.py"
        
        if upload_scripts:
            if not self.upload_script("main.py", remote_script_path):
                return None
        
        command = f"python3 {remote_script_path} '{remote_path}'"
        print(f"Running: {command}")
        
        output = self.execute_command(command)
        return output
    
    def remote_file_move(self, source_path, target_dir, backup_dir, dry_run=False, upload_scripts=False):
        """Run file move operation on remote server"""
        remote_script_path = "/tmp/swap.py"
        
        if upload_scripts:
            if not self.upload_script("swap.py", remote_script_path):
                return None
        
        dry_run_flag = "--dry-run" if dry_run else ""
        command = f"python3 {remote_script_path} '{source_path}' '{target_dir}' '{backup_dir}' {dry_run_flag}"
        print(f"Running: {command}")
        
        output = self.execute_command(command)
        return output
    
    def upload_file(self, local_file, remote_file):
        """Upload a single file to remote server"""
        try:
            local_path = Path(local_file)
            if not local_path.exists():
                print(f"Error: Local file '{local_file}' does not exist")
                return False
            
            # Create remote directory if it doesn't exist
            remote_dir = str(Path(remote_file).parent)
            self.execute_command(f"mkdir -p '{remote_dir}'")
            
            self.sftp_client.put(str(local_path), remote_file)
            print(f"Uploaded: {local_path.name} -> {remote_file}")
            return True
        except Exception as e:
            print(f"Upload failed for {local_file}: {e}")
            return False
    
    def upload_files(self, local_files, remote_staging_dir):
        """Upload multiple files to remote staging directory"""
        try:
            # Create staging directory on remote server
            self.execute_command(f"mkdir -p '{remote_staging_dir}'")
            
            uploaded_files = []
            for local_file in local_files:
                local_path = Path(local_file)
                remote_file = f"{remote_staging_dir.rstrip('/')}/{local_path.name}"
                
                if self.upload_file(local_file, remote_file):
                    uploaded_files.append(remote_file)
                else:
                    print(f"Failed to upload {local_file}")
            
            print(f"Successfully uploaded {len(uploaded_files)} files to {remote_staging_dir}")
            return uploaded_files
        except Exception as e:
            print(f"Upload batch failed: {e}")
            return []
    
    def workflow_process_and_swap(self, local_folder, remote_target_dir, remote_backup_dir, 
                                  remote_staging_dir="/tmp/seg_it_staging"):
        """Complete workflow: upload local files and run remote swap operation"""
        try:
            local_path = Path(local_folder)
            if not local_path.exists():
                print(f"Error: Local folder '{local_folder}' does not exist")
                return False
            
            # Find all files in local folder
            local_files = [str(f) for f in local_path.iterdir() if f.is_file()]
            if not local_files:
                print(f"No files found in {local_folder}")
                return False
            
            print(f"Found {len(local_files)} files to process")
            
            # Upload files to staging area
            uploaded_files = self.upload_files(local_files, remote_staging_dir)
            if not uploaded_files:
                print("No files were uploaded successfully")
                return False
            
            # Upload swap.py script
            if not self.upload_script("swap.py", "/tmp/swap.py"):
                return False
            
            # Run swap operation for each uploaded file
            success_count = 0
            for remote_file in uploaded_files:
                filename = Path(remote_file).name
                print(f"\nProcessing: {filename}")
                
                output = self.remote_file_move(
                    remote_file, 
                    remote_target_dir, 
                    remote_backup_dir, 
                    upload_scripts=False  # Already uploaded
                )
                
                if output:
                    print(f"Swap result for {filename}:")
                    print(output)
                    success_count += 1
                else:
                    print(f"Failed to process {filename}")
            
            # Clean up staging area
            self.execute_command(f"rm -rf '{remote_staging_dir}'")
            print(f"\nWorkflow completed: {success_count}/{len(uploaded_files)} files processed successfully")
            return success_count > 0
            
        except Exception as e:
            print(f"Workflow failed: {e}")
            return False
    
    def list_remote_files(self, remote_path, pattern="*"):
        """List files on remote server"""
        command = f"find '{remote_path}' -name '{pattern}' -type f 2>/dev/null || ls '{remote_path}'"
        return self.execute_command(command)


def main():
    parser = argparse.ArgumentParser(
        description='Run SEG_IT utilities on remote servers via SSH'
    )
    
    # Connection arguments
    parser.add_argument('hostname', help='Remote server hostname or IP')
    parser.add_argument('username', help='SSH username')
    parser.add_argument('--port', type=int, default=22, help='SSH port (default: 22)')
    parser.add_argument('--password', help='SSH password (will prompt if not provided)')
    
    # Operation arguments
    subparsers = parser.add_subparsers(dest='operation', help='Available operations')
    
    # Serial extraction
    serial_parser = subparsers.add_parser('extract', help='Extract serial numbers from remote JPG files')
    serial_parser.add_argument('remote_path', help='Remote path to JPG file or directory')
    serial_parser.add_argument('--upload', action='store_true', help='Upload main.py script to remote server')
    
    # File move
    move_parser = subparsers.add_parser('move', help='Move files on remote server with backup')
    move_parser.add_argument('source_path', help='Remote source file/directory path')
    move_parser.add_argument('target_dir', help='Remote target directory path')
    move_parser.add_argument('backup_dir', help='Remote backup directory path')
    move_parser.add_argument('--dry-run', action='store_true', help='Show what would happen without making changes')
    move_parser.add_argument('--upload', action='store_true', help='Upload swap.py script to remote server')
    
    # List files
    list_parser = subparsers.add_parser('list', help='List files on remote server')
    list_parser.add_argument('remote_path', help='Remote directory path')
    list_parser.add_argument('--pattern', default='*', help='File pattern to match (default: *)')
    
    # Workflow - upload local files and swap remotely
    workflow_parser = subparsers.add_parser('workflow', help='Upload local files and run complete swap workflow remotely')
    workflow_parser.add_argument('local_folder', help='Local folder containing files to upload')
    workflow_parser.add_argument('remote_target_dir', help='Remote target directory')
    workflow_parser.add_argument('remote_backup_dir', help='Remote backup directory')
    workflow_parser.add_argument('--staging-dir', default='/tmp/seg_it_staging', help='Remote staging directory for uploads')
    
    args = parser.parse_args()
    
    if not args.operation:
        parser.print_help()
        return
    
    # Create remote runner
    runner = RemoteRunner(
        hostname=args.hostname,
        username=args.username,
        password=args.password,
        port=args.port
    )
    
    # Connect to remote server
    if not runner.connect():
        return
    
    try:
        # Execute requested operation
        if args.operation == 'extract':
            output = runner.remote_serial_extraction(args.remote_path, args.upload)
            if output:
                print("Serial extraction results:")
                print(output)
        
        elif args.operation == 'move':
            output = runner.remote_file_move(
                args.source_path, 
                args.target_dir, 
                args.backup_dir, 
                args.dry_run, 
                args.upload
            )
            if output:
                print("File move results:")
                print(output)
        
        elif args.operation == 'list':
            output = runner.list_remote_files(args.remote_path, args.pattern)
            if output:
                print("Remote files:")
                print(output)
        
        elif args.operation == 'workflow':
            success = runner.workflow_process_and_swap(
                args.local_folder,
                args.remote_target_dir,
                args.remote_backup_dir,
                args.staging_dir
            )
            if success:
                print("Workflow completed successfully!")
            else:
                print("Workflow failed!")
    
    finally:
        runner.disconnect()


if __name__ == "__main__":
    main()