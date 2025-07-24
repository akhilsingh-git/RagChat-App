# lambda.tf

# Configure the AWS provider
provider "aws" {
  region = "ap-south-1" # You can change this to your preferred region
}

# 1. IAM Role for Lambda Execution
# This role grants the Lambda function permission to run and write logs.
resource "aws_iam_role" "rag_lambda_role" {
  name = "rag-app-lambda-execution-role"

  assume_role_policy = jsonencode({
    Version   = "2012-10-17",
    Statement = [{
      Action    = "sts:AssumeRole",
      Effect    = "Allow",
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

# Attach the basic Lambda execution policy to the role
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.rag_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# 2. Package the Application Code
# This data source zips the entire project directory for deployment.
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}"
  output_path = "${path.module}/lambda_payload.zip"
  # Exclude files not needed in the Lambda package to reduce size
  excludes = [
    "lambda.tf",
    "main.tf",
    ".git",
    ".github",
    "__pycache__",
    "README.md"
  ]
}

# 3. Create the Lambda Function
resource "aws_lambda_function" "rag_app_lambda" {
  function_name = "RAG-App-Function"
  role          = aws_iam_role.rag_lambda_role.arn
  handler       = "api.index.app" # The path to the FastAPI app instance
  runtime       = "python3.11"
  timeout       = 30 # Set timeout to 30 seconds

  # Use the 'filename' attribute to point to the zip file
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  # Use Lambda container image for dependencies
  package_type = "Zip"

  environment {
    variables = {
      # Pass environment variables to the Lambda function
      DATABASE_URL             = var.database_url
      HUGGING_FACE_API_TOKEN   = var.hugging_face_api_token
    }
  }
}

# 4. Create the API Gateway to trigger the Lambda
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
  route_key = "ANY /{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.rag_api_integration.id}"
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

# 6. Output the API Gateway URL
output "api_endpoint_url" {
  value = aws_apigatewayv2_api.rag_api.api_endpoint
}
