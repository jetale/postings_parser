terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }

    local = {
      source  = "hashicorp/local"
      version = "~> 2.1"
    }
  }

  required_version = ">= 1.2.0"
}

provider "aws" {
  region = "us-east-1" # Replace with your desired region
}

resource "aws_key_pair" "ssh_key" {
  key_name   = "my_aws_key"
  public_key = file("~/.ssh/id_rsa.pub")
}

resource "aws_instance" "example" {
  count = 20
  ami           = "ami-04b70fa74e45c3917" # Replace with a valid AMI ID for your region
  instance_type = "t2.micro"
  key_name      = aws_key_pair.ssh_key.key_name
  vpc_security_group_ids = ["sg-01b0a61a502fdf61a"]


  tags = {
    Name = "parser-instance-${count.index + 1}"
  }
}


resource "local_file" "inventory" {
  content = templatefile("${path.module}/inventory.tpl", {
    instances = aws_instance.example.*.public_ip
  })
  filename = "${path.module}/inventory.ini"
}
