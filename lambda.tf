# lambda.tf

# Configure the AWS provider
provider "aws" {
  region = "ap-south-1"
}

# 1. IAM Role for Lambda Execution (no changes here)
resource "aws_iam_role" "rag_lambda_role" {
  name = "rag-app-lambda-execution-role"
  assume_role_policy = jsonencode({
    Version   = "2012-10-17",
    Statement = [{
      Action    = "sts:AssumeRole",
      Effect    = "Allow",
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.rag_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# 2. ECR Repository to store the Lambda container image
resource "aws_ecr_repository" "rag_app_ecr" {
  name                 = "rag-app-lambda"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }
}

# 3. Create the Lambda Function from a Container Image
resource "aws_lambda_function" "rag_app_lambda" {
  function_name = "RAG-App-Function"
  role          = aws_iam_role.rag_lambda_role.arn
  package_type  = "Image"
  timeout       = 60
  memory_size   = 2048
  image_uri     = var.image_uri

  environment {
    variables = {
      DATABASE_URL             = var.database_url
      HUGGING_FACE_API_TOKEN   = var.hugging_face_api_token
    }
  }
}

# 4. API Gateway resources
resource "aws_apigatewayv2_api" "rag_api" {
  name          = "RAG-App-API"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "rag_api_integration" {
  api_id           = aws_apigatewayv2_api.rag_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.rag_app_lambda.invoke_arn
}

resource "aws_apigatewayv2_route" "rag_api_route" {
  api_id    = aws_apigatewayv2_api.rag_api.id
  route_key = "$default" # Use the $default route for a simple API
  target    = "integrations/${aws_apigatewayv2_integration.rag_api_integration.id}"
}

# --- NEW: Create the API Gateway Stage ---
# This is the crucial missing piece that makes the API live.
resource "aws_apigatewayv2_stage" "rag_api_stage" {
  api_id      = aws_apigatewayv2_api.rag_api.id
  name        = "$default" # The default stage is automatically invoked
  auto_deploy = true
}

resource "aws_lambda_permission" "api_gateway_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.rag_app_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.rag_api.execution_arn}/*/*"
}

# 5. Define input variables for secrets
variable "database_url" {
  description = "The connection string for the Neon database."
  type        = string
  sensitive   = true
}

variable "hugging_face_api_token" {
  description = "The API token for Hugging Face."
  type        = string
  sensitive   = true
}

variable "image_uri" {
  description = "The URI of the Docker image in ECR."
  type        = string
}

# 6. UPDATED: Output the final, public URL
output "api_endpoint_url" {
  value = aws_apigatewayv2_stage.rag_api_stage.invoke_url
}
