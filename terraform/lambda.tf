resource "aws_lambda_function" "processor" {
  filename         = "../lambda/function.zip"
  function_name    = "${var.project_name}-processor"
  role             = aws_iam_role.lambda.arn
  handler          = "handler.handler"
  runtime          = "python3.12"
  timeout          = 30

 
  environment {
    variables = {
      REDIS_HOST     = aws_elasticache_cluster.redis.cache_nodes[0].address
      REDIS_PORT     = "6379"
      S3_BUCKET_NAME = aws_s3_bucket.results.bucket
    }
  }

 
  vpc_config {
    subnet_ids         = [
      aws_subnet.private_a.id,
      aws_subnet.private_b.id
    ]
    security_group_ids = [aws_security_group.lambda.id]
  }

  tags = {
    Name = "${var.project_name}-processor"
  }
}


resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${var.project_name}-processor"
  retention_in_days = 7

  tags = {
    Name = "${var.project_name}-lambda-logs"
  }
}
