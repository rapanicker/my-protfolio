import json
import boto3
import StringIO
import zipfile
import mimetypes

def lambda_handler(event, context):

    sns = boto3.resource('sns')
    topic = sns.Topic("arn:aws:sns:us-east-1:230290740745:deployportfolio")

    try:
        s3 = boto3.resource('s3')
        portfolio_bucket = s3.Bucket('panicktestsite.com')
        build_bucket = s3.Bucket('myportfolio.panicktestsite.com')

        portfolio_zip = StringIO.StringIO()
        build_bucket.download_fileobj('portfoliobuild.zip', portfolio_zip)

        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj, nm,
                  ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')

        print "Job Done!"
        topic.publish(Subject="Deployed Task", Message="Portfolio Update Successful")

    except:
        topic.publish(Subject="DeploymentFailed", Message="Portfolio update Unsuccessful!")
        raise

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

    
