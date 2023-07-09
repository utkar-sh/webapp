variable "aws_region" {
  type    = string
  default = "us-west-2"
}

variable "source_ami" {
  type    = string
  default = "ami-0f1a5f5ada0e7da53" # Ubuntu 22.04 LTS as of 10/19/2022
}

variable "ssh_username" {
  type    = string
  default = "ubuntu"
}

variable "subnet_id" {
  type    = string
  default = "subnet-02992e69b27fb93d3" # Default subnet in default VPC
}

# https://www.packer.io/plugins/builders/amazon/ebs
source "amazon-ebs" "ubuntu-ami" {
  region                  = "${var.aws_region}"
  ami_name                = "csye6225_${formatdate("YYYY_MM_DD_hh_mm_ss", timestamp())}"
  ami_description         = "AMI for CSYE 6225"
  shared_credentials_file = "C:/Users/weasel/.aws/credentials"
  profile                 = "dev"

  ami_users = [
    "327836084619",
    "531886003212"
  ]

  ami_regions = [
    "us-west-2",
  ]

  aws_polling {
    delay_seconds = 120
    max_attempts  = 50
  }


  instance_type = "t2.micro"
  source_ami    = "${var.source_ami}"
  ssh_username  = "${var.ssh_username}"
  subnet_id     = "${var.subnet_id}"

  launch_block_device_mappings {
    delete_on_termination = true
    device_name           = "/dev/sda1"
    volume_size           = 50
    volume_type           = "gp2"
  }
}

build {
  sources = ["source.amazon-ebs.ubuntu-ami"]

  provisioner "file" {
    source      = "./"
    destination = "/tmp/"
  }

  provisioner "shell" {
    environment_vars = [
      "DEBIAN_FRONTEND=noninteractive",
      "CHECKPOINT_DISABLE=1"
    ]
    script = "scripts/setup.sh"
  }

  post-processor "manifest" {
    output     = "ami.json"
    strip_path = true
  }
}
