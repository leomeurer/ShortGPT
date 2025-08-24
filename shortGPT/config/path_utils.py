import os
import platform
import sys
import subprocess
import tempfile
import hashlib
def search_program(program_name):
    try: 
        search_cmd = "where" if platform.system() == "Windows" else "which"
        return subprocess.check_output([search_cmd, program_name]).decode().strip()
    except subprocess.CalledProcessError:
        return None

def get_program_path(program_name):
    program_path = search_program(program_name)
    return program_path

def is_running_in_colab():
    return 'COLAB_GPU' in os.environ

def handle_path(path, extension = ".mp4"):
    # Sempre baixar recursos de URLs 
    if 'https' in path or 'http' in path:
        # Criar diretório de cache se não existir
        cache_dir = ".editing_assets/cached_media/"
        os.makedirs(cache_dir, exist_ok=True)
        
        # Gerar nome único baseado na URL
        url_hash = hashlib.md5(path.encode()).hexdigest()[:8]
        cached_file = os.path.join(cache_dir, f"{url_hash}{extension}")
        
        # Se já existe em cache, reutilizar
        if os.path.exists(cached_file):
            return cached_file      

        timeout_seconds = 300
        
        try:
            command = ['ffmpeg', '-y', '-i', path, '-c', 'copy', cached_file]
            result = subprocess.run(command, capture_output=True, text=True, timeout=timeout_seconds)
            
            if result.returncode != 0:
                stderr = result.stderr.lower()
                raise subprocess.CalledProcessError(result.returncode, command, result.stderr)
            
            # Verificar se o arquivo foi criado com sucesso
            if not os.path.exists(cached_file) or os.path.getsize(cached_file) == 0:
                if os.path.exists(cached_file):
                    os.remove(cached_file)
                raise Exception(f"Failed to download file (empty or not created): {path}")
            
            return cached_file
            
        except subprocess.TimeoutExpired:
            # Limpar arquivo parcial em caso de timeout
            if os.path.exists(cached_file):
                os.remove(cached_file)
            timeout_minutes = timeout_seconds / 60
            raise Exception(f"Timeout downloading after {timeout_minutes} minutes: {path[:100]}...")
        except subprocess.CalledProcessError as e:
            # Limpar arquivo parcial em caso de erro
            if os.path.exists(cached_file):
                os.remove(cached_file)
            raise Exception(f"Failed to download {path}: {e.stderr}")
    
    return path