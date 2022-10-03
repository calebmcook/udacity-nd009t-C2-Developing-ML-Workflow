###LAMBDA FUNCTION 1: serializeImageData
import json
import boto3
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""
    
    # Get the s3 address from the Step Function event input
    key = event["s3_key"] ## TODO: fill in
    bucket = event["s3_bucket"]
    
    # Download the data from s3 to /tmp/image.png
    ## TODO: fill in
    s3.download_file(bucket, key,"/tmp/image.png")
    
    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read())
    
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
       }
    }

###LAMBDA FUNCTION 2: classification2
import json
import boto3
import base64

def lambda_handler(event, context):
    
    # Fill this in with the name of your deployed model
    ENDPOINT = "image-classification-2022-10-03-18-26-00-794"

    # Decode the image data
    image = base64.b64decode(event["body"]["image_data"])

    ###
    ## REFERENCE: https://knowledge.udacity.com/questions/760135
    ## I borrowed from the comment within this question thread from Peter, in below use of invoke_endpoint and boto3 
    runtime = boto3.client('runtime.sagemaker')
    response = runtime.invoke_endpoint(
        EndpointName=ENDPOINT,
        ContentType='image/png',
        Body=image)
    
    event["body"]["inferences"] = response['Body'].read().decode("utf-8")

    #return {
    #    'statusCode': 200,
    #    'body': json.dumps(event)
    #}
    
    return event

###LAMBDA FUNCTION 3: filterInferences
import json

THRESHOLD = .70

def lambda_handler(event, context):
    
    # Grab the inferences from the event
    inferences_str = event["body"]["inferences"]
    y = inferences_str[1:-1].split(',')
    inferences = [float(i) for i in y]
    
    # Check if any values in our inferences are above THRESHOLD
    meets_threshold = any([inf > THRESHOLD for inf in inferences])  ## TODO: fill in
    
    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        pass
    else:
        raise("THRESHOLD_CONFIDENCE_NOT_MET")

    return json.dumps(event)