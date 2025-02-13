# rest_api_client.py

"""
REST API Client Application
--------------------------
This application processes CSV files and makes REST API calls with XML payloads.
It includes features like SSL handling, CDATA processing, and request/response logging.

Author: [Your Name]
Version: 1.0
Date: 2025-01-15

Usage:
    1. Install required packages: pip install requests
    2. Run the script: python rest_api_client.py
"""

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import csv
import requests
import xml.etree.ElementTree as ET
import time
from datetime import datetime
import os
from typing import Dict, List, Optional
import json
from xml.dom import minidom

class RestApiClient:
    """
    Main application class for the REST API client.
    Handles GUI creation, CSV processing, and API communication.
    """
    
    def __init__(self):
        """Initialize the application window and UI components."""
        self.window = tk.Tk()
        self.window.title("REST API Client")
        self.window.geometry("1200x800")
        self.create_ui()
        
    def create_ui(self):
        """Create and configure all UI elements."""
        # Main container
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Input section
        input_frame = self.create_input_section(main_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Notebook for logs
        self.create_notebook(main_frame)
        
    def create_input_section(self, parent):
        """Create the input controls section."""
        input_frame = ttk.LabelFrame(parent, text="Configuration", padding="5")
        
        # URL input
        url_frame = ttk.Frame(input_frame, padding="5")
        url_frame.pack(fill=tk.X)
        ttk.Label(url_frame, text="API URL:").pack(side=tk.LEFT)
        self.url_entry = ttk.Entry(url_frame, width=50)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Token input
        token_frame = ttk.Frame(input_frame, padding="5")
        token_frame.pack(fill=tk.X)
        ttk.Label(token_frame, text="Bearer Token:").pack(side=tk.LEFT)
        self.token_entry = ttk.Entry(token_frame, width=50)
        self.token_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # SSL Verification
        ssl_frame = ttk.Frame(input_frame, padding="5")
        ssl_frame.pack(fill=tk.X)
        self.verify_ssl = tk.BooleanVar(value=False)
        ttk.Checkbutton(ssl_frame, text="Verify SSL Certificate", 
                       variable=self.verify_ssl).pack(side=tk.LEFT)
        
        # Certificate path
        cert_frame = ttk.Frame(input_frame, padding="5")
        cert_frame.pack(fill=tk.X)
        ttk.Label(cert_frame, text="Certificate Path (optional):").pack(side=tk.LEFT)
        self.cert_entry = ttk.Entry(cert_frame, width=40)
        self.cert_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(cert_frame, text="Browse", 
                  command=self.browse_cert).pack(side=tk.LEFT)
        
        # File selection
        file_frame = ttk.Frame(input_frame, padding="5")
        file_frame.pack(fill=tk.X)
        self.file_label = ttk.Label(file_frame, text="No file selected")
        self.file_label.pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text="Browse CSV", 
                  command=self.browse_file).pack(side=tk.LEFT)
        
        # Process button and progress bar
        control_frame = ttk.Frame(input_frame, padding="5")
        control_frame.pack(fill=tk.X)
        ttk.Button(control_frame, text="Process CSV", 
                  command=self.process_csv).pack(side=tk.LEFT, padx=5)
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(control_frame, variable=self.progress_var, 
                                      maximum=100, length=300)
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        return input_frame
        
    def create_notebook(self, parent):
        """Create the notebook with logging tabs."""
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Process Log tab
        log_frame = ttk.Frame(notebook)
        notebook.add(log_frame, text='Process Log')
        self.log_area = scrolledtext.ScrolledText(log_frame, height=20)
        self.log_area.pack(fill=tk.BOTH, expand=True)
        
        # Request tab
        request_frame = ttk.Frame(notebook)
        notebook.add(request_frame, text='API Requests')
        self.request_area = scrolledtext.ScrolledText(request_frame, height=20)
        self.request_area.pack(fill=tk.BOTH, expand=True)
        
        # Response tab
        response_frame = ttk.Frame(notebook)
        notebook.add(response_frame, text='API Responses')
        self.response_area = scrolledtext.ScrolledText(response_frame, height=20)
        self.response_area.pack(fill=tk.BOTH, expand=True)
        
    def browse_cert(self):
        """Open file dialog for certificate selection."""
        filename = filedialog.askopenfilename(
            filetypes=[("Certificate Files", "*.pem;*.crt;*.cer"), 
                      ("All Files", "*.*")]
        )
        if filename:
            self.cert_entry.delete(0, tk.END)
            self.cert_entry.insert(0, filename)
            
    def browse_file(self):
        """Open file dialog for CSV selection."""
        filename = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv"), 
                      ("All Files", "*.*")]
        )
        if filename:
            self.file_label.config(text=os.path.basename(filename))
            self.selected_file = filename
            
    def log_message(self, message: str, area_type: str = 'log'):
        """Log a message to the specified area with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        if area_type == 'request':
            self.request_area.insert(tk.END, log_entry)
            self.request_area.see(tk.END)
        elif area_type == 'response':
            self.response_area.insert(tk.END, log_entry)
            self.response_area.see(tk.END)
        else:
            self.log_area.insert(tk.END, log_entry)
            self.log_area.see(tk.END)
            
    def format_xml(self, xml_string: str) -> str:
        """Format XML string with proper indentation while preserving CDATA."""
        # Extract CDATA content before formatting
        import re
        cdata_pattern = r'<!\[CDATA\[(.*?)\]\]>'
        cdata_matches = re.findall(cdata_pattern, xml_string, re.DOTALL)
        
        # Replace CDATA content with placeholder
        placeholder = "CDATA_PLACEHOLDER_XYZ"
        xml_with_placeholder = re.sub(cdata_pattern, placeholder, xml_string)
        
        try:
            dom = minidom.parseString(xml_with_placeholder)
            formatted_xml = dom.toprettyxml(indent="  ")
            # Remove empty lines
            formatted_xml = '\n'.join([line for line in formatted_xml.split('\n') 
                                     if line.strip()])
            
            # Restore CDATA content
            for cdata_content in cdata_matches:
                formatted_xml = formatted_xml.replace(
                    placeholder,
                    f'<![CDATA[{cdata_content}]]>'
                )
            return formatted_xml
        except:
            return xml_string
            
    def format_request(self, row_num: int, url: str, headers: dict, payload: str) -> str:
        """Format request details for display."""
        formatted_headers = json.dumps(headers, indent=2)
        formatted_payload = self.format_xml(payload)
        
        return f"""
=== Request for Row {row_num} ===
URL: {url}
Headers:
{formatted_headers}
Payload:
{formatted_payload}
===============================
"""
            
    def format_response(self, response, row_num: int) -> str:
        """Format response details for display."""
        try:
            content = response.json()
            formatted_content = json.dumps(content, indent=2)
        except json.JSONDecodeError:
            formatted_content = response.text
            
        return f"""
=== Response for Row {row_num} ===
Status Code: {response.status_code}
Headers: {dict(response.headers)}
Content:
{formatted_content}
===============================
"""
            
    def create_xml_payload(self, row: Dict[str, str]) -> Optional[str]:
        """Create XML payload from row data."""
        if not row.get('id'):
            return None
            
        # Create the XML structure
        ET.register_namespace('', "http://purl.org/atom/ns#")
        ET.register_namespace('tes', "http://www.tidalsoftware.com/client/tesservlet")
        
        root = ET.Element("{http://purl.org/atom/ns#}entry")
        job_update = ET.SubElement(root, "{http://www.tidalsoftware.com/client/tesservlet}Job.update")
        object_elem = ET.SubElement(job_update, "object")
        job = ET.SubElement(object_elem, "{http://www.tidalsoftware.com/client/tesservlet}job")
        
        # Add required id
        id_elem = ET.SubElement(job, "{http://www.tidalsoftware.com/client/tesservlet}id")
        id_elem.text = row['id']
        
        # Add optional elements
        if row.get('agentid'):
            agent_elem = ET.SubElement(job, "{http://www.tidalsoftware.com/client/tesservlet}agentid")
            agent_elem.text = row['agentid']
            
        if row.get('inheritagent'):
            inherit_agent_elem = ET.SubElement(job, "{http://www.tidalsoftware.com/client/tesservlet}inheritagent")
            inherit_agent_elem.text = row['inheritagent']
            
        if row.get('inheritcalendar'):
            inherit_calendar_elem = ET.SubElement(job, "{http://www.tidalsoftware.com/client/tesservlet}inheritcalendar")
            inherit_calendar_elem.text = row['inheritcalendar']
            
        if row.get('parameters'):
            parameters_elem = ET.SubElement(job, "{http://www.tidalsoftware.com/client/tesservlet}parameters")
            # Handle parameters value with CDATA and preserve formatting
            parameters_value = row['parameters']
            parameters_value = parameters_value.replace('\r\n', '\n').replace('\r', '\n')
            
            # Convert the Element to string
            xml_str = ET.tostring(root, encoding='unicode', xml_declaration=True)
            
            # Insert CDATA section
            cdata_section = f"<![CDATA[{parameters_value}]]>"
            xml_str = xml_str.replace(
                '<tes:parameters></tes:parameters>',
                f'<tes:parameters>{cdata_section}</tes:parameters>'
            )
            return xml_str
            
        return ET.tostring(root, encoding='unicode', xml_declaration=True)
        
    def process_csv(self):
        """Process the CSV file and make API requests."""
        if not hasattr(self, 'selected_file'):
            self.log_message("Error: No file selected")
            return
            
        url = self.url_entry.get().strip()
        token = self.token_entry.get().strip()
        cert_path = self.cert_entry.get().strip()
        
        if not url or not token:
            self.log_message("Error: URL and Bearer Token are required")
            return
            
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/xml'
        }
        
        # Configure SSL verification
        if self.verify_ssl.get():
            verify = cert_path if cert_path else True
        else:
            verify = False
            requests.packages.urllib3.disable_warnings(
                requests.packages.urllib3.exceptions.InsecureRequestWarning
            )
        
        errors = []
        
        # Clear previous content
        self.request_area.delete(1.0, tk.END)
        self.response_area.delete(1.0, tk.END)
        self.log_area.delete(1.0, tk.END)
        
        try:
            with open(self.selected_file, 'r') as file:
                csv_reader = csv.DictReader(file)
                rows = list(csv_reader)
                total_rows = len(rows)
                
                for index, row in enumerate(rows, 1):
                    # Map CSV columns
                    data = {
                        'id': row.get(csv_reader.fieldnames[0], ''),
                        'agentid': row.get(csv_reader.fieldnames[1], ''),
                        'inheritagent': row.get(csv_reader.fieldnames[2], ''),
                        'inheritcalendar': row.get(csv_reader.fieldnames[3], ''),
                        'parameters': row.get(csv_reader.fieldnames[4], '')
                    }
                    
                    # Update progress
                    self.progress_var.set((index / total_rows) * 100)
                    self.window.update_idletasks()
                    
                    # Create payload
                    payload = self.create_xml_payload(data)
                    
                    if not payload:
                        error_msg = f"Row {index}: Missing required 'id' field"
                        self.log_message(error_msg)
                        errors.append(error_msg)
                        continue
                    
                    # Log request details
                    self.log_message(self.format_request(index, url, headers, payload), 'request')
                    
                    try:
                        # Make API request with SSL verification configuration
                        response = requests.post(url, headers=headers, data=payload, verify=verify)
                        
                        # Log the response
                        self.log_message(f"Row {index}: Status Code {response.status_code}")
                        self.log_message(self.format_response(response, index), 'response')
                        
                        # Check for successful response
                        response.raise_for_status()
                        self.log_message(f"Row {index}: Successfully processed")
                        
                    except requests.exceptions.RequestException as e:
                        error_msg = f"Row {index}: API request failed - {str(e)}"
                        self.log_message(error_msg)
                        errors.append(error_msg)
                        
                    # Wait 3 seconds before next request
                    time.sleep(3)
                    
        except Exception as e:
            self.log_message(f"Error processing file: {str(e)}")
            return
            
        # Display final status
        self.log_message("\nProcessing completed!")
        if errors:
            self.log_message("\nErrors encountered:")
            for error in errors:
                self.log_message(error)
        
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = RestApiClient()
    app.run()
