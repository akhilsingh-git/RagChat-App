# main.tf

# Configure the AWS provider
provider "aws" {
  region = "ap-south-1" # You can change this to your preferred region
}

# 1. Define the Security Group to allow inbound traffic
resource "aws_security_group" "rag_app_sg" {
  name        = "rag-app-sg"
  description = "Allow HTTP and SSH inbound traffic"

  # Allow inbound HTTP traffic on port 8000 for the application
  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Allow from any IP address
  }

  # Allow inbound SSH traffic on port 22 for management
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # WARNING: For production, restrict this to your IP
  }

  # Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "rag-app-security-group"
  }
}

# 2. Define the EC2 Instance
resource "aws_instance" "rag_app_server" {
  # Ubuntu 24.04 LTS AMI for the ap-south-1 region.
  # Find the correct AMI ID for your region if you change it.
  ami           = "ami-0f5ee92e2d63afc18"
  instance_type = "t4g.large" # As requested

  # Associate the security group created above
  vpc_security_group_ids = [aws_security_group.rag_app_sg.id]

  # Specify the root block device for storage
  root_block_device {
    volume_size = 30  # 30 GB storage
    volume_type = "gp3"
    delete_on_termination = true
  }

  # Add your SSH key name to be able to connect via SSH
  # This key must already exist in your AWS account.
  key_name = "ShopOS" # <-- IMPORTANT: Replace this

  # User data script to bootstrap the instance using the official Docker install script
  user_data = <<-EOF
              #!/bin/bash
              # Update package lists and install prerequisites
              sudo apt-get update -y
              sudo apt-get install -y ca-certificates curl
              
              # Add Docker's official GPG key
              sudo install -m 0755 -d /etc/apt/keyrings
              sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
              sudo chmod a+r /etc/apt/keyrings/docker.asc

              # Add the repository to Apt sources
              echo \
                "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
                $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
                sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
              sudo apt-get update -y
              
              # Install Docker Engine, CLI, Containerd, and Docker Compose plugin
              sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
              
              # Start and enable Docker service
              sudo systemctl start docker
              sudo systemctl enable docker
              
              # Add the default 'ubuntu' user to the docker group
              sudo usermod -aG docker ubuntu
              EOF

  tags = {
    Name = "RAG-App-Server"
  }
}

# 3. Output the Public IP of the instance
output "instance_public_ip" {
  value = aws_instance.rag_app_server.public_ip
}
