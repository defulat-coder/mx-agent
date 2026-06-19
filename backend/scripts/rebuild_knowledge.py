"""全量重建知识库向量索引"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.knowledge.loader import load_knowledge  # noqa: E402


async def main() -> None:
    print("开始全量重建知识库...")
    await load_knowledge(recreate=True)
    print("知识库重建完成")


if __name__ == "__main__":
    asyncio.run(main())
