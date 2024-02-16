import boto3
import csv
import datetime

def get_account_details():
    """Retrieves details of all AWS accounts within the organization."""
    org_client = boto3.client('organizations')
    tagging_client = boto3.client('resourcegroupstaggingapi')

    accounts = []
    paginator = org_client.get_paginator('list_accounts')
    for page in paginator.paginate():
        for account in page['Accounts']:
            try:
                tags_response = tagging_client.get_resources(
                    ResourceARNList=[account['Arn']]
                )
                tags = tags_response['ResourceTagMappingList'][0].get('Tags', [])
            except Exception:
                tags = []

            accounts.append({
                'Account ID': account['Id'],
                'Name': account.get('Name', 'No Alias'),
                'ARN': account['Arn'],
                'Email': account['Email'],
                'Created Date': account['JoinedTimestamp'].strftime('%Y-%m-%d'),
                'Tags': tags
            })

    return accounts

def get_bucket_details(account_id):
    """Fetches S3 bucket details for a given account."""
    session = boto3.Session(profile_name=None)  # Adjust if using profiles
    s3_client = session.client('s3', region_name='us-east-1')  # Replace if needed
    buckets = []

    try:
        response = s3_client.list_buckets()
        for bucket in response['Buckets']:
            try:
                region = s3_client.get_bucket_location(Bucket=bucket['Name'])['LocationConstraint'] or 'None'
                tags = s3_client.get_bucket_tagging(Bucket=bucket['Name'])['TagSet']
            except Exception as e:
                print(f"Error getting region or tags for bucket {bucket['Name']}: {e}")
                region = 'None'
                tags = []

            buckets.append({
                'Account ID': account_id,
                'Bucket Name': bucket['Name'],
                'Bucket Region': region,
                'Resource ID (ARN)': f'arn:aws:s3:::{bucket["Name"]}',
                'Creation Date': bucket['CreationDate'].strftime('%Y-%m-%d'),
                'Tags': tags
            })
    except Exception as e:
        print(f"Error listing buckets for account {account_id}: {e}")

    return buckets

def export_details_to_csv(data, filename='core_resource_details.csv'):
    """Exports data to a CSV file."""
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

if __name__ == '__main__':
    all_account_details = get_account_details()

    all_resource_details = []
    for account in all_account_details:
        all_resource_details.extend(get_bucket_details(account['Account ID']))

    export_details_to_csv(all_resource_details)
