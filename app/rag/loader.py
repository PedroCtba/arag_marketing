from pathlib import Path
from typing import List, Dict, Any

class MarketingDataLoader:
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
    
    def load_campaign_data(self, campaign_name: str = None) -> List[Dict[str, Any]]:
        """
        Load marketing data from markdown files
        Returns list of documents with metadata
        """
        documents = []
        search_dir = self.data_dir / campaign_name if campaign_name else self.data_dir
        
        # Walk through the directory
        for markdown_file in search_dir.rglob('*.md'):
            if markdown_file.name == 'index.md':  # Skip index file
                continue
                
            try:
                with open(markdown_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                documents.append({
                    'content': content,
                    'metadata': {
                        'file_path': str(markdown_file.relative_to(self.data_dir))
                    }
                })
            except Exception as e:
                print(f"Error loading {markdown_file}: {str(e)}")
        
        return documents 
