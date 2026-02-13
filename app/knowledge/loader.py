"""知识库文档加载器 — 从指定目录扫描并导入文档到向量库"""

from pathlib import Path

from loguru import logger

from app.config import settings
from app.knowledge import company_knowledge


async def load_knowledge(*, recreate: bool = False) -> None:
    """加载企业文档到向量库

    Args:
        recreate: 是否全量重建（清空后重新导入）
    """
    docs_dir = Path(settings.KNOWLEDGE_DIR)
    if not docs_dir.exists():
        logger.warning("知识库文档目录不存在: {}", docs_dir)
        docs_dir.mkdir(parents=True, exist_ok=True)
        return

    doc_files = list(docs_dir.glob("*.md")) + list(docs_dir.glob("*.pdf"))
    if not doc_files:
        logger.info("知识库文档目录为空，跳过加载")
        return

    logger.info("开始加载知识库文档，共 {} 个文件，recreate={}", len(doc_files), recreate)

    for doc_file in doc_files:
        try:
            company_knowledge.insert(path=str(doc_file), skip_if_exists=not recreate)
            logger.info("已加载文档: {}", doc_file.name)
        except Exception:
            logger.exception("加载文档失败: {}", doc_file.name)

    logger.info("知识库文档加载完成")
