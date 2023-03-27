import boto3
import os
from sqlalchemy.engine.url import URL


def get_rds_url():
    rds = boto3.client('rds', region_name='your-region',
                       aws_access_key_id='your-access-key', aws_secret_access_key='your-secret-key')
    db_instance = rds.describe_db_instances(
        DBInstanceIdentifier='your-db-instance-identifier')
    db_instance_data = db_instance['DBInstances'][0]
    host = db_instance_data['Endpoint']['Address']
    port = db_instance_data['Endpoint']['Port']
    db_url = URL(drivername='postgresql+psycopg2', username=os.environ.get('DB_USER'),
                 password=os.environ.get('DB_PASSWORD'), host=host, port=port, database=os.environ.get('DB_NAME'))
    return db_url
