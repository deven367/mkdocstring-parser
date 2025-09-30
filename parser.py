import re
from typing import Any, Dict, Optional

import griffe
import yaml
from griffe2md import ConfigDict, render_object_docs
from rich.console import Console
from rich.markdown import Markdown


class MkDocstringsParser:
    def __init__(self):
        pass
        
    def parse_docstring_block(self, block_content: str) -> tuple[str, str, Dict[str, Any]]:
        """Parse a ::: block to extract module path, handler, and options"""
        lines = block_content.strip().split('\n')
        
        # First line contains the module path
        module_path = lines[0].replace(':::', '').strip()
        
        # Parse YAML configuration
        yaml_content = '\n'.join(lines[1:]) if len(lines) > 1 else ''
        
        try:
            config = yaml.safe_load(yaml_content) or {}
        except yaml.YAMLError:
            config = {}
        
        handler_type = config.get('handler', 'python')
        options = config.get('options', {})
        
        return module_path, handler_type, options
        
    def generate_documentation(self, module_path: str, options: Dict[str, Any]) -> str:
        """Generate documentation for a given module using griffe and griffe2md"""
        try:
            # Parse the module path to extract package and object path
            if '.' in module_path:
                parts = module_path.split('.')
                package_name = parts[0]
                object_path = '.'.join(parts[1:])
            else:
                package_name = module_path
                object_path = ""
            
            # Load the package with griffe
            package = griffe.load(package_name)
            to_replace = '.'.join((package_name + '.' + object_path).split('.')[:-1])
            # Get the specific object if path is provided
            if object_path:
                obj = package[object_path]
            else:
                obj = package
            
            # Ensure the docstring is properly parsed with Google parser
            if obj.docstring:
                # Force parsing with Google parser to get structured sections
                obj.docstring.parsed = griffe.parse_google(obj.docstring)
            
            # Also parse docstrings for all methods/functions if this is a class
            if hasattr(obj, 'members'):
                for member_name, member in obj.members.items():
                    if member.docstring:
                        member.docstring.parsed = griffe.parse_google(member.docstring)
            
            # Create ConfigDict with the options
            # Ensure docstring_section_style is set to "list" for bullet points
            default_options = {
                'docstring_section_style': 'table',
                'heading_level': 3,
                'show_root_heading': True,
                'show_source': True,
                'show_docstring_functions':False
            }
            default_options.update(options)
            config = ConfigDict(**default_options)
            
            # Generate the documentation using griffe2md
            markdown_docs = render_object_docs(obj, config)
            
            markdown_docs = markdown_docs.replace(f"### `{to_replace}.", "### `")
            
            return markdown_docs
            
        except Exception as e:
            return f"<!-- Error generating docs for {module_path}: {str(e)} -->"
    
    def process_markdown(self, content: str) -> str:
        """Process markdown content, replacing ::: blocks with generated documentation"""
        
        # Pattern to match ::: blocks (including multi-line YAML config)
        pattern = r':::\s*([^\n]+)(?:\n((?:\s{4}.*\n?)*))?'
        
        def replace_block(match):
            module_line = match.group(1).strip()
            yaml_block = match.group(2) or ''
            
            # Reconstruct the full block
            full_block = f":::{module_line}\n{yaml_block}".rstrip()
            
            try:
                module_path, handler_type, options = self.parse_docstring_block(full_block)
                generated_docs = self.generate_documentation(module_path, options)
                return generated_docs
            except Exception as e:
                return f"<!-- Error processing block: {str(e)} -->"
        
        return re.sub(pattern, replace_block, content, flags=re.MULTILINE)
    
    def process_file(self, input_file: str, output_file: Optional[str] = None) -> str:
        """Process a markdown file and return the result"""
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        processed_content = self.process_markdown(content)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(processed_content)
        
        return processed_content

# Usage example
if __name__ == "__main__":
    parser = MkDocstringsParser()
    
    # Example usage
    # sample_content = open("models.md").read()
    
    result = parser.process_file("test.md")
    print(result)
    # console = Console()
    # console.print(Markdown(result))