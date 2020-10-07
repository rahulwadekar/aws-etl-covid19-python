Event-Driven Python on AWS- #CloudGuruChallenge
Automate an ETL processing CI/CD pipeline for COVID-19 data using Python and cloud services.

What is the Challenge?

The challenge is to implement a event driven Python ETL processing job which will run daily. It will download and process US Covid19 data from different data sources and create a dashboard to visualize the same using AWS QuickSight.

Approach and Steps towards problem solving

ETL Job: Created a Lambda function in Python as asked by author and scheduled it as a daily job with the help of CloudWatch events rules.

Extraction & Transformation: We need to download two CSV files from different urls through Python Lambda code,   which i did by using pandas Python library. Converted the columns like date into proper format using separate Python transformation module. Filtered the dataframes only for US data as asked and kept only those columns which are required(date, cases, deaths, recovered). Merged two data sets into one and same data is loaded into a database in the next step.

Load: Transformed and well formatted data which is returned by above Python module is then loaded into a PostgreSQL RDS instance. Initially i loaded data into DynamoDB but later on realized that there is no direct integration for DynamoDB as a data source with Quicksight. Tried inserting the same data as a JSON file into S3 and generated a dashboard with it in QuickSight also. Thought of using DynamoDB streams also to load daily data and update the JSON file in S3. But appending the JSON file in S3 daily seemed to be not an optimal solution so ended up inserting data into PostgreSQL RDS instance.

Notifications: Notifications have been configured on successfully completion of the ETL job and communicating the number of records inserted into the database daily in email. Any other failures or exceptions in Lambda code will also be notified using SNS topic and an email will be sent through SNS subscription.

Infrastructure as Code: Implemented a CloudFormation template for all the AWS resources used and same is also integrated with the CI/CD pipeline which will update the infrastructure as needed when any code changes are pushed to the code repository. Refer CloudFormation template here.

CI/CD Pipeline: Automated CI/CD pipeline has been setup using the CloudFormation template and AWS resources such as CodePipeline, CodeBuild, CodeDeploy etc.. Pipeline will be triggered as and when code is pushed to the code repository. It has 3 stages Source, Build and Deploy. Build stage will use below command to package the Lambda function code and generate a output template yaml file. The packaged code will be deployed as a Python Lambda function.

aws cloudformation package - template-file etl-covid19-cloudformation.yml - s3-bucket cloud-guru-challenge-etl-lambda-code-rahul - output-template-file output.yml

Data inserted can me mapped with any visualization tool of your choice.

Conclusion:

It is a very interesting challenge by Forrest Brazeal and I am literally amazed about the amount of AWS learning and practical experience it has given to me :) It was great learning experience and I would really appreciate any feedback or comments regarding the approach and the blog.
Thank you :)
