import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import csv
import requests
import xml.etree.ElementTree as ET
import time
from datetime import datetime
import os
from typing import Dict, List, Optional

class RestApiClient:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("REST API Client")
        self.window.geometry("800x600")
        self.create_ui()
        
    def create_ui(self):
        # URL input
        url_frame = ttk.Frame(self.window, padding="5")
        url_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(url_frame, text="API URL:").pack(side=tk.LEFT)
        self.url_entry = ttk.Entry(url_frame, width=50)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Token input
        token_frame = ttk.Frame(self.window, padding="5")
        token_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(token_frame, text="Bearer Token:").pack(side=tk.LEFT)
        self.token_entry = ttk.Entry(token_frame, width=50)
        self.token_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # File selection
        file_frame = ttk.Frame(self.window, padding="5")
        file_frame.pack(fill=tk.X, padx=5, pady=5)
        self.file_label = ttk.Label(file_frame, text="No file selected")
        self.file_label.pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_file).pack(side=tk.LEFT)
        
        # Process button
        ttk.Button(self.window, text="Process CSV", command=self.process_csv).pack(pady=10)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(self.window, variable=self.progress_var, maximum=100)
        self.progress.pack(fill=tk.X, padx=5, pady=5)
        
        # Log area
        self.log_area = scrolledtext.ScrolledText(self.window, height=20)
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def browse_file(self):
        filename = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if filename:
            self.file_label.config(text=os.path.basename(filename))
            self.selected_file = filename
            
    def log_message(self, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_area.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_area.see(tk.END)
        
    def create_xml_payload(self, row: Dict[str, str]) -> Optional[str]:
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
        
        # Add optional elements only if they have values
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
            parameters_elem.text = row['parameters']
            
        return ET.tostring(root, encoding='unicode', xml_declaration=True)
        
    def process_csv(self):
        if not hasattr(self, 'selected_file'):
            self.log_message("Error: No file selected")
            return
            
        url = self.url_entry.get().strip()
        token = self.token_entry.get().strip()
        
        if not url or not token:
            self.log_message("Error: URL and Bearer Token are required")
            return
            
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/xml'
        }
        
        errors = []
        
        try:
            with open(self.selected_file, 'r') as file:
                csv_reader = csv.DictReader(file)
                rows = list(csv_reader)
                total_rows = len(rows)
                
                for index, row in enumerate(rows, 1):
                    # Map CSV columns to payload attributes
                    data = {
                        'id': row.get(csv_reader.fieldnames[0], ''),
                        'agentid': row.get(csv_reader.fieldnames[1], ''),
                        'inheritagent': row.get(csv_reader.fieldnames[2], ''),
                        'inheritcalendar': row.get(csv_reader.fieldnames[3], ''),
                        'parameters': row.get(csv_reader.fieldnames[4], '')
                    }
                    
                    # Update progress bar
                    self.progress_var.set((index / total_rows) * 100)
                    self.window.update_idletasks()
                    
                    # Create XML payload
                    payload = self.create_xml_payload(data)
                    
                    if not payload:
                        error_msg = f"Row {index}: Missing required 'id' field"
                        self.log_message(error_msg)
                        errors.append(error_msg)
                        continue
                    
                    try:
                        # Make API request
                        response = requests.post(url, headers=headers, data=payload)
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
