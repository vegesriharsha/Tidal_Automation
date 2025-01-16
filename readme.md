# REST API Client with CSV Processing

A Python desktop application for processing CSV files and making REST API calls with XML payloads. The application provides a graphical user interface for configuring API endpoints, managing authentication, and processing CSV data in batch.

## Features

- Graphical User Interface (GUI) for easy interaction
- CSV file processing with customizable field mapping
- XML payload generation with CDATA support
- SSL certificate verification options
- Bearer token authentication
- Detailed request and response logging
- Progress tracking for batch processing
- Error handling and reporting
- Support for carriage return preservation in XML CDATA sections

## Prerequisites

- Python 3.x
- Required Python packages:
  - requests
  - tkinter (usually comes with Python)

## Installation

1. Create a virtual environment (recommended):
```bash
python -m venv venv
```

2. Activate the virtual environment:
   - Windows (PowerShell):
   ```powershell
   .\venv\Scripts\Activate
   ```
   - Linux/Mac:
   ```bash
   source venv/bin/activate
   ```

3. Install required packages:
```bash
pip install requests
```

4. Save the code as `rest_api_client.py`

5. Run the application:
```bash
python rest_api_client.py
```

## Usage

### Main Interface

The application window contains several sections:
1. Configuration inputs
2. CSV file selection
3. Process control
4. Logging tabs

### Configuration Options

- **API URL**: The endpoint URL for the REST API
- **Bearer Token**: Authentication token
- **SSL Certificate Verification**: Toggle for SSL verification
- **Certificate Path**: Optional path to custom SSL certificate
- **CSV File Selection**: Browse and select input CSV file

### CSV File Format

The CSV file should contain the following columns (in order):
1. ID (required)
2. Agent ID
3. Inherit Agent
4. Inherit Calendar
5. Parameters

Example CSV format:
```csv
id,agentid,inheritagent,inheritcalendar,parameters
123,agent1,true,false,param1=value1
124,agent2,false,true,param2=value2
```

### XML Payload Format

The application generates XML payloads in the following format:
```xml
<?xml version="1.0" encoding="UTF-8" ?>
<entry xmlns="http://purl.org/atom/ns#">
    <tes:Job.update xmlns:tes="http://www.tidalsoftware.com/client/tesservlet">
        <object>
            <tes:job xmlns:tes="http://www.tidalsoftware.com/client/tesservlet">
                <tes:id>123</tes:id>
                <tes:agentid>agent1</tes:agentid>
                <tes:inheritagent>true</tes:inheritagent>
                <tes:inheritcalendar>false</tes:inheritcalendar>
                <tes:parameters><![CDATA[param1=value1]]></tes:parameters>
            </tes:job>
        </object>
    </tes:Job.update>
</entry>
```

### Processing Rules

1. Each row in the CSV file is processed sequentially
2. There is a 3-second delay between API requests
3. The process continues even if individual requests fail
4. Missing optional fields are omitted from the XML payload
5. Missing required fields (ID) trigger validation errors

### Logging and Monitoring

The application provides three separate logging areas:
1. **Process Log**: General operation information and errors
2. **API Requests**: Complete request details including headers and payloads
3. **API Responses**: Full response data from each API call

### Error Handling

- Missing required fields are logged
- API request failures are captured and logged
- SSL certificate issues are handled with options to bypass or provide custom certificates
- Process continues despite individual row failures
- Comprehensive error summary provided after completion

## Troubleshooting

### SSL Certificate Issues

If encountering SSL certificate errors:
1. Uncheck "Verify SSL Certificate" for testing purposes
2. For production, provide the path to your SSL certificate
3. Ensure the certificate is in PEM, CRT, or CER format

### API Errors

1. Verify the API URL is correct and accessible
2. Check the Bearer token is valid and properly formatted
3. Review the API Responses tab for detailed error messages
4. Ensure the XML payload matches the API's expected format

### CSV Processing Issues

1. Verify the CSV file has the correct column order
2. Check for missing required ID values
3. Ensure the CSV file is properly formatted and not corrupted
4. Verify character encoding (UTF-8 recommended)

## Security Notes

- Bearer tokens are handled as plain text in the UI
- SSL verification can be disabled but is not recommended for production use
- XML payloads may contain sensitive data in the parameters field
- CDATA sections preserve formatting but do not provide encryption

## Contributing

Feel free to modify and enhance the code according to your needs. Some potential areas for improvement:
- Add support for different authentication methods
- Implement concurrent request processing
- Add payload validation before submission
- Enhance error recovery mechanisms
- Add support for different input file formats

## License

This code is provided as-is under the MIT license. Feel free to modify and distribute as needed.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the error logs
3. Verify your input data formatting
4. Check your API endpoint documentation
