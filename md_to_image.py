from PIL import Image, ImageDraw, ImageFont
import textwrap

def markdown_to_image(md_content, output_path='workflow.png', width=1200):
    """
    Convert markdown content to an image
    
    Args:
        md_content: String containing markdown text
        output_path: Output file path for the image
        width: Width of the output image in pixels
    """
    
    # Parse markdown content
    lines = md_content.split('\n')
    
    # Styling configuration
    font_sizes = {
        'h1': 36,
        'h2': 28,
        'h3': 22,
        'normal': 18,
        'list': 16
    }
    
    colors = {
        'h1': (0, 102, 204),      # Blue
        'h2': (51, 51, 51),        # Dark gray
        'h3': (102, 102, 102),     # Medium gray
        'normal': (51, 51, 51),    # Dark gray
        'bullet': (0, 153, 76)     # Green
    }
    
    # Calculate required height
    y_position = 40
    line_data = []
    
    for line in lines:
        if not line.strip():
            y_position += 20
            line_data.append(('space', None, y_position))
            continue
            
        if line.startswith('# '):
            text = line[2:].strip()
            line_data.append(('h1', text, y_position))
            y_position += font_sizes['h1'] + 30
            
        elif line.startswith('## '):
            text = line[3:].strip()
            line_data.append(('h2', text, y_position))
            y_position += font_sizes['h2'] + 25
            
        elif line.startswith('### '):
            text = line[4:].strip()
            line_data.append(('h3', text, y_position))
            y_position += font_sizes['h3'] + 20
            
        elif line.strip().startswith('- ') or line.strip().startswith('* '):
            text = line.strip()[2:]
            # Word wrap for list items
            wrapped = textwrap.wrap(text, width=80)
            for i, wrapped_line in enumerate(wrapped):
                indent = 60 if i > 0 else 40
                line_data.append(('list', wrapped_line, y_position, indent))
                y_position += font_sizes['list'] + 8
            y_position += 5
            
        elif line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')):
            # Numbered list
            parts = line.strip().split('.', 1)
            if len(parts) == 2:
                num = parts[0].strip()
                text = parts[1].strip()
                wrapped = textwrap.wrap(text, width=75)
                for i, wrapped_line in enumerate(wrapped):
                    if i == 0:
                        line_data.append(('numbered', f"{num}. {wrapped_line}", y_position, 40))
                    else:
                        line_data.append(('numbered', wrapped_line, y_position, 70))
                    y_position += font_sizes['list'] + 8
                y_position += 5
                
        elif line.startswith('**') or line.startswith('→'):
            text = line.strip()
            line_data.append(('bold', text, y_position))
            y_position += font_sizes['normal'] + 15
            
        elif line.strip():
            # Regular text with word wrap
            wrapped = textwrap.wrap(line.strip(), width=90)
            for wrapped_line in wrapped:
                line_data.append(('normal', wrapped_line, y_position))
                y_position += font_sizes['normal'] + 10
    
    # Add padding
    height = y_position + 40
    
    # Create image
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use default font (will fallback if not available)
    try:
        fonts = {
            'h1': ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', font_sizes['h1']),
            'h2': ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', font_sizes['h2']),
            'h3': ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', font_sizes['h3']),
            'normal': ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', font_sizes['normal']),
            'list': ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', font_sizes['list'])
        }
    except:
        # Fallback to default font
        fonts = {
            'h1': ImageFont.load_default(),
            'h2': ImageFont.load_default(),
            'h3': ImageFont.load_default(),
            'normal': ImageFont.load_default(),
            'list': ImageFont.load_default()
        }
    
    # Draw content
    for item in line_data:
        if item[0] == 'space':
            continue
            
        line_type = item[0]
        text = item[1] if len(item) > 1 else None
        y = item[2] if len(item) > 2 else 0
        
        if text is None:
            continue
        
        if line_type == 'h1':
            draw.text((40, y), text, fill=colors['h1'], font=fonts['h1'])
            # Add underline
            draw.line([(40, y + font_sizes['h1'] + 5), (width - 40, y + font_sizes['h1'] + 5)], 
                     fill=colors['h1'], width=3)
            
        elif line_type == 'h2':
            draw.text((40, y), text, fill=colors['h2'], font=fonts['h2'])
            
        elif line_type == 'h3':
            draw.text((40, y), text, fill=colors['h3'], font=fonts['h3'])
            
        elif line_type == 'list':
            indent = item[3] if len(item) > 3 else 40
            # Draw bullet point
            if indent == 40:
                draw.ellipse([indent - 15, y + 5, indent - 8, y + 12], fill=colors['bullet'])
            draw.text((indent, y), text, fill=colors['normal'], font=fonts['list'])
            
        elif line_type == 'numbered':
            indent = item[3] if len(item) > 3 else 40
            draw.text((indent, y), text, fill=colors['normal'], font=fonts['list'])
            
        elif line_type == 'bold':
            text = text.replace('**', '').replace('→', '→')
            draw.text((40, y), text, fill=colors['h2'], font=fonts['normal'])
            
        else:  # normal
            draw.text((40, y), text, fill=colors['normal'], font=fonts['normal'])
    
    # Save image
    img.save(output_path, quality=95)
    print(f"Image saved to: {output_path}")
    return output_path


# Example usage with the BOM workflow
md_content = """# BOM Generation Workflow

## Process Flow

**Start** →

1. **Product & Test Requirements**
   - Initial input stage for product specifications and test requirements

2. **Requirement Normalization**
   - Standardize and normalize incoming requirements

3. **Historical Test Station Data**
   - Access historical data from test stations
   - ↑ Feedback from Feedback Loop

4. **Similarity Search & Matching**
   - Match current requirements with historical data

5. **Candidate BOM Extraction**
   - Extract potential BOM candidates based on matches

6. **Rule Engine (Eng Constraints)**
   - Apply engineering constraints and business rules

7. **GenAI Inference & Explanation**
   - Use AI to generate recommendations and explanations

8. **Confidence-Scored Test Station BOM**
   - Generate BOM with confidence scores

9. **Engineer Review & Override**
   - Human-in-the-loop review and approval stage
   - Engineers can override AI recommendations

10. **Feedback Loop**
    - Captures engineer decisions and feeds back to Historical Test Station Data
    - Enables continuous improvement

11. **Approved BOM**
    - Final approved Bill of Materials

→ **End**

## Key Features

- **Feedback Mechanism**: Engineer decisions loop back to improve Historical Test Station Data
- **AI-Assisted**: GenAI provides inference and explanations for recommendations
- **Human Oversight**: Engineers review and can override AI suggestions
- **Rule-Based Validation**: Engineering constraints ensure technical feasibility"""

# Convert to image
if __name__ == "__main__":
    markdown_to_image(md_content, 'bom_workflow.png', width=1400)