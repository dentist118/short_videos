from utils.gemini import generate_content
from config import OUTPUT_DIR
import logging
from pathlib import Path
from datetime import datetime

def generate_script(topic=None):
    """Generate script content in Markdown format using Gemini API
    
    Args:
        topic (str, optional): The video topic. If not provided, prompts user.
        
    Returns:
        Path: Path to the generated markdown file
        
    Raises:
        Exception: If script generation fails
    """
    try:
        if not topic:
            topic = input("أدخل موضوع الفيديو: ")
        
        logging.info(f"Generating script for topic: {topic}")
        
        # Generate markdown content using Gemini
        prompt = f"""أنشئ محتوى مكتوبًا بتنسيق ماركداون (MD) بالعربية الفصحى عن: {topic}
المتطلبات:
- عنوان رئيسي جذاب (H1)
- 3 عناوين فرعية (H2)
- فقرات تحت كل عنوان فرعي
- استخدام النقاط عند اللزوم
- باللغة العربية فقط
- لا يحتوي على أي كلمات إنجليزية
- بدون أرقام أو رموز غير ضرورية
- مناسب لمقطع يوتيوب قصير

مثال:
# أهمية الكهرباء في حياتنا

## مقدمة عن الكهرباء
الكهرباء من أهم الاختراعات...
* تسهيل الحياة اليومية
* تحسين جودة الحياة

## استخدامات الكهرباء
تستخدم الكهرباء في...
"""
        content = generate_content(prompt)
        
        # Add metadata to the markdown
        md_content = f"""---
title: {topic}
date: {datetime.now().strftime('%Y-%m-%d')}
lang: ar
---

{content}
"""
        # Save to markdown file
        script_path = OUTPUT_DIR / "script.md"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        # Create processed versions
        create_line_by_line(script_path)
        create_plain_text_version(script_path)
        
        return script_path
        
    except Exception as e:
        logging.error(f"Failed to generate script: {str(e)}")
        raise

def create_line_by_line(md_path):
    """Create a line-by-line version of the script from markdown
    
    Args:
        md_path (Path): Path to the markdown file
        
    Returns:
        Path: Path to the line-by-line text file
        
    Raises:
        Exception: If processing fails
    """
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Remove markdown syntax
        text = text.replace('#', '').replace('*', '').replace('-', '')
        
        # Split into sentences
        sentences = []
        for line in text.split('\n'):
            line = line.strip()
            if line and not line.startswith(('---', 'title:', 'date:', 'lang:')):
                for sentence in line.split('.'):
                    sentence = sentence.strip()
                    if sentence:
                        sentences.append(sentence)
        
        # Save line-by-line version
        line_path = OUTPUT_DIR / "line_by_line.txt"
        with open(line_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sentences))
            
        return line_path
        
    except Exception as e:
        logging.error(f"Failed to create line-by-line version: {str(e)}")
        raise

def create_plain_text_version(md_path):
    """Create a plain text version from markdown
    
    Args:
        md_path (Path): Path to the markdown file
        
    Returns:
        Path: Path to the plain text file
    """
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Basic markdown to plain text conversion
        lines = []
        for line in text.split('\n'):
            if line.startswith('---'):
                continue
            # Remove markdown headers
            line = line.lstrip('#').strip()
            # Remove list markers
            line = line.lstrip('*- ').strip()
            if line:
                lines.append(line)
        
        plain_text = '\n'.join(lines)
        txt_path = OUTPUT_DIR / "plain_text.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(plain_text)
            
        return txt_path
        
    except Exception as e:
        logging.error(f"Failed to create plain text version: {str(e)}")
        raise
