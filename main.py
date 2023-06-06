import boto3
import os
from botocore import exceptions

def create_key(key_name: str) -> None:
    ec2_client = boto3.client("ec2", region_name="eu-north-1")
    key_pair = ec2_client.create_key_pair(KeyName=key_name)

    private_key = key_pair["KeyMaterial"]
    with os.fdopen(os.open(f"{key_name}.pem", os.O_WRONLY | os.O_CREAT, 0o400), "w+") as handle:
        handle.write(private_key)

def create_instance(key_name: str) -> str:
    ec2_client = boto3.client("ec2", region_name="eu-north-1")
    instances = ec2_client.run_instances(ImageId="ami-0989fb15ce71ba39e", MinCount=1, MaxCount=1, InstanceType="t3.micro", KeyName=key_name)
    return instances["Instances"][0]["InstanceId"]

def get_instance_ip(instance_id: str) -> str:
    ec2_client = boto3.client("ec2", region_name="eu-north-1")
    try:
        reservations = ec2_client.describe_instances(InstanceIds=[instance_id]).get("Reservations")
        for reservation in reservations:
            for instance in reservation['Instances']:
                if (instance["State"]["Name"] == "terminated"):
                    raise exceptions.ClientError({"Error":{"Code":500,"Message":"Error"}}, "terminated")
                return instance["PublicIpAddress"]
    except(exceptions.ClientError):
        print(f"Instance with id {instance_id} does not exist")

def get_running_instances() -> list:
    ec2_client = boto3.client("ec2", region_name="eu-north-1")
    reservations = ec2_client.describe_instances(Filters=[{"Name": "instance-state-name","Values": ["running"],},{"Name": "instance-type","Values": ["t3.micro"]}]).get("Reservations")
    instances = []
    for reservation in reservations:
        for instance in reservation["Instances"]:
            instances.append([instance["InstanceId"], instance["InstanceType"], instance["PublicIpAddress"], instance["PrivateIpAddress"]])
    return instances

def stop_instance(instance_id: str) -> None:
    ec2_client = boto3.client("ec2", region_name="eu-north-1")
    try:
        response = ec2_client.stop_instances(InstanceIds=[instance_id])
        if (response["StoppingInstances"][0]["PreviousState"]["Name"] == "running"):
            print(f"Instance with id {instance_id} has been stopped")
        elif (response["StoppingInstances"][0]["PreviousState"]["Name"] == "stopped" or response["StoppingInstances"][0]["PreviousState"]["Name"] == "stopping"):
            print(f"Instance with id {instance_id} already stopped")
    except(exceptions.ClientError):
        print(f"Instance with id {instance_id} does not exist")  

def terminate_instance(instance_id: str) -> None:
    ec2_client = boto3.client("ec2", region_name="eu-north-1")
    try:
        response = ec2_client.terminate_instances(InstanceIds=[instance_id])
        if (response["TerminatingInstances"][0]["PreviousState"]["Name"] == "running" or response["TerminatingInstances"][0]["PreviousState"]["Name"] == "stopped" or response["TerminatingInstances"][0]["PreviousState"]["Name"] == "stopping"):
            print(f"Instance with id {instance_id} has been ternimated")
        elif (response["TerminatingInstances"][0]["PreviousState"]["Name"] == "terminated"):
            print(f"Instance with id {instance_id} already terminated")
    except(exceptions.ClientError):
        print(f"Instance with id {instance_id} does not exist") 

if __name__ == "__main__":
    # create_key("test1")
    # print(create_instance("test2"))
    print(get_instance_ip("i-0fc5e00c2597bbc3d"))
    # print(get_running_instances())
    # stop_instance('i-0fc5e00c2597bbc3d')
    # terminate_instance("i-0fc5e00c2597bbc3d")