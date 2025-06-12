from typing import List, Dict

class Memory:
    def __init__(self):
        self.items: List[Dict] = []  # working memory 暫存區

    def add_memory(self, memory: Dict):
        """
        加入一則記憶（通常是一次對話或分析紀錄）
        """
        self.items.append(memory)

    def get_memories(self, limit: int = None) -> List[Dict]:
        """
        取得最後 N 則記憶，作為 prompt 或 context 使用
        """
        if limit:
            return self.items[-limit:]
        return self.items

    def clear(self):
        """
        清除所有記憶（例如開始新任務或使用者重設）
        """
        self.items = []

    def __repr__(self):
        return f"<Memory with {len(self.items)} items>"