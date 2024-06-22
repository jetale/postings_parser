provider "aws" {
  region = "us-east-1" # Replace with your desired region
}

resource "aws_instance" "example" {
  ami           = "ami-04b70fa74e45c3917" # Replace with a valid AMI ID for your region
  instance_type = "t2.micro"
  key_name      = "terraform_key_pair"    # Replace with your key pair name

  user_data = <<-EOF
              #!/bin/bash
              echo "Hello, World!"
              uptime
              shutdown -h now
              EOF

  tags = {
    Name = "ExampleInstance"
  }
}
