# Choose a slim-buster image for a smaller footprint
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
# If requirements.txt doesn't change, this layer won't be rebuilt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code into the container
# The '.' at the end means "copy everything from the current directory into the WORKDIR of the container"
COPY . .

# Expose port 7860, which is the default port for Hugging Face Spaces
EXPOSE 7860

# Command to run the application using Gunicorn
# "--bind 0.0.0.0:7860" tells Gunicorn to listen on all network interfaces on port 7860.
# "SkyLite:server" specifies the Python module ("SkyLite.py") and the Dash app's server instance ("server").
# Ensure your SkyLite.py file has `server = app.server` after "app = Dash(...)"
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "SkyLite:server"]