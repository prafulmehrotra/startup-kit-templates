""" Paravirtualization
"""

import boto3, botocore, sys, os
from botocore.client import Config

def get_regions(client):
    """ Load the region codes
    """
    response = client.describe_regions()
    regions = []
    for region in response['Regions']:
        regions.append(region['RegionName'])
    return regions

def bastion_ami(session, config, region):
	final = []
	ami_filters= [
	{'Name':'virtualization-type','Values':['hvm']},
	{'Name':'hypervisor','Values':['xen']},
	{'Name':'owner-alias','Values':['amazon']},
	{'Name':'ena-support','Values':['true']},
	{'Name':'sriov-net-support','Values':['simple']},
	{'Name':'state','Values':['available']},
	{'Name':'architecture','Values':['x86_64']},
	{'Name':'root-device-type','Values':['ebs']},
	{'Name':'root-device-name','Values':['/dev/xvda']},
	{'Name':'image-type','Values':['machine']},
	{'Name':'is-public','Values':['true']},
	{'Name':'block-device-mapping.volume-type','Values':['gp2']},
	{'Name':'block-device-mapping.volume-size','Values':['8']},
	{'Name':'block-device-mapping.delete-on-termination','Values':['true']},
	{'Name':'block-device-mapping.device-name','Values':['/dev/xvda']}]

	ec2_client = session.client('ec2', region_name=region, config= config)
	amis =  ec2_client.describe_images(ExecutableUsers=['all'], Owners=['amazon'], Filters = ami_filters)['Images']
	print len(amis)

	for ami in amis:
		if 'elasticbeanstalk' not in ami['Name'] and 'ecs' not in ami['Name'] and 'amzn2' not in ami['Name']:
			final.append(ami)

	print len(final)
 	sort_on = 'CreationDate'
	decorated = [(dict_[sort_on], dict_) for dict_ in final]
	decorated.sort(reverse=True)
	result = [dict_ for (key, dict_) in decorated]
	print result[0]['ImageId']
	print result[1]['ImageId']
	print result[2]['ImageId']

def main():

    config = Config(connect_timeout=60, read_timeout=60)
    session = boto3.Session(profile_name=None if len(sys.argv) < 2 else sys.argv[1])
    
    print 'Get AMI for every region'
    for region in get_regions(session.client('ec2', region_name= 'us-east-1', config= config)):
    	print region
    	bastion_ami(session, config, region)
    
if __name__ == '__main__':
    main()


