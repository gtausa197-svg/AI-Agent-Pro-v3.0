"""
Bridge to connect FastAPI with existing AI Agent core
"""
import sys
from pathlib import Path

# Add parent directory to path to import ai_agent modules
# Path: backend/api/utils/agent_bridge.py -> need to go up 3 levels to reach ai_local_agent/
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from ai_agent import AgentDatabase, LMStudioClient, Config
    import psutil
    import platform
    from datetime import datetime
except ImportError as e:
    print(f"Error importing AI Agent modules: {e}")
    raise


class AgentBridge:
    """Bridge class to interact with AI Agent core"""
    
    def __init__(self):
        self.db = AgentDatabase()
        self.llm_client = LMStudioClient(db=self.db)
        self.config = Config
    
    def get_system_info(self):
        """Get system information"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu": {
                    "percent": cpu_percent,
                    "count": psutil.cpu_count(),
                    "freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": disk.percent
                },
                "system": {
                    "platform": platform.system(),
                    "platform_version": platform.version(),
                    "architecture": platform.machine(),
                    "processor": platform.processor(),
                    "hostname": platform.node()
                },
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_processes(self, limit=20):
        """Get running processes"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
            return processes[:limit]
        except Exception as e:
            return {"error": str(e)}
    
    def execute_command(self, command: str):
        """Execute command through LLM client"""
        try:
            response = self.llm_client.send_message(command)
            
            # Log to database
            self.db.log_command(
                command=command,
                result=response[:500] if response else "No response",
                success=bool(response),
                execution_time=0.0
            )
            
            return {
                "success": True,
                "command": command,
                "response": response,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "command": command,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_command_history(self, limit=50):
        """Get command history from database"""
        try:
            history = self.db.get_command_history(limit=limit)
            return [
                {
                    "command": h[0],
                    "result": h[1][:200] if h[1] else "",  # Truncate for API
                    "success": bool(h[2]),
                    "execution_time": h[3],
                    "timestamp": h[4]
                }
                for h in history
            ]
        except Exception as e:
            return {"error": str(e)}
    
    def search_files(self, pattern: str, directory: str = None, limit=100):
        """Search for files"""
        try:
            from pathlib import Path
            import fnmatch
            
            search_dir = Path(directory) if directory else Path.home()
            results = []
            
            for file_path in search_dir.rglob(pattern):
                if len(results) >= limit:
                    break
                if file_path.is_file():
                    try:
                        stat = file_path.stat()
                        results.append({
                            "path": str(file_path),
                            "name": file_path.name,
                            "size": stat.st_size,
                            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                        })
                    except:
                        pass
            
            return results
        except Exception as e:
            return {"error": str(e)}


# Global instance
agent_bridge = AgentBridge()
