# mattermost-delete-channel-posts

## Dependencies
### CentOS 7
```
sudo yum install python3-pip
pip3 install --user -r requirements.txt  # (e.g. inside the **mattermost** user)
```

or to install the needed module system wide

```
sudo pip3 install -r requirements.txt
```

## Usage
This reposity needs to be cloned or downloaded as archive. Next after cloning or extracting `cd` into
*mattermost-delete-channel-posts*. Afterwards one could use `chmod +x delete-channel-posts.py` and
```
./delete-channel-posts.py -n 100 -s 'http://localhost:8065' -c 44uabjn3y7yidkmnobed3whmyh -w 10 -u mmuser -p mmuser_password -D mattermost -H localhost --api-user test@test.com --api-pass 'test!'
```

### Options
```
-n or --n-posts       Number of oldest posts to delete
-s or --siteurl       Mattermost siteurl (e.g. http://localhost:8065 or https://mm.example.com)
-c or --channel-id    Id of channel
-w or --worker        Number of workers used for calling API
-u or --db-user       Username for database
-p or --db-password   Password for database
-D or --database      Database name
-H or --host          Database host (e.g. localhost, 127.0.0.1)
--api-user            Username for authenticating against API
--api-password        Password for API user
```

API Documentation for the used call can be found [here](https://api.mattermost.com/#operation/DeletePost).
