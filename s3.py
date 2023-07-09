import boto3

class S3Executor:
    def __init__(self):
        self.s3 = boto3.resource(service_name='s3')
        try:
            self.bucket_name = open("/home/ec2-user/webConfig/bucket_name.txt").readline().strip()
        except FileNotFoundError:
            print("Bucket name not found!")

    def post(self, key, data):
        try:
            self.s3.Bucket(self.bucket_name).put_object(Key=key, Body=data)
            return True
        except Exception:
            return False

    def get(self, key):
        try:
            obj = self.s3.Object(bucket_name=self.bucket_name, key=key).get()
            return obj
        except Exception:
            return None

    def delete(self, key):
        _dic = {'Objects': [{'Key': key}],
                  'Quiet': True | False}
        try:
            self.s3.Bucket(self.bucket_name).delete_objects(Delete=_dic)
            return True
        except Exception:
            return False