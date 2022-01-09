Umer Ahmed

Description: A python shell that lets users interact with their AWS S3 buckets and object through their local terminal.

Run shell with 'python shell.py'

To authenticate into AWS account enter your AWS credentials into a file called 'S5-S3conf' in the same dir as shell.py with the following format:
[umer]
aws_access_key_id = [AWS_ACCESS_KEY_ID]
aws_secret_access_key = [AWS_SECRET_ACCESS_KEY]

general guidelines: 
- if you are are entering a folder/file name with a space, it needs to be in quotes ex. 'folder name'/'file name'.jpg
- use forward slashes for you cloud object path ex. folder1/folder2/file.txt
- file names must include extentions ex. file.txt
- local full path should begin from you C drive ex. C:/Users/user/Desktop/Folder/'File.txt'

Below are descriptions of the S5 shell commands and fornating rules to follow:

1. lc_copy: 
- description:  
    copies a local file to a Cloud (S3) location
- argument expectations:    
    "lc_copy <full or relative pathname of local file> <bucket name>:<full pathname of S3 object>"

2. cl_copy:   
- description:  
    copies a Cloud object to a local file system location
- argument expectations:    
    cl_copy <bucket name>:<full pathname of S3 file> <full or relative pathname of the local file>
    cl_copy <full or relative pathname of S3 file> <full or relative pathname of the local file>

3. create_bucket:
- description:  
    creates a bucket in the user's S3 space following naming conventions for S3 buckets
- argument expectations:    
    create_bucket <bucket name>

4) create_folder:
- description:  
    creates a directory or folder in an existing S3 bucket
- argument expectations:    
    create_folder <bucket name>:<full pathname for the folder>
    create_folder <full or relative pathname for the folder>

5) ch_folder:
- description:  
     changes the current working folder/directory in your S3 space
- argument expectations:    
    ch_folder / (to change to the root of s3 console where you can access you buckets)
    ch_folder .. (to go back a folder in a bucket )
    ch_folder <bucket name> (only accessable by going to the root first "ch_folder /")
    ch_folder <bucket name>:<full pathname of directory>
    ch_folder <full or relative pathname of directory>


6) cwf:
- description:  
    displays the current working folder/directory, i.e. your location in S3 space. If you are 
    not yet located in a bucket, then the response will be "/". This would be the response 
    if you execute this command after starting the shell

- argument expectations: 
    cwf

7) list:
- description:  
    Displays either a short or long form of the contents of your 
    current working directory or a specified S3 location (including "/"). The argument 
    to get the long version is "-l" - same as the Unix ls command
- argument expectations:    
    list -l(optional)
    list -l(optional) <bucket name>
    list -l(optional) <bucket name>:<full pathname for directory or file> 

8) ccopy:
- description:  
    copy an object from one S3 location to another
- argument expectations:    
    ccopy <from S3 location of object> <to S3 location>

9) cdelete:
- description:  
    delete an object (folders included but only if they are empty). This command will not 
    delete buckets.
    you can only delete objects if they in a lower folder level than the cwf
- argument expectations:    
    cdelete <full or indirect pathname of object>

10) delete_bucket:
- description:  
    delete a bucket if it is empty. You cannot delete the bucket that you are currently in.
- argument expectations:
    delete_bucket <bucket name>    


