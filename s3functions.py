import boto3
from configparser import ConfigParser
from botocore.exceptions import ClientError
import os

# HELPER FUNCTIONS_____________________________________________


def bucketExist(s3, bucketArg):
    try:
        for bucket in s3.buckets.all():
            if bucket.name == bucketArg:
                return True
    except:
        return False

    return False


def objectExist(s3, bucketname, path):

    if(len(path) == 0):
        return True
    lastSlash = ''
    if(path[-1] != '/'):
        lastSlash = '/'

    bucket = s3.Bucket(bucketname)

    for object_summary in bucket.objects.filter(Prefix=path + lastSlash):
        return True
    return False


def getRelativePath(currPath, directions):
    currPath = [s for s in currPath if s != '']
    directions = [s for s in directions if s != '']

    for s in directions:
        if(s == '..' and len(currPath) > 0):
            currPath.pop()
        elif(s != '..'):
            currPath.append(s)

    newPath = ''
    for s in currPath:
        newPath = newPath + s + '/'

    return newPath


def deleteIfObjectIsEmpty(s3, deleteLocation, isRelativePath, bucketAndPath):
    if isRelativePath:
        my_bucket = s3.Bucket(bucketAndPath[0])
    else:
        my_bucket = s3.Bucket(deleteLocation[0])

    pathIndex = 0 if isRelativePath else 1
    pathSting = deleteLocation if isRelativePath else deleteLocation[1]
    deleteLocationSplit = []
    deleteString = ''

    for s in pathSting.split('/'):
        if len(s) > 0:
            deleteLocationSplit.append(s)

    for s in deleteLocationSplit:
        deleteString = deleteString + s + ('/' if "." not in s else '')

    count = 0
    tempObj = ''
    for object_summary in my_bucket.objects.filter(Prefix=deleteString):
        count = count + 1
        tempObj = object_summary.key

    if count == 1:  # and (len(deleteString)-len(tempObj) == 0):
        my_bucket.objects.filter(Prefix=deleteString).delete()
        return True

    return False

# MAIN FUNCTIONS_____________________________________________


def authenticate():
    print("Welcome to the AWS S3 Storage Shell (S5)")

    parser = ConfigParser()
    parser.read('S5-S3conf')

    for section_name in parser.sections():
        username = section_name

        for name, value in parser.items(section_name):
            if name == 'aws_access_key_id':
                aws_access_key_id = value
            if name == 'aws_secret_access_key':
                aws_secret_access_key = value

        break

    if len(username) == 0 or len(aws_access_key_id) == 0 or len(aws_secret_access_key) == 0:
        print('You could not be connected to your S3 storage\nPlease review procedures for authenticating your account on AWS S3')
        return 1

    return [username, aws_access_key_id, aws_secret_access_key]


def authenticateClient(credentials):

    s3 = boto3.client(
        's3',
        aws_access_key_id=credentials[1],
        aws_secret_access_key=credentials[2]
    )

    # test to see if successfull authenticated
    try:
        response = s3.list_buckets()
    except ClientError as e:
        print('You could not be connected to your S3 storage\nPlease review procedures for authenticating your account on AWS S3')
        return 1

    return s3


def authenticateResource(credentials):
    s3 = boto3.resource(
        's3',
        aws_access_key_id=credentials[1],
        aws_secret_access_key=credentials[2]
    )

    try:
        response = s3.buckets.all()
    except ClientError as e:
        print('You could not be connected to your S3 storage\nPlease review procedures for authenticating your account on AWS S3')
        return 1
    return s3


def lcCopy(args, s3, currPath):
    try:
        lc_file = args[1]
        cl_file = args[2].split(":")
        if(len(cl_file) == 2):
            bucket = cl_file[0]
            cl_path = cl_file[1]
            s3.upload_file(lc_file, bucket, cl_path)
        elif(len(cl_file) == 1):
            currBucketPath = currPath.split(':')
            newPath = getRelativePath(
                currBucketPath[1].split('/'), cl_file[0].split('/'))

            if(len(newPath) > 0):
                newPath = newPath[:-1]
            s3.upload_file(lc_file, currBucketPath[0], newPath)
        else:
            raise Exception

    except Exception as e:
        print("\nUnsuccessful copy")
        print("Error: ", e)
        print("expected argument example:")
        print(
            "lc_copy <full or relative pathname of local file> <bucket name>:<full pathname of S3 object>")
        print()

        return 1
    return 0


def clCopy(args, s3, currPath, s3_resource):
    try:
        lc_file = args[2]
        cl_file = args[1].split(":")
        if(len(cl_file) == 2):
            bucket = cl_file[0]
            cl_path = cl_file[1]
            s3.download_file(bucket, cl_path, lc_file)
        elif(len(cl_file) == 1):
            currBucketPath = currPath.split(':')

            try:
                s3.download_file(
                    currBucketPath[0], cl_file[0], lc_file)
                return 0
            except:
                newPath = getRelativePath(
                    currBucketPath[1].split('/'), cl_file[0].split('/'))

                if(len(newPath) > 0):
                    newPath = newPath[:-1]

                s3.download_file(
                    currBucketPath[0], newPath, lc_file)
        else:
            raise Exception
    except Exception as e:
        print("\nUnsuccessful copy")
        print("Error: ", e)
        print("expected argument example:")
        print(
            "cl_copy <bucket name>:<full pathname of S3 file> <full pathname of the local file>")
        print(
            "cl_copy <full or relative pathname of S3 file> <full pathname of the local file>")
        print()

        return 1

    return 0


def createBucket(args, s3):
    try:
        bucket = args[1]
        s3.create_bucket(Bucket=bucket, CreateBucketConfiguration={
            'LocationConstraint': 'us-east-2',
        },)
    except:
        print("\nCannot create bucket")
        print("expected argument example:")
        print("create_bucket <bucket name>")
        print()

        return 1

    return 0


def createFolder(args, currPath, s3):
    try:
        cl_file = args[1].split(":")
        if(len(cl_file) == 2):
            bucket = cl_file[0]
            cl_path = cl_file[1]
            s3.put_object(Bucket=bucket, Key=(cl_path+'/'))
        elif(len(cl_file) == 1):
            currBucketPath = currPath.split(':')
            newPath = getRelativePath(
                currBucketPath[1].split('/'), cl_file[0].split('/'))

            s3.put_object(Bucket=currBucketPath[0], Key=(newPath))
        else:
            raise Exception
    except Exception as e:
        print("\nCannot create folder", e)
        print("expected argument example:")
        print("create_folder <bucket name>:<full pathname for the folder>")
        print("create_folder <full or relative pathname for the folder>")
        print()

        return 1

    return 0


def changeFolder(args, currPath, s3):
    try:
        pathArg = args[1].split(':')

        # check to see if its a full path: ch_folder <bucket name>:<full pathname of directory>
        if(len(pathArg) == 2 and len(pathArg[1]) > 0):
            if(bucketExist(s3, pathArg[0]) == False):
                raise Exception("Bucket does not exist")

            if(objectExist(s3, pathArg[0], pathArg[1]) == False):
                raise Exception("Directory/File doesn't exists")

            currPath = pathArg[0] + ':' + pathArg[1] + \
                ('/' if(pathArg[1][-1] != '/') else '')
            return currPath

        elif(len(pathArg) == 1):
            currBucketPath = currPath.split(':')

            if(pathArg[0] == '/'):
                currPath = ''
                return currPath
            elif(bucketExist(s3, pathArg[0]) == True and currPath == ''):
                # it a bucket
                currPath = pathArg[0] + ":"
                return currPath
            elif(len(currBucketPath[0]) > 0):

                newPath = getRelativePath(
                    currBucketPath[1].split('/'), pathArg[0].split('/'))

                if(len(newPath) == 0):
                    currPath = currBucketPath[0] + ':'
                    return currPath
                elif(objectExist(s3, currBucketPath[0], pathArg[0]) == True):
                    # its a full path
                    currPath = currBucketPath[0] + ':' + pathArg[0] + \
                        ('/' if(pathArg[0][-1] != '/') else '')
                    return currPath
                elif(objectExist(s3, currBucketPath[0], newPath) == True):
                    # elif(objectExist(s3_resource, currBucketPath[0], currBucketPath[1] + pathArg[0]) == True):
                    # its a relative path
                    currPath = currBucketPath[0] + ':' + newPath
                    return currPath
                else:
                    raise Exception
            else:
                raise Exception
        else:
            raise Exception

    except Exception:
        print("\nCannot change folder: ")
        print("expected argument example:")
        print("ch_folder <bucket name>    (only allowed from root of s3, to access to enter 'ch_folder /')")
        print("ch_folder <bucket name>:<full pathname of directory>")
        print("ch_folder <full or relative pathname of directory>")
        print()
        return 1


def clList(currPath, args, s3_resource, s3_client):

    bucketAndPath = currPath.split(':')
    try:
        longVersion = True if (len(args) >= 2 and args[1] == '-l') else False
        # list or -l
        if(len(args) == 1 or (len(args) == 2 and args[1] == '-l')):
            if(len(bucketAndPath) == 1 and len(bucketAndPath[0]) == 0):
                print('S3 Buckets:')
                for bucket in s3_resource.buckets.all():
                    if longVersion:
                        print(bucket.creation_date, '\t', bucket.name)
                    else:
                        print(bucket.name)
            elif(len(bucketAndPath) == 2):

                my_bucket = s3_resource.Bucket(bucketAndPath[0])
                for object_summary in my_bucket.objects.filter(Prefix=bucketAndPath[1]):
                    if longVersion:
                        if(len(object_summary.key[len(bucketAndPath[1]):]) > 0):
                            print(object_summary.bucket_name, object_summary.last_modified,
                                  object_summary.size, object_summary.key[len(bucketAndPath[1]):])
                    else:
                        if(len(object_summary.key[len(bucketAndPath[1]):]) > 0):
                            print(object_summary.key[len(bucketAndPath[1]):])
            else:
                raise Exception
        elif len(args) == 2 or (len(args) == 3 and args[1] == '-l'):

            pathIndex = 1 if longVersion == False else 2
            pathArg = args[pathIndex].split(':')

            # check to see if its a full path: ch_folder <bucket name>:<full pathname of directory>
            if(len(pathArg) == 2 and len(pathArg[1]) > 0):
                if(bucketExist(s3_resource, pathArg[0]) == False):
                    raise Exception("Bucket does not exist")

                if(objectExist(s3_resource, pathArg[0], pathArg[1]) == False):
                    raise Exception("Directory/File doesn't exists")

                currPath = pathArg[0] + ':' + pathArg[1] + \
                    ('/' if(pathArg[1][-1] != '/') else '')

                my_bucket = s3_resource.Bucket(pathArg[0])
                for object_summary in my_bucket.objects.filter(Prefix=pathArg[1]):

                    if longVersion:
                        if(len(object_summary.key[len(pathArg[1]):]) > 0):
                            print(object_summary.bucket_name, object_summary.last_modified,
                                  object_summary.size, object_summary.key[len(pathArg[1]):])
                    else:
                        if(len(object_summary.key[len(pathArg[1]):]) > 0):
                            print(object_summary.key[len(pathArg[1]):])

            elif(len(pathArg) == 1):
                #     currBucketPath = currPath.split(':') bucketAndPath

                if(pathArg[0] == '/'):
                    for bucket in s3_resource.buckets.all():
                        if longVersion:
                            print(bucket.creation_date, '\t', bucket.name)
                        else:
                            print(bucket.name)
                elif(bucketExist(s3_resource, pathArg[0]) == True):
                    # it a bucket
                    my_bucket = s3_resource.Bucket(pathArg[0])
                    for object_summary in my_bucket.objects.filter(Prefix=''):
                        if longVersion:
                            print(object_summary.bucket_name, object_summary.last_modified,
                                  object_summary.size, object_summary.key)
                        else:
                            print(object_summary.key)
                elif(len(bucketAndPath[0]) > 0):
                    newPath = getRelativePath(
                        bucketAndPath[1].split('/'), pathArg[0].split('/'))

                    if(objectExist(s3_resource, bucketAndPath[0], newPath) == False):
                        raise Exception("Directory/File doesn't exists")
                    my_bucket = s3_resource.Bucket(bucketAndPath[0])
                    for object_summary in my_bucket.objects.filter(Prefix=newPath):
                        if longVersion:
                            if(len(object_summary.key[len(newPath):]) > 0):
                                print(object_summary.bucket_name, object_summary.last_modified,
                                      object_summary.size, object_summary.key[len(newPath):])
                        else:
                            if(len(object_summary.key[len(newPath):]) > 0):
                                print(object_summary.key[len(newPath):])
                else:
                    raise Exception
            else:
                raise Exception

        else:
            raise Exception
    except Exception:
        print("Cannot list contents of the S3 location")
        print("expected argument example:")
        print("list")
        print("list <bucket name>")
        print("list <bucket name>:<full pathname for the directory or file>")
        return 1

    return 0


def cCopy(currPath, args, s3):

    try:
        bucketAndPath = currPath.split(':')
        fromLocation = args[1].split(":")
        toLocation = args[2].split(":")
        if(len(fromLocation) == 2):
            copy_source = {
                'Bucket': fromLocation[0],
                'Key': fromLocation[1]
            }
        elif(len(fromLocation) == 1):
            newPath = getRelativePath(
                bucketAndPath[1].split('/'), fromLocation[0].split('/'))

            if(len(newPath) > 0):
                newPath = newPath[:-1]

            copy_source = {
                'Bucket': bucketAndPath[0],
                'Key': newPath
            }
        else:
            raise Exception

        if(len(toLocation) == 2):
            bucket = s3.Bucket(toLocation[0])
            bucket.copy(copy_source, toLocation[1])
        elif(len(toLocation) == 1):
            newPath = getRelativePath(
                bucketAndPath[1].split('/'), toLocation[0].split('/'))

            if(len(newPath) > 0):
                newPath = newPath[:-1]

            bucket = s3.Bucket(bucketAndPath[0])
            bucket.copy(copy_source, newPath)
        else:
            raise Exception
    except:
        print("Cannot perform copy")
        print("expected argument example:")
        print("ccopy <from S3 location of object> <to S3 location>")
        return 1
    return 0


def cDelete(currPath, args, s3):
    try:
        bucketAndPath = currPath.split(':')
        deleteLocation = args[1].split(":")
        if(len(deleteLocation) == 2):
            res = deleteIfObjectIsEmpty(
                s3, deleteLocation, False, bucketAndPath)
            if res == False:
                raise Exception

        elif(len(deleteLocation) == 1):
            newPath = getRelativePath(
                bucketAndPath[1].split('/'), deleteLocation[0].split('/'))
            res = deleteIfObjectIsEmpty(s3, newPath, True, bucketAndPath)
            if res == False:
                raise Exception

        else:
            raise Exception

    except Exception:
        print("Cannot perform delete")
        print("expected argument example:")
        print("cdelete <full or indirect pathname of object>")
        return 1

    return 0


def deleteBucket(currPath, args, s3):
    try:
        bucketAndPath = currPath.split(':')
        if(bucketExist(s3, args[1]) != True):
            raise Exception

        if(bucketAndPath[0] == args[1]):
            raise Exception

        bucket = s3.Bucket(args[1])
        bucket.delete()
        return 0

    except Exception:
        print("Cannot delete bucket")
        print("expected argument example:")
        print("delete_bucket <bucket name>")
        return 1

    return 0
