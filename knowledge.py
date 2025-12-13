"""
Custom knowledge implementation for the HALO Agent Interface
"""

from pathlib import Path
from typing import Iterator, List, Optional

from agno.knowledge.document import Document
from agno.knowledge.reader.text_reader import TextReader
from agno.knowledge.knowledge import Knowledge
from agno.utils.log import logger


class HaloKnowledge(Knowledge):
    """Custom knowledge implementation for the HALO Agent Interface."""
    
    knowledge_dir: Optional[Path] = None
    formats: List[str] = [".txt", ".md"]
    reader: TextReader = TextReader()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Always set a knowledge directory
        if "uri" in kwargs:
            self.knowledge_dir = Path(kwargs["uri"]).parent / "knowledge_docs"
        else:
            # Default to a directory in the current working directory
            self.knowledge_dir = Path.cwd() / "knowledge_docs"
            
        # Ensure the directory exists
        self.knowledge_dir.mkdir(exist_ok=True, parents=True)
        logger.info(f"Using knowledge directory: {self.knowledge_dir}")
    
    @property
    def document_lists(self) -> Iterator[List[Document]]:
        """Iterate over knowledge documents and yield lists of documents."""
        if not self.knowledge_dir or not self.knowledge_dir.exists():
            logger.warning(f"Knowledge directory does not exist: {self.knowledge_dir}")
            return
            
        # Process all supported files in the knowledge directory
        for file_format in self.formats:
            for file_path in self.knowledge_dir.glob(f"*{file_format}"):
                try:
                    logger.info(f"Reading knowledge document: {file_path}")
                    documents = self.reader.read(file=file_path)
                    if documents:
                        yield documents
                    else:
                        logger.warning(f"No documents were read from file: {file_path}")
                except Exception as e:
                    logger.exception(f"Failed to read document {file_path}: {e}")
    
    def add_document(self, content: str, filename: str, metadata: Optional[dict] = None) -> bool:
        """Add a document to the knowledge base.
        
        Args:
            content: The text content of the document
            filename: The name to save the file as (will add extension if needed)
            metadata: Optional metadata to associate with the document
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.knowledge_dir:
            logger.error("Knowledge directory not set")
            return False
            
        # Ensure the filename has a supported extension
        if not any(filename.endswith(fmt) for fmt in self.formats):
            filename = f"{filename}.txt"
            
        file_path = self.knowledge_dir / filename
        
        try:
            # Write the content to the file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            # Load the document into the vector database
            documents = self.reader.read(file=file_path)
            
            if metadata:
                for doc in documents:
                    doc.meta_data.update(metadata)
            
            # Process and index the documents
            self.process_documents(
                documents=documents,
                metadata=metadata,
                upsert=True,
                skip_existing=False,
                source_info=str(file_path),
            )
            
            logger.info(f"Added document to knowledge base: {file_path}")
            return True
            
        except Exception as e:
            logger.exception(f"Failed to add document {filename}: {e}")
            return False
