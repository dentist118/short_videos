from utils.gemini import generate_content
from config import OUTPUT_DIR
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_script(topic=None):
    """Generate video script content in Markdown format with duration control"""
    try:
        if not topic:
            topic = input("أدخل موضوع الفيديو: ")
        
        logging.info(f"بدء إنشاء النص للموضوع: {topic}")
        
        # Generate content with strict constraints
        prompt = f"""أنشئ محتوى مكتوبًا بتنسيق ماركداون (MD) بالعربية الفصحى عن: {topic}
المتطلبات:
- عنوان رئيسي جذاب (H1)
- عنوانين فرعيين فقط (H2)
- فقرات قصيرة تحت كل عنوان فرعي (لا تزيد عن 3 جمل)
- استخدام النقاط عند اللزوم (لا تزيد عن 3 نقاط)
- باللغة العربية فقط
- لا يحتوي على أي كلمات إنجليزية
- بدون أرقام أو رموز غير ضرورية
- مناسب لمقطع يوتيوب قصير لا يتجاوز 50 ثانية
- إجمالي عدد الكلمات لا يزيد عن 120 كلمة

مثال:
# أهمية الرياضة اليومية

## فوائد الرياضة البدنية
ممارسة الرياضة بانتظام تعزز صحة القلب...
* تحسين الدورة الدموية
* زيادة مرونة العضلات

## الفوائد النفسية
الرياضة تساعد على تخفيف التوتر...
* تحسين المزاج
* زيادة التركيز
"""
        content = generate_content(prompt)
        
        # Validate word count
        content_words = [w for w in content.split() if w.strip()]
        word_count = len(content_words)
        if word_count > 120:
            logging.warning(f"عدد الكلمات ({word_count}) يتجاوز الحد الموصى به (120 كلمة)، قد يتجاوز الفيديو 50 ثانية")
        
        # Add metadata
        md_content = f"""---
title: {topic}
date: {datetime.now().strftime('%Y-%m-%d')}
lang: ar
word_count: {word_count}
---

{content}
"""
        # Save markdown
        script_path = OUTPUT_DIR / "script.md"
        script_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        # Create processed versions
        create_line_by_line(script_path)
        create_plain_text_version(script_path)
        
        logging.info(f"تم حفظ النص في: {script_path}")
        return script_path
        
    except Exception as e:
        logging.error(f"فشل إنشاء النص: {str(e)}")
        raise

def create_line_by_line(md_path):
    """Create duration-controlled line-by-line version"""
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Remove metadata and markdown
        sentences = []
        for line in text.split('\n'):
            line = line.strip()
            if line and not line.startswith(('---', 'title:', 'date:', 'lang:', 'word_count:')):
                # Remove markdown syntax
                clean_line = line.replace('#', '').replace('*', '').replace('-', '').strip()
                # Split into sentences
                for sentence in clean_line.split('.'):
                    sentence = sentence.strip()
                    if sentence:
                        sentences.append(sentence)
        
        # Duration control calculations
        max_seconds = 50
        avg_words_per_second = 2.33  # 140 words/minute
        max_words = int(max_seconds * avg_words_per_second)  # ~116 words
        
        selected_sentences = []
        word_count = 0
        
        # Select sentences within limit
        for sentence in sentences:
            sentence_words = len(sentence.split())
            if (word_count + sentence_words) > max_words:
                break
            selected_sentences.append(sentence)
            word_count += sentence_words
        
        # Save truncated version
        line_path = OUTPUT_DIR / "line_by_line.txt"
        with open(line_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(selected_sentences))
        
        logging.info(f"تم إنشاء النسخة السطرية مع {word_count} كلمة (~{round(word_count/avg_words_per_second)} ثانية)")
        return line_path
        
    except Exception as e:
        logging.error(f"فشل إنشاء النسخة السطرية: {str(e)}")
        raise

def create_plain_text_version(md_path):
    """Create basic plain text version"""
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        lines = []
        for line in text.split('\n'):
            if line.startswith('---'):
                continue
            line = line.lstrip('#').strip()
            line = line.lstrip('*- ').strip()
            if line and not line.startswith(('title:', 'date:', 'lang:', 'word_count:')):
                lines.append(line)
        
        txt_path = OUTPUT_DIR / "plain_text.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        return txt_path
        
    except Exception as e:
        logging.error(f"فشل إنشاء النسخة النصية: {str(e)}")
        raise
