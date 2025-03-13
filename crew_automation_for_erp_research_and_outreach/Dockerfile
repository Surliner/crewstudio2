FROM python:3.12-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the application
COPY . .

# Install the package in development mode
RUN pip install -e .

# Expose the port
EXPOSE 8501

# Set environment variables
ENV PYTHONPATH=/app/src

# Run the application
CMD ["streamlit", "run", "src/crew_automation_for_erp_research_and_outreach/app.py", "--server.address", "0.0.0.0"] 