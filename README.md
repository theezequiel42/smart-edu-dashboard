# Smart Edu Dashboard - Interactive Educational Assessment Analysis Tool

Smart Edu Dashboard is a Streamlit-based web application that enables educational professionals to analyze and visualize student assessment data through two specialized modes: SME (Survey Analysis) and CMAE (Student Development Assessment). The application provides interactive data visualization, customizable reporting, and comprehensive analysis tools for educational institutions.

The application offers robust features for data analysis including:
- Dynamic filtering of assessment data by school unit, category, and individual student
- Multiple visualization options including bar charts, pie charts, and line graphs
- Automated report generation in PDF and Word formats
- Real-time calculation of student development metrics
- Interactive dashboard with summary statistics and status distribution

## Repository Structure
```
.
├── main.py                 # Application entry point and UI initialization
├── sme_mode.py            # Survey analysis mode implementation
├── cmae_mode.py           # Student assessment analysis mode implementation
├── utils.py               # Shared utility functions for data processing
├── requirements.txt       # Python package dependencies
└── auxiliar.txt          # Setup and deployment instructions
```

## Usage Instructions
### Prerequisites
- Python 3.x
- pip package manager

### Installation
```bash
# Install required dependencies
python -m pip install -r requirements.txt

# Run the application
python -m streamlit run main.py
```

### Quick Start
1. Launch the application using the command above
2. Select either SME or CMAE mode from the initial screen
3. Upload an Excel file containing the assessment data
4. Use the sidebar filters to customize your analysis
5. Generate and download reports based on the visualized data

### More Detailed Examples

**SME Mode Usage:**
```python
# Upload survey data Excel file
# Select course from dropdown
# Choose questions to analyze
# Select visualization type (Bar/Pie/Line)
# Download Word report with analysis
```

**CMAE Mode Usage:**
```python
# Upload student assessment Excel file
# Filter by school unit
# Select category (Socialization/Language/Cognition/etc.)
# Choose student from dropdown
# View status distribution
# Download PDF report
```

### Troubleshooting

**Common Issues:**

1. File Upload Errors
   - Problem: "Unable to load Excel file"
   - Solution: Ensure file is in .xlsx format
   - Check file permissions

2. Visualization Issues
   - Problem: Graphs not displaying
   - Solution: Verify data contains valid responses
   - Check column names match expected format

3. Report Generation Errors
   - Problem: PDF/Word export fails
   - Solution: Ensure sufficient disk space
   - Verify write permissions in output directory

## Data Flow
The application processes educational assessment data through a structured pipeline from file upload to visualization and reporting.

```ascii
[Excel File] -> [Data Loading] -> [Processing/Filtering] -> [Analysis] -> [Visualization]
                                                                      -> [Report Generation]
```

Key component interactions:
1. Data loading through Streamlit's file uploader
2. Pandas DataFrame processing for data manipulation
3. Matplotlib/Seaborn for visualization generation
4. ReportLab/python-docx for report creation
5. Real-time filtering and recalculation of metrics
6. Dynamic UI updates based on user selections
7. Automated status calculation based on assessment criteria
8. Export functionality for generated reports