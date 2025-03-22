import subprocess
from typing import Any, Dict, Optional


def run_terminal_command(
    command: str,
    explanation: Optional[str] = None,
    is_background: bool = False,
    require_user_approval: bool = True,
) -> Dict[str, Any]:
    """
    Run a terminal command.

    Args:
        command: The terminal command to execute
        explanation: Optional explanation of why this command needs to be run
        is_background: Whether the command should be run in the background
        require_user_approval: Whether the user must approve the command before execution

    Returns:
        Dict containing the output of the command
    """
    try:
        # For safety, we'll add a check to prevent destructive commands
        dangerous_commands = ["rm -rf", "sudo rm", "dd", "mkfs", "format", ":(){:|:&};:"]

        for dangerous in dangerous_commands:
            if dangerous in command:
                return {
                    "error": f"Command '{command}' contains potentially dangerous operation '{dangerous}'. Execution aborted."
                }

        # If the command is to be run in the background, add & at the end
        if is_background and not command.strip().endswith("&"):
            command = f"{command} &"

        # If this is a command that would require a pager, we'll append | cat
        pager_commands = ["less", "more", "git diff", "git show", "head", "tail"]
        for pager in pager_commands:
            if command.startswith(pager) or f" {pager} " in command:
                if " | cat" not in command:
                    command = f"{command} | cat"

        # Run the command
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True
        )

        stdout, stderr = process.communicate()

        # Prepare the output
        result = {
            "command": command,
            "exit_code": process.returncode,
            "stdout": stdout,
            "stderr": stderr,
        }

        if process.returncode != 0:
            result["error"] = f"Command failed with exit code {process.returncode}"

        return result

    except Exception as e:
        return {"error": str(e)}
