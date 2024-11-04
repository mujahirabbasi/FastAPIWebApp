# FastAPI Web Application

This FastAPI web application can be run locally using Docker. The following steps needs yo be followed in order to run the Docker container, install dependencies, and start the application.

## Setting up your local environment

Clone the repository:

```bash
git clone https://github.com/mujahirabbasi/FastAPIWebApp.git
```

## Running the Application

### Step 1: Start the Docker Container

Run the following command in your terminal to start the Docker container, map the current directory to `/workspace` inside the container, and expose port `8000`:

```bash
docker run -it --rm -v "$(pwd):/workspace" -p 8000:8000 ghcr.io/broadinstitute/ml4h:tf2.9-latest-cpu
```

### Step 2: Install Dependencies

Inside the running Docker container, navigate to the `/workspace` directory and install the dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Step 3: Start the FastAPI Application

Run the following command to start the FastAPI application using `uvicorn`:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### Accessing the Application

Once the server is running, you can access the application locally by navigating to:

- **Homepage**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

The server will automatically reload upon detecting any changes in the source code, thanks to the `--reload` flag.

## Building the Docker Image Locally

To build a custom Docker image, create a `Dockerfile` with the following content:

```dockerfile
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
```

### Build the Docker Image

```bash
docker build -t my-fastapi-ecg-app .
```

### Test the Docker Image Locally

```bash
docker run -p 8000:8000 my-fastapi-ecg-app
```

## Deploying to Azure

### Deployment Workflow
Create Docker Image ➔ Push Image to Azure Container Registry ➔ Host on Azure App Service

### Step 1: Log in to Azure

```bash
az login
```

### Step 2: Create a Resource Group

```bash
az group create --name myResourceGroup --location westus
```

### Step 3: Create an Azure Container Registry (ACR)

```bash
az acr create --resource-group myResourceGroup --name myContainerRegistry --sku Basic
az acr login --name myContainerRegistry
```
![Azure Container Registry](https://raw.githubusercontent.com/mujahirabbasi/FastAPIWebApp/main/container%20_registry.png)


### Step 4: Build, Tag, and Push Docker Image

```bash
docker build -t my-fastapi-ecg-app .
docker tag my-fastapi-ecg-app mycontainerregistry.azurecr.io/my-fastapi-ecg-app:latest
docker push mycontainerregistry.azurecr.io/my-fastapi-ecg-app:latest
```

### Step 5: Create App Service Plan and Web App

```bash
az appservice plan create --resource-group myResourceGroup --name myAppServicePlan --is-linux --sku B1
az webapp create --resource-group myResourceGroup --plan myAppServicePlan --name myFastApiApp --deployment-container-image-name mycontainerregistry.azurecr.io/my-fastapi-ecg-app:latest
az webapp config container set --name myFastApiApp --resource-group myResourceGroup --docker-custom-image-name mycontainerregistry.azurecr.io/my-fastapi-ecg-app:latest --docker-registry-server-url https://mycontainerregistry.azurecr.io
```
![Azure App Service](https://raw.githubusercontent.com/mujahirabbasi/FastAPIWebApp/main/AzureAppSevice.png)

### Step 6: Set App Service to Listen on Port 8000

```bash
az webapp config appsettings set --resource-group myResourceGroup --name myFastApiApp --settings WEBSITES_PORT=8000
```

Once the server is running, you can access the application on the web by navigating to:

- **Homepage**: [https://mynewfastapiapp.azurewebsites.net/](https://mynewfastapiapp.azurewebsites.net/)

![Azure WebApp](https://raw.githubusercontent.com/mujahirabbasi/FastAPIWebApp/main/AzureWebApp.png)

> **Note**: All deployment steps in this guide are performed using the **Azure CLI**.

## Why FastAPI?

FastAPI’s asynchronous request handling improves response times and enables scalability, making it ideal for processing large ECG files and serving multiple users concurrently. It delivers high performance, enhancing user experience during model predictions. Its seamless Docker compatibility aligns perfectly with the ML4H Docker environment, simplifying deployment and dependency management.

## Scalability

To scale this solution for analyzing a larger data volume and supporting more users, we can use two main strategies. First, implement asynchronous processing to handle file uploads and model inference concurrently, allowing large batches to be processed without blocking. Second, utilize cloud-based scaling by deploying the application on a cloud platform like AWS or Google Cloud or Azure, enabling horizontal scaling with multiple instances to distribute the workload based on demand. 

## Tools Used
To develop portions of the HTML, CSS, and JavaScript for this application, I used ChatGPT and Gemini to accelerate development and enhance code quality.

