import boto3
import csv

def get_all_accounts():
    """Retrieves a list of all AWS account IDs within the organization"""
    org_client = boto3.client('organizations')
    accounts = []

    try:
        response = org_client.list_accounts()
        accounts.extend(response.get('Accounts', []))

        while 'NextToken' in response:
            response = org_client.list_accounts(NextToken=response['NextToken'])
            accounts.extend(response.get('Accounts', []))
    except Exception as e:
        print(f"An error occurred retrieving account IDs: {e}")

    return [account['Id'] for account in accounts]

def get_vpc_details(account_id):
    """Fetches VPC details for a given account"""
    ec2_client = boto3.client('ec2')
    vpcs = []

    try:
        response = ec2_client.describe_vpcs()
        for vpc in response['Vpcs']:
            vpc_id = vpc['VpcId']
            vpc_name = ''
            for tag in vpc.get('Tags', []):
                if tag['Key'] == 'Name':
                    vpc_name = tag['Value']
                    break
            
            vpcs.append({
                'Account ID': account_id,
                'VPC Name': vpc_name,
                'VPC ID': vpc_id,
                'CIDR Block': vpc['CidrBlock'],
                'Region': boto3.session.Session().region_name,
                'Availability Zones': [zone['ZoneName'] for zone in vpc['AvailabilityZones']],
                'State': vpc['State']
            })
    except Exception as e:
        print(f"Error listing VPCs for account {account_id}: {e}")

    return vpcs

def export_details_to_csv(data, filename='vpc_details.csv'):
    """Exports data to a CSV file"""
    if not data:
        print("No resource details found.")
        return

    with open(filename, 'w', newline='') as csvfile:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

if __name__ == '__main__':
    all_vpc_details = []

    all_accounts = get_all_accounts()
    for account_id in all_accounts:
        all_vpc_details.extend(get_vpc_details(account_id))

    export_details_to_csv(all_vpc_details)
