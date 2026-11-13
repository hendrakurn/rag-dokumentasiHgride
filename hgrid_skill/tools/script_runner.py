"""Tool untuk menjalankan script di sistem."""
import subprocess
from langchain_core.tools import tool


@tool
def run_shell_command(command: str) -> str:
    """
    Jalankan shell command di sistem.
    PERINGATAN: Hanya gunakan untuk perintah yang aman (read-only atau
    perintah yang sudah dikonfirmasi user). Jangan jalankan perintah destruktif
    tanpa konfirmasi.
    
    Args:
        command: Shell command yang akan dijalankan
    
    Returns:
        Output dari command (stdout + stderr)
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60,
        )
        output = result.stdout
        if result.stderr:
            output += f"\n[STDERR]: {result.stderr}"
        if result.returncode != 0:
            output += f"\n[EXIT CODE]: {result.returncode}"
        return output or "(tidak ada output)"
    except subprocess.TimeoutExpired:
        return "[ERROR] Command timeout setelah 60 detik"
    except Exception as e:
        return f"[ERROR] {str(e)}"


@tool
def run_hgrid_script(script_content: str) -> str:
    """
    Jalankan shell script untuk HGrid247. Biasanya berisi perintah spark-submit
    atau hadoop jar untuk menjalankan workflow.
    
    Contoh script:
        #!/bin/bash
        spark-submit --class workshop.Lab03 workshop.jar input output
    
    Args:
        script_content: Isi script yang akan dieksekusi
    
    Returns:
        Output eksekusi script
    """
    try:
        result = subprocess.run(
            ["bash", "-c", script_content],
            capture_output=True,
            text=True,
            timeout=300,
        )
        output = f"Script selesai dieksekusi.\n\nOutput:\n{result.stdout}"
        if result.stderr:
            output += f"\nWarnings/Errors:\n{result.stderr}"
        return output
    except subprocess.TimeoutExpired:
        return "[ERROR] Script timeout setelah 5 menit"
    except Exception as e:
        return f"[ERROR] Gagal menjalankan script: {str(e)}"
