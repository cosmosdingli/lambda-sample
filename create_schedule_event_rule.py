import boto3
import json
import uuid
from datetime import datetime,timedelta

events_client = boto3.client('events')            
lambda_client = boto3.client('lambda')

def create_rule(**args):

    TIMESTAMP_FORMAT = "%Y-%m-%dT%H-%M-%S.%f"
    
    ct = datetime.now() + timedelta(minutes=2)
    rule_name = 'cwr-{}.{}'.format('xxxxx', ct.strftime(TIMESTAMP_FORMAT))
    response = events_client.put_rule(
        Name=rule_name,
        ScheduleExpression=f"cron({ct.minute} {ct.hour} {ct.day} {ct.month} ? {ct.year})",
        State='ENABLED'
    )
    
    lambda_arn = 'arn:aws:lambda:{}:{}:function:{}'.format(args['region'], args['account'], args['lambda_id'])
    lambda_input = {
        "region": args['region'],
        "account": args['account'],
        "rule_name": rule_name,
        "lambda_id": args['lambda_id'],
        "value": args['value']
    }
    events_client.put_targets(
        Rule=rule_name,
        Targets=[{
                    'Arn': lambda_arn,
                    'Id': args['lambda_id'],
                    'Input': json.dumps(lambda_input)
        }]
    )
    
    lambda_client.add_permission(
        FunctionName=args['lambda_id'],
        StatementId=str(uuid.uuid4()),
        Action="lambda:InvokeFunction",
        Principal='events.amazonaws.com',
        SourceArn=response['RuleArn']
    )

'''
{
  "region": "ap-northeast-1",
  "account": "123456789012"
}
'''
def lambda_handler(event, context):
    create_rule(lambda_id = 'lmd-create-event-rule',
                region = event['region'],
                account = event['account'],
                value = 'aa')
