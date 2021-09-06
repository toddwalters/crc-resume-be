#!/bin/sh

# This runs the pre_build phase of the build.
#
# To run outside CodeBuild, set the following variables before running:
# CODEBUILD_SRC_DIR
#   Set this to your project's root directory.
# CODEBUILD_SRC_DIR_LintRules
#   Set this to the cfn-lint-rules subdirectory in a local git clone of 
#   https://github.com/toddwalters/waltodders-cfn-lint-rules
# TEMPLATE_PATH
#   Set this to the path to the template.yml file at the root of your project.
#
# Be sure you are logged in to AWS, as this script runs an AWS CLI command.

check_node_code() {
  echo "Checking Node.js code"
  for function_directory in ${CODEBUILD_SRC_DIR}/functions/* ; do
    cd ${function_directory}
    if [ -f "package.json" ]; then
      echo "  Linting ${function_directory}"
      npm run lint
      echo "  Testing ${function_directory}"
      npm test
    fi
  done
}

check_python_code() {
  echo "Checking Python code"
  for function_directory in ${CODEBUILD_SRC_DIR}/functions/* ; do
    cd ${function_directory}
    if [ -f "requirements.txt" ]; then
      echo "  Linting ${function_directory}"
      pylint ${function_directory}
      echo "  Testing ${function_directory}"
      # python -m pytest .
    fi
  done
}

check_cf_template() {
  echo "Linting CloudFormation template"
  cd $CODEBUILD_SRC_DIR
  cfn-lint --version
  # https://github.com/aws-cloudformation/cfn-python-lint/issues/1265#issuecomment-568525313
  cfn-lint --ignore-checks W3011 --template ${TEMPLATE_PATH}
}

echo "Starting pre_build - $(date)"
STARTING_DIR=$PWD
set -xe

check_node_code
check_python_code
check_cf_template

cd $STARTING_DIR
unset STARTING_DIR
echo "Completed pre_build - $(date)"
