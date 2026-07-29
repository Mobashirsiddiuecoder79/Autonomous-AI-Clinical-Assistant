import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Type, Optional
from pydantic import BaseModel
from langchain_core.tools import StructuredTool
from config.logging_config import system_logger

class BaseHealthcareTool(ABC):
    name: str
    description: str
    args_schema: Type[BaseModel]
    timeout: int = 30

    def run(self, **kwargs) -> Dict[str, Any]:
        """Wrapper method that adds timing, standard logging, and safety envelopes."""
        start_time = time.time()
        result = {"success": False, "data": None, "error": None, "duration_ms": 0.0}
        
        try:
            # 1. Parse arguments using schema
            validated_args = self.args_schema(**kwargs).model_dump()
            
            # 2. Run core execution logic
            system_logger.info(f"Executing tool {self.name} with inputs: {validated_args}")
            data = self.execute(validated_args)
            
            result["success"] = True
            result["data"] = data
        except Exception as e:
            system_logger.error(f"Error executing tool {self.name}: {e}", exc_info=True)
            result["error"] = str(e)
        finally:
            duration = (time.time() - start_time) * 1000.0
            result["duration_ms"] = duration
            system_logger.info(f"Tool {self.name} finished in {duration:.2f}ms.")
            
        return result

    @abstractmethod
    def execute(self, arguments: Dict[str, Any]) -> Any:
        """Core execution block to be implemented by child classes."""
        pass

    def to_langchain_tool(self) -> StructuredTool:
        """Converts class tool instance into a standard LangChain StructuredTool."""
        def langchain_run_wrapper(**kwargs):
            res = self.run(**kwargs)
            if res["success"]:
                return res["data"]
            return f"Error executing tool: {res['error']}"

        return StructuredTool(
            name=self.name,
            description=self.description,
            args_schema=self.args_schema,
            func=langchain_run_wrapper
        )
