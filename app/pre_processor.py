import os
from pathlib import Path
from typing import List, Dict
from docx import Document
from tqdm import tqdm

class DataPreProcessor:
    def __init__(self, raw_data_dir: str, processed_data_dir: str):
        self.raw_data_dir = Path(raw_data_dir)
        self.processed_data_dir = Path(processed_data_dir)
    
    def clean_title(self, title: str) -> str:
        """Clean and format title from folder/file name"""
        # Remove file extension if present
        title = os.path.splitext(title)[0]
        
        # Remove numeric prefixes (e.g., "3. ", "1- ", etc.)
        title = ' '.join(title.split('.')[1:]) if '.' in title else title
        title = ' '.join(title.split('-')[1:]) if '-' in title and title.split('-')[0].strip().isdigit() else title
        
        # Replace remaining underscores and hyphens with spaces
        title = title.replace('_', ' ').replace('-', ' ')
        
        # Remove extra whitespace and strip
        title = ' '.join(word for word in title.split() if word)
        
        # Capitalize words
        return ' '.join(word.capitalize() for word in title.split())
    
    def get_hierarchy_title(self, file_path: Path) -> str:
        """Generate title based on folder hierarchy"""
        relative_path = file_path.relative_to(self.raw_data_dir)
        parts = list(relative_path.parts[:-1])  # Exclude filename
        if parts:
            return ' > '.join(self.clean_title(part) for part in parts)
        return "General"
    
    def docx_to_markdown(self, docx_path: Path) -> str:
        """Convert DOCX content to markdown format"""
        try:
            # Try opening with python-docx
            doc = Document(str(docx_path))  # Convert Path to string explicitly
            markdown_content = []
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    # Handle different heading levels
                    if paragraph.style.name.startswith('Heading'):
                        level = paragraph.style.name[-1]  # Get heading level
                        markdown_content.append(f"{'#' * int(level)} {paragraph.text}\n")
                    else:
                        # Handle text formatting
                        text = paragraph.text
                        if paragraph.runs:
                            for run in paragraph.runs:
                                if run.bold:
                                    text = text.replace(run.text, f"**{run.text}**")
                                if run.italic:
                                    text = text.replace(run.text, f"*{run.text}*")
                        
                        markdown_content.append(f"{text}\n")
            
            # Add extra newline between paragraphs
            return "\n".join(markdown_content)
        
        except Exception as e:
            # Fallback: Try reading as plain text
            try:
                with open(docx_path, 'r', encoding='utf-8', errors='ignore') as f:

                    content = f.read()
                    return content
                
            except Exception as e2:
                raise Exception(f"Failed to process file: {str(e)} and fallback also failed: {str(e2)}")
    
    def process_file(self, file_path: Path) -> Dict[str, str]:
        """Process individual file and convert to markdown"""
        hierarchy_title = self.get_hierarchy_title(file_path)
        file_title = self.clean_title(file_path.name)
        
        if file_path.suffix.lower() == '.docx':
            try:
                # Convert DOCX to markdown
                markdown_content = self.docx_to_markdown(file_path)
                
                # Add metadata as YAML frontmatter
                processed_content = f"""---
title: {file_title}
category: {hierarchy_title}
source_file: {file_path.name}
source_path: {str(file_path.relative_to(self.raw_data_dir))}
---

{markdown_content}
"""
                return {
                    'content': processed_content,
                    'title': file_title,
                    'category': hierarchy_title
                }
            
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")
                return None
        
        return None
    
    def process_directory(self):
        """Process all files in the raw data directory"""
        # Create processed directory if it doesn't exist
        self.processed_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Get all files recursively
        all_files = list(self.raw_data_dir.rglob('*'))
        files_to_process = [f for f in all_files if f.is_file() and f.suffix.lower() == '.docx']
        
        processed_files = []
        
        for file_path in tqdm(files_to_process, desc="Processing files"):
            result = self.process_file(file_path)
            if result:
                # Create category-based directory structure
                category_path = self.processed_data_dir / result['category'].replace(' > ', '/')
                category_path.mkdir(parents=True, exist_ok=True)
                
                # Save as markdown file
                output_path = category_path / f"{result['title']}.md"
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(result['content'])
                
                processed_files.append({
                    'original_path': str(file_path),
                    'processed_path': str(output_path),
                    'category': result['category'],
                    'title': result['title']
                })
        
        # Create index file
        self._create_index_file(processed_files)
        
        return processed_files
    
    def _create_index_file(self, processed_files: List[Dict[str, str]]):
        """Create an index file with links to all processed documents"""
        index_content = "# Marketing Content Index\n\n"
        
        # Group by category
        categories = {}
        for file in processed_files:
            if file['category'] not in categories:
                categories[file['category']] = []
            categories[file['category']].append(file)
        
        # Create index content
        for category, files in sorted(categories.items()):
            index_content += f"\n## {category}\n\n"
            for file in sorted(files, key=lambda x: x['title']):
                relative_path = os.path.relpath(
                    file['processed_path'], 
                    str(self.processed_data_dir)
                )
                index_content += f"- [{file['title']}]({relative_path})\n"
        
        # Save index file
        with open(self.processed_data_dir / 'index.md', 'w', encoding='utf-8') as f:
            f.write(index_content)

def main():
    # Initialize preprocessor
    preprocessor = DataPreProcessor(
        raw_data_dir="data/raw",
        processed_data_dir="data/processed"
    )
    
    # Process all files
    processed_files = preprocessor.process_directory()
    
    print(f"\nProcessed {len(processed_files)} files")
    print(f"Results saved in {preprocessor.processed_data_dir}")

if __name__ == "__main__":
    main()
