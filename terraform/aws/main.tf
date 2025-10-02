# use terraform to provision an EC2 (virtual machines and a common component of many infrastructure) instance on Amazon
# 2. Configure provider which AWS account & region to use
provider "aws" {
    region = "ap-southeast-2"
}

# 3. Create vpc (our pvc instead of aws_default_vpc) ----------------------------
# create default vpc if one does not exist
# Ensures DNS support and hostname assignment are enabled for instances within the VPC.
resource "aws_vpc" "main" {
    cidr_block          = "10.0.0.0/16" # network class 10.0.0.0 | host 10.0.0.1 - 10.0.255.255
    instance_tenancy    = "default"
    enable_dns_support   = true
    enable_dns_hostnames = true
    tags = {
        Name = "default vpc"
    }
}
# 3.1 Associating a Public DNS Record with Elastic IP (EIP) using Route 53
# create custom domain name to point to specific public IP address
# Allocate Elastic IP(EIP)
# - Allocates a static public IPv4 address (Elastic IP) to your AWS account
resource "aws_eip" "web_eip" {
    vpc = true
    tags = {
        Name = "web-eip"
    }
}

# ---------------------------------------------------------------------------
# 4. create a public subnet (need IGW for outbound) -----------------------
# use data source to get all availability zones in region
data "aws_availability_zones" "availability_zones" {} 

# create default subnet if one does not exist
resource "aws_subnet" "default_az1" {
    vpc_id     = aws_vpc.main.id # select vpc_id from created vpc
    cidr_block = "10.0.1.0/24" # network for subnet (กำหนดให้มันมีขนาด Subnet เล็กกว่าที่เราสร้างเอาไว้ในขั้นตอนสร้าง VPC)
    # availability_zone = "ap-southeast-2b"
    availability_zone = data.aws_availability_zones.availability_zones.names[0]
    map_public_ip_on_launch = true 

    tags = {
        Name = "default subnet"
    }
}
#------------------------------------------------------------------------------
# 5. Create Internet Gateway
# Internet Gateway
resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id # select created vpc

  tags = { Name = "main-igw" }
}

# 6. create routing table -------------------------------
# Route Table for Public Subnet
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0" # destination: public 0.0.0.0/0 | internal org: org IP
    gateway_id = aws_internet_gateway.gw.id # target: select internet gateway
  }

  tags = { Name = "public-rt" }
}
# (cont.) & attach to subnet
# Associate subnet with public route table
resource "aws_route_table_association" "public_assoc" {
  subnet_id      = aws_subnet.default_az1.id # selected created subnet
  route_table_id = aws_route_table.public.id # selected created subnet
}
# ---------------------------------------------------------------
# 7. create Security group: Allow HTTP(80) and SSH (22)
# create security group for the ec2 instance
resource "aws_security_group" "ec2_security_group" {
    name        = "ec2 security group"
    description = "allow access on ports 80 and 22"
    vpc_id      = aws_vpc.main.id

    ingress {
        description = "http access"
        from_port   = 80
        to_port     = 80
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    ingress {
        description = "ssh access"
        from_port   = 22
        to_port     = 22
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"] # can restrict to your IP (ssh access only from your IP)
    }

    egress {
        from_port   = 0
        to_port     = 0
        protocol    = -1
        cidr_blocks = ["0.0.0.0/0"]
    }

    tags = {
        Name = "docker server sg"
    }
}
# -----------------------------------------------------------------------
# 8. Generate SSH key pair and saves .pem locally -----------------
# create private key to ssh access 
resource "tls_private_key" "ec2" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "ec2_key" {
  key_name   = "ec2_key"
  public_key = tls_private_key.ec2.public_key_openssh
}

resource "local_file" "private_key" {
  content     = tls_private_key.ec2.private_key_pem
  filename  = "${path.module}/ec2_key.pem" # path.module is current location
}
#-------------------------------------------------
# 9. Create EC2 instance --------------------------------------
# use data source to get a registered amazon linux 2 ami
data "aws_ami" "amazon_linux_2" {
    most_recent = true
    owners      = ["amazon"]

    filter {
        name    = "owner-alias"
        values  = ["amazon"]
    }

    filter {
        name    = "name"
        values  = ["amzn2-ami-hvm*"]
    }
}

# launch the ec2 instance
resource "aws_instance" "ec2_instance" {
    ami                     = data.aws_ami.amazon_linux_2.id
    instance_type           = "t4g.micro"
    subnet_id               = aws_subnet.default_az1.id
    vpc_security_group_ids  = [aws_security_group.ec2_security_group.id]
    key_name                = aws_key_pair.ec2_key.key_name
    associate_public_ip_address = true

    #   - B. use user_data
    user_data = <<-EOF
                #!/bin/bash
                sudo yum update -y
                sudo amazon-linux-extras install docker -y
                sudo service docker start
                sudo systemctl enable docker
                sudo yum install git -y
                cd /home/ec2-user
                mkdir learn_mlopz
                # git clone https://github.com/Ar3ee3ar/learn_mlopz.git
                EOF

    tags = {
        Name = "docker server"
    }
}

# (Optional) Associate the EIP with an EC2 instance
# - Associates the allocated EIP with a specific EC2 instance.
resource "aws_eip_association" "eip_assoc" {
    instance_id = aws_instance.ec2_instance.id
    allocation_id = aws_eip.web_eip.id
}

# # 10. Create a Route 53 Hosted Zone (if you don't have one already)
# # - Represents your domain's hosted zone in Route 53, where DNS records are managed.
# resource "aws_route53_zone" "primary" {
#     name = "mlopz.com" # domain name
# }

# # 10.1 Create a record to point your domain to the EIP
# # - Creates an "A" record within the hosted zone, mapping a subdomain (e.g., www.example.com) to the public IPv4 address of your EIP.
# resource "aws_route53_record" "www" {
#     zone_id = aws_route53_zone.primary.zone_id
#     name = "www.mlopz.com"
#     type = "A"
#     ttl  = 300
#     records = [aws_eip.web_eip.public_ip]
# }
# --------------------------------------------------------------------------
# (optional) connect to EC2 to send file/ run command/ etc.
# an empty resource block
# resource "null_resource" "name" {
#     # wait for ec2 to be created
#     depends_on = [aws_instance.ec2_instance]

#     # ssh into the ec2 instance
#     connection {
#         type        = "ssh"
#         user        = "ec2-user"
#         private_key = tls_private_key.ec2.private_key_pem
#         host        = aws_instance.ec2_instance.public_ip
#     }

#     # copy the password file for your docker hub account
#     # from your computer to the ec2 instance
#     # provisioner "file" {
#     #     source      = "D:/personal_proj/mlops/mlops-project/terraform/aws/docker_password.txt"
#     #     destination = "/home/ec2-user/docker_password.txt"
#     # }

#     # # copy the dockerfile from your computer to the ec2 instance
#     # provisioner "file" {
#     #     source      = "D:/personal_proj/mlops/mlops-project/Dockerfile"
#     #     destination = "/home/ec2-user/Dockerfile"
#     # }

#     # # copy .env file for docker
#     # provisioner "file" {
#     #     source      = "D:/personal_proj/mlops/mlops-project/.env"
#     #     destination = "/home/ec2-user/.env"
#     # }
#     # How to run command can use 2 option:
#     #   - A. Can send .sh file and run --------------------------
#     # copy the deployment.sh from your computer to the ec2 instance
#     # provisioner "file" {
#     #     source      = "D:/personal_proj/mlops/mlops-project/terraform/aws/deployment.sh"
#     #     destination = "/home/ec2-user/deployment.sh"
#     # }

#     # # set permissions and run the build_docker_image.sh file
#     # provisioner "remote-exec" {
#     #     inline = [
#     #         "sudo chmod +x /home/ec2-user/deployment.sh",
#     #         "sh /home/ec2-user/deployment.sh",
#     #     ]
#     # }
#     # ------------------------------------------------------------
#     #   - B. use user_data (in instance)
#     user_data = <<-EOF
#                 #!/bin/bash
#                 yum update -y
#                 amazon-linux-extras install docker -y
#                 service docker start
#                 systemctl enable docker
#                 yum install git
#                 git clone https://github.com/Ar3ee3ar/learn_mlopz.git
#                 EOF

# }

output "instance_ip" {
    value  = aws_instance.ec2_instance.public_ip
}

# print the url of the container
output "container_url" {
    value  = join("", ["http://", aws_instance.ec2_instance.public_dns])
}

