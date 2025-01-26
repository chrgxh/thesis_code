# Variables
$ImageName = "flask-db-access"
$ContainerName = "flask-db-container"
$HostPort = 8080  # Port on the host
$AppHost = "0.0.0.0"  # Host for the application inside the container
$AppPort = 5000  # Port for the application inside the container
$DB_Host = "host.docker.internal"
$DB_Port = 5433
$DB_Name = "thesis_database"
$DB_User = "postgres"
$DB_Password = "password"
$BaseURL = "localhost"  # Configurable base URL (e.g., "192.168.1.100" or "example.com")

# Check if Docker CLI is working
Write-Host "Checking if Docker is running..."
try {
    docker info | Out-Null
    Write-Host "Docker is running."
} catch {
    Write-Error "Docker service is not accessible. Please ensure Docker Desktop is running and Docker CLI is available in your PATH."
    exit 1
}

# Stop and remove any existing container with the same name
Write-Host "Stopping and removing any existing container named $ContainerName..."
docker stop $ContainerName | Out-Null
docker rm $ContainerName | Out-Null

# Run the Docker container
Write-Host "Running the Docker container..."
docker run -d `
    --name $ContainerName `
    -p "$($HostPort):$($AppPort)" `
    -e APP_HOST="$AppHost" `
    -e APP_PORT="$AppPort" `
    -e DB_HOST="$DB_Host" `
    -e DB_PORT="$DB_Port" `
    -e DB_NAME="$DB_Name" `
    -e DB_USER="$DB_User" `
    -e DB_PASSWORD="$DB_Password" `
    $ImageName

# Check if the container is running
Write-Host "Checking if the container is running..."
if (docker ps -q -f "name=$ContainerName") {
    Write-Host "Container is running and accessible at http://${BaseURL}:${HostPort}"
} else {
    Write-Error "Failed to start the container. Check the logs for details:"
    docker logs $ContainerName
}
