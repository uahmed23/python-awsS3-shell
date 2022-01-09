import boto3
from botocore.exceptions import ClientError
import logging
import os
import shlex

from s3functions import authenticate, authenticateClient, authenticateResource, bucketExist, objectExist, getRelativePath, \
    lcCopy, clCopy, createBucket, createFolder, changeFolder, clList, cCopy, cDelete, deleteBucket


def main():

    cloud_dir = ''
    # local_dir = os.getcwd()

    credentials = authenticate()

    s3_client = authenticateClient(credentials)
    # AWS authentication failed
    if s3_client == 1:
        return 1

    s3_resource = authenticateResource(credentials)
    if s3_resource == 1:
        return 1

    print('You are now connected to your S3 storage\n')

    # os.system("echo Hello from hackanons")
    # home_dir = os.system("cd ~")

    while True:
        try:
            inputString = input('S5> ')
            inputString = inputString.replace('\\', '\\\\')
            splitInput = shlex.split(inputString)
        except Exception as e:
            print(
                'Invalid input make sure to in-close folder/file names with spaces in quotes ex. \'folder name\'/\'file name\'.jpg', e)
            continue

        if inputString.lower() == 'exit' or inputString == 'quit':
            break
        elif len(splitInput) == 0:
            returnCode = 0
        elif splitInput[0].lower() == 'lc_copy':
            # example: S5> lc_copy catpictures/mycat01.jpg umerBucket:images/cats/mycat.jpg
            returnCode = lcCopy(splitInput, s3_client, cloud_dir)

        elif splitInput[0].lower() == 'cl_copy':
            # example: S5> cl_copy umerBucket:images/cats/mycat.jpg catpic001.jpg
            # example: S5> cl_copy mycat.jpg catpic001.jpg
            returnCode = clCopy(splitInput, s3_client, cloud_dir, s3_resource)

        elif splitInput[0].lower() == 'create_bucket':
            # example: S5> create_bucket umerBucket
            returnCode = createBucket(splitInput, s3_client)

        elif splitInput[0].lower() == 'create_folder':
            # example
            # S5> create_folder umerBucket:images
            # S5> create_folder umerBucket:images/cats
            # S5> ch_folder umerBucket
            # S5> create_folder images
            # S5> ch_folder images
            # S5> create_folder cats
            returnCode = createFolder(splitInput, cloud_dir, s3_client)

        elif splitInput[0].lower() == 'ch_folder':
            # example
            # ch_folder <bucket name>
            # ch_folder <bucket name>:<full pathname of directory>
            # ch_folder <full or relative pathname of directory>
            returnCode = changeFolder(splitInput, cloud_dir, s3_resource)
            if returnCode != 1:
                cloud_dir = returnCode

        elif splitInput[0].lower() == 'cwf':
            if len(cloud_dir) == 0:
                print('/')
            else:
                print(cloud_dir)

        elif splitInput[0].lower() == 'list':
            # example
            # S5> list umerBucket
            # S5> list -l umerBucket:images/cats
            # S5> list /
            # S5> ch_folder umerBucket
            # S5> list -l
            returnVal = clList(cloud_dir, splitInput, s3_resource, s3_client)

        elif splitInput[0].lower() == 'ccopy':
            returnVal = cCopy(cloud_dir, splitInput, s3_resource)
        elif splitInput[0].lower() == 'cdelete':
            returnVal = cDelete(cloud_dir, splitInput, s3_resource)
        elif splitInput[0].lower() == 'delete_bucket':
            returnVal = deleteBucket(cloud_dir, splitInput, s3_resource)
        elif(splitInput[0].lower() == 'cd'):
            try:
                os.chdir(splitInput[1] if len(splitInput) > 1 else './')
            except Exception as e:
                print('could not change folders', e)
        else:
            systemReturn = os.system(inputString)
            if systemReturn == 1:
                print(' "{}" command was not recognize, please try again'.format(
                    inputString))
            else:
                print("cd ~ ran with exit code %d" % systemReturn)


if __name__ == "__main__":
    main()
