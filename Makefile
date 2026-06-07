.PHONY: venv install lint clean build deploy test

# Détection de l'OS
ifeq ($(OS),Windows_NT)
    PYTHON = venv/Scripts/python
    PIP = venv/Scripts/pip
    PYTHON_CMD = python
    RM_RF = rmdir /s /q
else
    PYTHON = venv/bin/python
    PIP = venv/bin/pip
    PYTHON_CMD = python3
    RM_RF = rm -rf
endif

AWS_REGION = eu-west-3
ENVIRONMENT = yadjassem
TEMPLATE = infrastructure/template.yaml
STACK_NAME = exam-iot-stack-$(ENVIRONMENT)

venv:
	@echo "Setting up virtual environment..."
	$(PYTHON_CMD) -m venv venv

install: venv
	@echo "Installing dependencies..."
	$(PIP) install -r requirements.txt

clean:
	@echo "Cleaning up..."
	$(RM_RF) .aws-sam

build:
	@echo "Building SAM application..."
	sam build --use-container --region $(AWS_REGION) --template-file $(TEMPLATE)

deploy: build
	@echo "Deploying to AWS..."
	sam deploy --resolve-s3 \
		--region $(AWS_REGION) \
		--stack-name $(STACK_NAME) \
		--template-file .aws-sam/build/template.yaml \
		--no-fail-on-empty-changeset \
		--parameter-overrides Environment=$(ENVIRONMENT) \
		--capabilities CAPABILITY_NAMED_IAM

test:
	@echo "Running test client..."
	$(PYTHON) test_client.py

upload-doc:
	@echo "Uploading documentation to S3..."
	aws s3 cp docs/index.html s3://exam-iot-tech-doc-$(ENVIRONMENT)/index.html --region $(AWS_REGION)
