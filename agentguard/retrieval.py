import os, time, requests
from abc import ABC, abstractmethod
from typing import List, Tuple
from .schemas import Policy

class BaseRetrievalProvider(ABC):
    @abstractmethod
    def retrieve(self, query: str, policies: List[Policy], settings) -> Tuple[list, float, str]:
        pass

class MossProvider(BaseRetrievalProvider):
    def retrieve(self, query: str, policies: List[Policy], settings) -> Tuple[list, float, str]:
        start = time.perf_counter()
        
        if not settings.moss_project_id or not settings.moss_project_key:
            raise ValueError("MOSS_PROJECT_ID and MOSS_PROJECT_KEY must be set to use MossProvider")
            
        try:
            import asyncio
            from moss import MossClient
            
            # Since retrieve is synchronous, we run the async Moss client in an event loop
            async def _run_moss():
                client = MossClient(
                    project_id=settings.moss_project_id,
                    project_key=settings.moss_project_key
                )
                
                # Assume the index is named "policies" for this implementation
                await client.load_index("policies")
                results = await client.query("policies", query, top_k=4)
                return results

            results = asyncio.run(_run_moss())
            
            found = []
            for h in results:
                # Map Moss hit schema to Evidence schema
                found.append({
                    "id": str(getattr(h, "id", "moss-hit")),
                    "title": getattr(h, "title", "Retrieved policy"),
                    "text": getattr(h, "text", getattr(h, "content", "")),
                    "score": float(getattr(h, "score", 0.0))
                })
            
            return found, (time.perf_counter() - start) * 1000, "moss-adapter"
            
        except ImportError:
            raise ImportError("The 'moss' library is required to use MossProvider. Install it with `pip install moss`")
        except Exception as e:
            # Fallback or pass exception up
            raise RuntimeError(f"Moss retrieval failed: {e}")

class LocalProvider(BaseRetrievalProvider):
    def retrieve(self, query: str, policies: List[Policy], settings) -> Tuple[list, float, str]:
        start = time.perf_counter()
        tokens = {t.lower().strip(".,:;!?()[]{}") for t in query.split() if len(t) > 2}
        ranked = []
        for p in policies:
            corpus = (p.title + " " + p.text + " " + " ".join(p.tags)).lower()
            words = set(corpus.replace(".", " ").replace(",", " ").split())
            score = len(tokens & words) / max(1, len(tokens))
            if score:
                ranked.append({"id": p.id, "title": p.title, "text": p.text, "score": score})
        
        found = sorted(ranked, key=lambda x: x["score"], reverse=True)[:4]
        return found, (time.perf_counter() - start) * 1000, "local-baseline"

def retrieve(query: str, policies: List[Policy], settings):
    # Hardcoded to LocalProvider for the demo to bypass Windows DLL issues
    provider = LocalProvider()
    return provider.retrieve(query, policies, settings)

