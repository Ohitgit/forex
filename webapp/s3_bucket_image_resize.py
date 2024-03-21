import boto3

def convert_mb_to_kb(bucket_name, image_prefix):
    s3_client = boto3.client('s3')

    # Retrieve objects from the S3 bucket
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=image_prefix)

    for obj in response.get('Contents', []):
        # Get the image size in MB
        image_size_mb = obj['Size'] / (1024 * 1024)

        # Convert the image size from MB to KB
        image_size_kb = image_size_mb * 1024

        # Print the result
        print("Image: {} - Size: {:.2f} KB".format(obj['Key'], image_size_kb))


# Example usage
bucket_name = 'aroundmebucket'
image_prefix = 'images/'
convert_mb_to_kb(bucket_name, image_prefix)
