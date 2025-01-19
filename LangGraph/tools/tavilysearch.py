from langchain_community.tools import TavilySearchResults
class MonitoredTavilySearch(TavilySearchResults):
    def __call__(self, *args, **kwargs):
        print(f"\n[Search Tool] 搜索: {args[0] if args else kwargs.get('query', '')}")
        result = super().__call__(*args, **kwargs)
        print(f"[Search Tool] 找到结果")
        return result