output "api_gateway_url" {
  description = "URL publica del API Gateway"
  value       = "${aws_apigatewayv2_api.main.api_endpoint}/process"
}

output "s3_bucket_name" {
  description = "Nombr del bucket S3"
  value       = aws_s3_bucket.results.bucket
}

output "redis_endpoint" {
  description = "Endpoint de Redis"
  value       = aws_elasticache_cluster.redis.cache_nodes[0].address
}

output "lambda_function_name" {
  description = "Nombre de la funcion Lambda"
  value       = aws_lambda_function.processor.function_name
}
