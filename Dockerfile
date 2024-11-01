# Use the base image from Broad Institute's ML4H repo
FROM ghcr.io/broadinstitute/ml4h:tf2.9-latest-cpu

# Set working directory
WORKDIR /workspace

# Copy your application code
COPY . /workspace

# Install necessary packages
RUN pip install fastapi uvicorn jinja2 python-multipart

# Expose port for the FastAPI application
EXPOSE 8000

# Run the FastAPI app with uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
