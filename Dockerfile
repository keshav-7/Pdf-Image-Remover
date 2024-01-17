# FROM amazonlinux:2 AS builder

# RUN yum install -y poppler-utils

# Second stage: Build the final image
FROM public.ecr.aws/lambda/python:3.12
WORKDIR /report_image_remover
# Copy Poppler binaries from the builder stage
# COPY --from=builder /usr/bin/pdftoppm /usr/bin/pdftoppm /var/task /var/lang/lib /opt/poppler/lib
# COPY --from=builder /opt/poppler-21.12.0 /opt/poppler

# Set the environment variable to include Poppler in the library path and the PATH to include Poppler binaries
# ENV LD_LIBRARY_PATH=/opt/poppler/lib \
#     PATH="/opt/poppler/bin:${PATH}"

# Copy your Lambda function code and requirements
COPY lambda_function.py requirements.txt ${LAMBDA_TASK_ROOT}/

# COPY . ${LAMBDA_TASK_ROOT}/
COPY . /var/task

# Install Python dependencies
RUN pip3 install --no-cache-dir -r ${LAMBDA_TASK_ROOT}/requirements.txt --target "${LAMBDA_TASK_ROOT}"
# RUN pip3 install --use-pep517 python-poppler

# Set the CMD to your handler
CMD [ "lambda_function.lambda_handler" ]

# Expose port (it's not used by AWS Lambda, but included for reference)
EXPOSE 3000

# ARG AWS_ACCESS_KEY_ID
# ARG AWS_SECRET_ACCESS_KEY
# ARG AWS_DEFAULT_REGION
# ARG AWS_S3_ENDPOINT_URL

# ENV AWS_ACCESS_KEY_ID ${AWS_ACCESS_KEY_ID}
# ENV AWS_SECRET_ACCESS_KEY ${AWS_SECRET_ACCESS_KEY}
# ENV AWS_DEFAULT_REGION ${AWS_DEFAULT_REGION}
# ENV AWS_S3_ENDPOINT_URL ${AWS_S3_ENDPOINT_URL}