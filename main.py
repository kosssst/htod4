import boto3
import os
from botocore import exceptions
import pandas

def create_key(key_name: str) -> None:
    ec2_client = boto3.client("ec2", region_name="eu-north-1")
    key_pair = ec2_client.create_key_pair(KeyName=key_name)

    private_key = key_pair["KeyMaterial"]
    with os.fdopen(os.open(f"{key_name}.pem", os.O_WRONLY | os.O_CREAT, 0o400), "w+") as handle:
        handle.write(private_key)

def create_instance(key_name: str) -> str:
    try:
        ec2_client = boto3.client("ec2", region_name="eu-north-1")
        instances = ec2_client.run_instances(ImageId="ami-0989fb15ce71ba39e", MinCount=1, MaxCount=1, InstanceType="t3.micro", KeyName=key_name)
        return instances["Instances"][0]["InstanceId"]
    except exceptions.ClientError:
        print(f"Invalid key name: {key_name}")

def get_instance_ip(instance_id: str) -> str:
    ec2_client = boto3.client("ec2", region_name="eu-north-1")
    try:
        reservations = ec2_client.describe_instances(InstanceIds=[instance_id]).get("Reservations")
        for reservation in reservations:
            for instance in reservation['Instances']:
                if (instance["State"]["Name"] == "terminated"):
                    raise Exception("terminated")
                if (instance["State"]["Name"] == "stopped" or instance["State"]["Name"] == "stopping"):
                    raise Exception("stopped")
                return instance["PublicIpAddress"]
    except(exceptions.ClientError):
        print(f"Instance with id {instance_id} does not exist")
    except Exception as e:
        if (str(e) == "terminated"):
            print(f"Instance with id {instance_id} is terminated")
        if (str(e) == "stopped"):
            print(f"Instance with id {instance_id} is stopped")

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

def create_bucket(name: str) -> None:
    s3_client = boto3.client("s3", region_name="eu-north-1")
    location = {"LocationConstraint": "eu-north-1"}
    try:
        response = s3_client.create_bucket(Bucket=name, CreateBucketConfiguration=location)
        print("Bucket created")
    except exceptions.ClientError:
        print("Invalid bucket name")

def list_of_buckets() -> list:
    s3_client = boto3.client("s3", region_name="eu-north-1")
    try:
        response = s3_client.list_buckets()
        return [bucket["Name"] for bucket in response["Buckets"]]
    except Exception as e:
        print(str(e))

def upload(file_name: str, bucket_name: str, obj_name: str) -> None:
    s3_client = boto3.client("s3", region_name="eu-north-1")
    try:
        response = s3_client.upload_file(Filename=file_name, Bucket=bucket_name, Key=obj_name)
    except Exception as e:
        print(str(e))

def get_file(bucket_name: str, key: str) -> None:
    s3_client = boto3.client("s3", region_name="eu-north-1")
    try:
        obj = s3_client.get_object(Bucket=bucket_name, Key=key)
        print(pandas.read_csv(obj["Body"]).head())
    except Exception as e:
        print(str(e))

def destroy_bucket(bucket_name: str) -> None:
    s3_client = boto3.client('s3', region_name="eu-north-1")
    try:
        response = s3_client.delete_bucket(Bucket=bucket_name)
    except Exception as e:
        print(str(e))

if __name__ == "__main__":
    # create_key("test1")
    # print(create_instance("test2"))
    # print(get_instance_ip("i-0fc5e00c2597bbc3d"))
    # print(get_running_instances())
    # stop_instance('i-0fc5e00c2597bbc3d')
    # terminate_instance("i-0fc5e00c2597bbc3d")
    # create_bucket("bucketforbototesting2")
    # print(list_of_buckets())
    # upload(".gitignore", "bucketforbototesting", "git")
    # get_file("bucketforbototesting", "git")
    destroy_bucket("bucketforbototesting2")