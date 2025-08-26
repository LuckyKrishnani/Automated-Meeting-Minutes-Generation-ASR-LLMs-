import json
import streamlit as st
from datetime import datetime
from typing import Dict, List
import base64

class OutputGenerator:
    """Generates output files in different formats (JSON, HTML, PDF)"""
    
    def __init__(self):
        # Constructor (currently unused but kept for future extensibility)
        pass
    
    def generate_outputs(self, minutes: Dict, formats: List[str]) -> Dict[str, bytes]:
        """
        Generate output files in specified formats.
        
        Args:
            minutes (Dict): Meeting minutes data (contains summary, actions, etc.)
            formats (List[str]): List of formats to generate ["JSON", "HTML", "PDF"]
            
        Returns:
            Dict[str, bytes]: Dictionary mapping format names to file content in bytes
        """
        outputs = {}
        
        try:
            # Loop through each requested format and call the respective generator
            for format_name in formats:
                if format_name == "JSON":
                    outputs["JSON"] = self._generate_json(minutes)
                elif format_name == "HTML":
                    outputs["HTML"] = self._generate_html(minutes)
                elif format_name == "PDF":
                    outputs["PDF"] = self._generate_pdf(minutes)
            
            return outputs
            
        except Exception as e:
            # If any error occurs during generation, display error in Streamlit
            st.error(f"Error generating outputs: {str(e)}")
            raise
    
    def _generate_json(self, minutes: Dict) -> bytes:
        """Generate JSON output"""
        try:
            # Convert Python dictionary into pretty-printed JSON string
            json_data = json.dumps(minutes, indent=2, ensure_ascii=False)
            return json_data.encode('utf-8')  # Convert string into bytes for file download
        except Exception as e:
            st.error(f"Error generating JSON: {str(e)}")
            raise
    
    def _generate_html(self, minutes: Dict) -> bytes:
        """Generate HTML output for meeting minutes"""
        try:
            # HTML template with placeholders for meeting data
            html_template = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Meeting Minutes - {title}</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        max-width: 800px;
                        margin: 0 auto;
                        padding: 20px;
                        line-height: 1.6;
                    }}
                    .header {{
                        background-color: #f4f4f4;
                        padding: 20px;
                        border-radius: 5px;
                        margin-bottom: 20px;
                    }}
                    .section {{
                        margin-bottom: 30px;
                    }}
                    .action-item {{
                        background-color: #fff3cd;
                        padding: 10px;
                        margin: 5px 0;
                        border-left: 4px solid #ffc107;
                    }}
                    .decision {{
                        background-color: #d1ecf1;
                        padding: 10px;
                        margin: 5px 0;
                        border-left: 4px solid #17a2b8;
                    }}
                    h1, h2 {{
                        color: #333;
                    }}
                    .timestamp {{
                        color: #666;
                        font-size: 0.9em;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Meeting Minutes: {title}</h1>
                    <p><strong>Date:</strong> {date}</p>
                    <p><strong>Duration:</strong> {duration}</p>
                    <p><strong>Participants:</strong> {participants}</p>
                </div>
                
                <div class="section">
                    <h2>📋 Summary</h2>
                    <p>{summary}</p>
                </div>
                
                <div class="section">
                    <h2>🎯 Key Decisions</h2>
                    {decisions_html}
                </div>
                
                <div class="section">
                    <h2>✅ Action Items</h2>
                    {action_items_html}
                </div>
                
                <div class="section">
                    <h2>🔄 Next Steps</h2>
                    <ul>
                        {next_steps_html}
                    </ul>
                </div>
                
                <div class="section">
                    <h2>📝 Full Transcript</h2>
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px;">
                        <pre style="white-space: pre-wrap;">{transcript}</pre>
                    </div>
                </div>
                
                <footer style="margin-top: 40px; text-align: center; color: #666;">
                    <p class="timestamp">Generated on {generated_time}</p>
                </footer>
            </body>
            </html>
            """
            
            # Extract meeting information
            meeting_info = minutes.get('meeting_info', {})
            
            # Build dynamic sections of HTML
            decisions_html = ''.join([
                f'<div class="decision">• {decision}</div>' 
                for decision in minutes.get('key_decisions', [])
            ])
            
            action_items_html = ''.join([
                f'<div class="action-item"><strong>{item.get("assignee", "Unassigned")}:</strong> '
                f'{item.get("task", "")} <em>(Due: {item.get("due_date", "TBD")})</em></div>'
                for item in minutes.get('action_items', [])
            ])
            
            next_steps_html = ''.join([f'<li>{step}</li>' for step in minutes.get('next_steps', [])])
            
            # Fill template with actual data
            html_content = html_template.format(
                title=meeting_info.get('title', 'Meeting'),
                date=meeting_info.get('date', ''),
                duration=meeting_info.get('duration', 'Unknown'),
                participants=', '.join(meeting_info.get('participants', [])),
                summary=minutes.get('summary', ''),
                decisions_html=decisions_html,
                action_items_html=action_items_html,
                next_steps_html=next_steps_html,
                transcript=minutes.get('full_transcript', ''),
                generated_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            
            return html_content.encode('utf-8')  # Return as bytes
            
        except Exception as e:
            st.error(f"Error generating HTML: {str(e)}")
            raise
    
    def _generate_pdf(self, minutes: Dict) -> bytes:
        """Generate PDF output (placeholder implementation)"""
        try:
            # For real implementation, use ReportLab or FPDF
            # This is a simple text-based placeholder pretending to be PDF content
            pdf_content = f"""
            Meeting Minutes: {minutes.get('meeting_info', {}).get('title', 'Meeting')}
            Date: {minutes.get('meeting_info', {}).get('date', '')}
            
            Summary:
            {minutes.get('summary', '')}
            
            Key Decisions:
            {chr(10).join(['• ' + decision for decision in minutes.get('key_decisions', [])])}
            
            Action Items:
            {chr(10).join([f"• {item.get('assignee', 'Unassigned')}: {item.get('task', '')}" 
                          for item in minutes.get('action_items', [])])}
            """
            
            return pdf_content.encode('utf-8')  # Return as bytes
            
        except Exception as e:
            st.error(f"Error generating PDF: {str(e)}")
            raise
