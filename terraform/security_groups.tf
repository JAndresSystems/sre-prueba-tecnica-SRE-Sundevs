resource "aws_security_group" "lambda" {
  name        = "${var.project_name}-sg-lambda"
  description = "Security group para Lambda"
  vpc_id      = aws_vpc.main.id


  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Pemite todo el trafico saliente"
  }

  tags = {
    Name = "${var.project_name}-sg-lambda"
  }
}


resource "aws_security_group" "redis" {
  name        = "${var.project_name}-sg-redis"
  description = "Security group para Redis"
  vpc_id      = aws_vpc.main.id


  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.lambda.id]
    description     = "Permitee acceso a Redis solo desde Lambda"
  }

  tags = {
    Name = "${var.project_name}-sg-redis"
  }
}
