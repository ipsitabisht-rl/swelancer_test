from nanoeval.solvers.computer_tasks.code_execution_interface import ComputerInterface, ExecutionResult
import subprocess
import os

class LocalComputerInterface(ComputerInterface):
    def __init__(self, base_dir: str = "/testbed"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    async def send_shell_command(self, cmd: str) -> ExecutionResult:
        # Run the command in the base_dir
        proc = subprocess.run(cmd, shell=True, cwd=self.base_dir, capture_output=True)
        return ExecutionResult(output=proc.stdout + proc.stderr, exit_code=proc.returncode)

    async def upload(self, file: bytes, destination: str) -> None:
        dest_path = os.path.join(self.base_dir, destination.lstrip("/"))
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        with open(dest_path, "wb") as f:
            f.write(file)

    async def download(self, file: str) -> bytes:
        file_path = os.path.join(self.base_dir, file.lstrip("/"))
        with open(file_path, "rb") as f:
            return f.read()

    async def stop(self) -> None:
        # Optionally clean up files or environment
        pass