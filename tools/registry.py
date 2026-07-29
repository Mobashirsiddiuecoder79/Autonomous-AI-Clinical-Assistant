from typing import Dict, Any, List, Optional
from tools.base import BaseHealthcareTool
from langchain_core.tools import StructuredTool

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseHealthcareTool] = {}

    def register(self, tool: BaseHealthcareTool) -> None:
        """Adds a healthcare tool instance to the registry."""
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[BaseHealthcareTool]:
        """Fetch a specific tool instance by name."""
        return self._tools.get(name)

    def list_tools(self) -> List[BaseHealthcareTool]:
        """Returns all registered tool classes."""
        return list(self._tools.values())

    def get_langchain_tools(self) -> List[StructuredTool]:
        """Helper to get list of registered tools pre-wrapped for LangChain consumption."""
        return [tool.to_langchain_tool() for tool in self._tools.values()]

    def rank_tools(self, query: str) -> List[BaseHealthcareTool]:
        """
        Ranks tools based on query token overlap with name/description.
        Helps prune search context or guide agent selection.
        """
        if not query:
            return self.list_tools()
            
        ranked = []
        query_words = set(query.lower().split())
        
        for tool in self._tools.values():
            score = 0
            text_pool = f"{tool.name} {tool.description}".lower()
            for word in query_words:
                if word in text_pool:
                    score += 1
            ranked.append((score, tool))
            
        # Sort descending by score
        ranked.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in ranked]

# Singleton registry instance for global sharing
tool_registry = ToolRegistry()
