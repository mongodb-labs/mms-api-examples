# Automation API Endpoints

## Automation Config

## Critical Concept: Versioning

The Automation Config for a Group is internally versioned. Each time a new Automation Config is submitted,
the version is incremented. The current version can be seen in the `version` field.

There is *no protection* in the Automation API to prevent concurrent modifications. Each time a new configuration
is submitted via the API, the current state of the system is adjusted to match the config. If two administrators of
the system both start with a configuration based on version 9, make their own modifications, and then submit their
modifications, the later modification will win.

The Automation API is very powerful, and should be used with great caution.

### Operations

* GET /api/public/v1.0/groups/GROUP-ID/automationConfig - Get the Automation configuration for a Group
* PUT /api/public/v1.0/groups/GROUP-ID/automationConfig - Put the Automation configuration for a Group

### GETting the Automation Config

The document return follows the format of the [Cluster Configuration](https://docs.mms.mongodb.com/reference/cluster-configuration/)

### PUTting the Automation Config

#### Example Usage

    curl -u "MMS_USER_NAME:MMS_API_KEY" -H "Content-Type: application/json" "https://mms.mongod.com/api/public/v1.0/groups/GROUP_ID/automationConfig"  --digest -X PUT -d @/PATH/TO/CONFIG/config.json -i

The document accepted by the PUT requires a subset of the fields return by the GET and explained in the
[Cluster Configuration](https://docs.mms.mongodb.com/reference/cluster-configuration/).  The details of 
some areas of the configuration is managed internally by MMS, and therefore less detail is required in the PUT
than is returned in the GET.

This is best explained by example - building up an Automation Config step by step.

#### Setting the Download Base

The central job of MMS Automation is to install, upgrade and maintain MongoDB processes.  In order to do so, it will
download specified MongoDB binaries and save these to the local disk.  The `options.downloadBase` property defines
the location on disk where the Automation Agent will store these MongoDB binaries.

Please note that this location must pre-exist on *every* server, and must be writeable by the Automation Agent system
user. If you installed the Automation Agents using our `RPM` or `DEB` packages, the directory `/var/lib/mongodb-mms-automation`
will have been pre-prepared for this purpose.

An Automation Config with only the download base specified looks like this:

    {
        "options": {
            "downloadBase": "/var/lib/mongodb-mms-automation"
        },
        "mongoDbVersions": [],
        "monitoringVersions": [],
        "backupVersions": [],
        "processes": [],
        "replicaSets": [],
        "sharding": []
    }

This example can also be viewed [here](https://github.com/10gen-labs/mms-api-examples/blob/master/automation/api_usage_example/configs/api_0_clean.json)

#### Defining MongoDB Versions

Next, specify the MongoDB versions that you wish to use in your deployment.  A simple example specifying the use of
MongoDB versions 3.0.1 and 3.0.2 looks like this:

    {
        "options": {
            "downloadBase": "/var/lib/mongodb-mms-automation"
        },
        "mongoDbVersions": [
            {"name": "3.0.1"},
            {"name": "3.0.2"}
        ],
        "monitoringVersions": [],
        "backupVersions": [],
        "processes": [],
        "replicaSets": [],
        "sharding": []
    }
    
With this configuration, the Automation Agent will download these MongoDB binaries from http://mongodb.org/downloads.
This example can also be viewed [here](https://github.com/10gen-labs/mms-api-examples/blob/master/automation/api_usage_example/configs/api_1_define_versions.json)

If you have a license for the Enterprise versions of MongoDB, these may be specified as:

    {
        "options": {
            "downloadBase": "/var/lib/mongodb-mms-automation"
        },
        "mongoDbVersions": [
            {"name": "3.0.1-ent"},
            {"name": "3.0.2-ent"}
        ],
        "monitoringVersions": [],
        "backupVersions": [],
        "processes": [],
        "replicaSets": [],
        "sharding": []
    }

If you wish to define a custom download location, or use custom versions, please see our Appendix.

#### (Optional) Installing Monitoring and Backup Agents

In order to have a fully functional MMS Group, you must also have one Monitoring Agent.  If you are using MMS Backup
you also need a Backup Agent. You may optionally configure your Automation Agents to manage your Monitoring and
Backup Agents.  

Suppose we are configuring a single-server MongoDB deployment, on which we want to run a MongoDB replica set, a
Monitoring Agent and Backup Agent.  Adding the Monitoring and Backup Agents to our configuration looks like this:

    {
        "options": {
            "downloadBase": "/var/lib/mongodb-mms-automation"
        },
        "mongoDbVersions": [
            {"name": "3.0.1"},
            {"name": "3.0.2"}
        ],
        "monitoringVersions": [
            {
                "hostname": "AGENT_HOSTNAME",
                "logPath": "/var/log/mongodb-mms-automation/monitoring-agent.log",
                "logRotate": {
                    "sizeThresholdMB": 1000,
                    "timeThresholdHrs": 24
                }
            }
        ],
        "backupVersions": [
            {
                "hostname": "AGENT_HOSTNAME",
                "logPath": "/var/log/mongodb-mms-automation/backup-agent.log",
                "logRotate": {
                    "sizeThresholdMB": 1000,
                    "timeThresholdHrs": 24
                }
            }
        ],
        "processes": [],
        "replicaSets": [],
        "sharding": []
    }


where `AGENT_HOSTNAME` is the full-qualified domain name (FQDN) of the server. This can be determined by running
`hostname -f` on the server.  It is essential that you specify the FQDN (`hostname -f`) and not the unqualified
hostname (`hostname`).

#### Building A MongoDB Deployment

Now that we've set up our environment, we're ready to specify our MongoDB deployment.  To create a 3-member replica 
set with two data nodes, and one arbiter we start filling in the [processes](https://docs.mms.mongodb.com/reference/cluster-configuration/#processes)
and [replicaSets](https://docs.mms.mongodb.com/reference/cluster-configuration/#replicasets) fields.

On our simple single-server deployment, these fields might look like:

    "processes": [
        {
            "args2_6": {
                "net": {
                    "port": 28000
                },
                "replication": {
                    "replSetName": "blue"
                },
                "storage": {
                    "dbPath": "/data/blue_0"
                },
                "systemLog": {
                    "destination": "file",
                    "path": "/data/blue_0/mongodb.log"
                }
            },
            "hostname": "AGENT_HOSTNAME",
            "logRotate": {
                "sizeThresholdMB": 1000,
                "timeThresholdHrs": 24
            },
            "name": "blue_0",
            "processType": "mongod",
            "version": "3.0.1",
            "authSchemaVersion": 3
        },
        {
            "args2_6": {
                "net": {
                    "port": 28001
                },
                "replication": {
                    "replSetName": "blue"
                },
                "storage": {
                    "dbPath": "/data/blue_1"
                },
                "systemLog": {
                    "destination": "file",
                    "path": "/data/blue_1/mongodb.log"
                }
            },
            "hostname": "AGENT_HOSTNAME",
            "logRotate": {
                "sizeThresholdMB": 1000,
                "timeThresholdHrs": 24
            },
            "name": "blue_1",
            "processType": "mongod",
            "version": "3.0.1",
            "authSchemaVersion": 3
        },
        {
            "args2_6": {
                "net": {
                    "port": 28002
                },
                "replication": {
                    "replSetName": "blue"
                },
                "storage": {
                    "dbPath": "/data/blue_2"
                },
                "systemLog": {
                    "destination": "file",
                    "path": "/data/blue_2/mongodb.log"
                }
            },
            "hostname": "AGENT_HOSTNAME",
            "logRotate": {
                "sizeThresholdMB": 1000,
                "timeThresholdHrs": 24
            },
            "name": "blue_2",
            "processType": "mongod",
            "version": "3.0.1",
            "authSchemaVersion": 3
        }
    ],
    "replicaSets": [
        {
            "_id": "blue",
            "members": [
                {
                    "_id": 0,
                    "host": "blue_0"
                },
                {
                    "_id": 1,
                    "host": "blue_1"
                },
                {
                    "_id": 2,
                    "arbiterOnly": true,
                    "host": "blue_2",
                    "priority": 0
                }
            ]
        }
    ],

Note that every processes must have a unique (but arbitrary `name`) and that the `replicaSets` configuration contains
references to the process `name`s. A full configuration example can be found
[here](https://github.com/10gen-labs/mms-api-examples/blob/master/automation/api_usage_example/configs/api_3_create_replica_set.json).

#### Removing ("Unmanaging") A Process or Processes from the Automation Configuration

If a process (or multiple processes) are moved from the Automation Configuration, the Automation Agents will no
longer manage these processes.  This means that the Automation Agents will simply ignore the existence of these
processes.  Removing a process from the Automation Configuration does *not* shut down the process or delete
its data or log directories.

It is critical to keep this in mind if you are going to deploy new processes on the same server.  If you remove
a process on port 27018 from your Automation Configuration and then add a new process, also on port 27018, the new
process will fail to reach goal state because the port will already be in use by the previously unmanaged process.

#### Configuring MONGODB-CR Authentication

##### Critical Concepts

1. All MongoDB processes belonging to a single Automation Config (and therefore a single MMS Group) share a *single*
auth configuration.  This means that there is a single, shared keyFile, and a single set of users and roles.
2. Configuring a username and password for the Automation Agent itself is required.
3. It is also required that an appropriate user be defined for both the Monitoring and Backup Agents - even if the
Monitoring and Backup Agents themselves are not managed by Automation.  The username for the Monitoring Agent must
be `mms-monitoring-agent` and the username for the Backup Agent must be `mms-backup-agent`.
4. In oder to enable authentication, the `auth.disabled` parameter must be set to `false.
5. Additional users may be defined manually. MMS Automation will ignore additional users, unless they are included
in the `auth.usersDeleted` field, in which case it will remove them.

##### Example and Details

An example [auth](https://docs.mms.mongodb.com/reference/cluster-configuration/#auth) configuration
might look like this:

    "auth": {
        "disabled": false,
        "autoPwd": "Sy4oBX9ei0amvupBAN8lVQhj",
        "autoUser": "mms-automation",
        "key": "GrSLAAsHGXmJOrvElJ2AHTGauvH4O0EFT1r8byvb0G9sTU0viVX21PwUMqBjyXB9WrZP9QvEmCQIF1wOqJofyWmx7wWZqpO69dnc9GUWcpGQLr7eVyKTs99WAPXR3kXpF4MVrHdBMEDfRfhytgomgAso96urN6eC8RaUpjX4Bf9HcAEJwfddZshin97XKJDmqCaqAfORNnf1e8hkfTIwYg1tvIpwemmEF4TkmOgK09N5dINyejyWMU8iWG8FqW5MfQ8A2DrtIdyGSKLH05s7H1dXyADjDECaC77QqLXTx7gWyHca3I0K92PuVFoOs5385vzqTYN3kVgFotSdXgoM8Zt5QIoj2lX4PYqm2TWsVp0s15JELikH8bNVIIMGiSSWJEWGU1PVEXD7V7cYepDb88korMjr3wbh6kZ76Q7F2RtfJqkd4hKw7B5OCX04b5eppkjL598iCpSUUx3X9C6fFavWj2DrHsv9DY86iCWBlcG08DRPKs9EPizCW4jNZtJcm3T7WlcI0MZMKOtsKOCWBZA0C9YnttNrp4eTsQ1U43StiIRPqp2K8rrQAu6etURH0RHedazHeeukTWI7iTG1dZpYk9EyittZ72qKXLNLhi5vJ9TlYw8O91vihB1nJwwA3B1WbiYhkqqRzoL0cQpXJMUsUlsoSP6Q70IMU92vEHbUmna5krESPLeJfQBKGQPNVVE63XYBh2TnvFTdi6koitu209wMFUnHZrzWj3UWGqsyTqqHbPl4RhRLFe24seRwV2SbUuLygBIdptKHnA3kutAbHzsWTT8UxOaiQzFV4auxounrgXj7MoMWEVKKS8AHkELPILGqFVFC8BZsfPC0WacSN5Rg5SaCvfs74hcsCQ3ghq9PyxEb2fbHUiaCjnsBcXqzQw9AjZJG4yX0ubEwicP0bKB6y3w4PUQqdouxH5y16OgkUjrZgodJfRLgP9vqGbHNDpj4yBuswluvCFBh38gBoSIQu11qtQmk43n4G8Dskn0DrJ32l2Gz35q5LaKT",
        "keyfile": "/var/lib/mongodb-mms-automation/keyfile",
        "usersWanted": [
            {
                "db": "fruit",
                "user": "fruitReadOnly",
                "initPwd": "6782fa9dfefc4da96ddc2e6099f79bbf",
                "roles": [
                    {
                        "db": "fruit",
                        "role": "read"
                    }
                ]
            },
            {
                "db": "admin",
                "initPwd": "6782fa9dfefc4da96ddc2e6099f79bbf",
                "roles": [
                    {
                        "db": "admin",
                        "role": "clusterMonitor"
                    }
                ],
                "user": "mms-monitoring-agent"
            },
            {
                "db": "admin",
                "initPwd": "d378693eb4888a79d1864f4affb0a739",
                "roles": [
                    {
                        "db": "admin",
                        "role": "clusterAdmin"
                    },
                    {
                        "db": "admin",
                        "role": "readAnyDatabase"
                    },
                    {
                        "db": "admin",
                        "role": "userAdminAnyDatabase"
                    },
                    {
                        "db": "local",
                        "role": "readWrite"
                    },
                    {
                        "db": "admin",
                        "role": "readWrite"
                    }
                ],
                "user": "mms-backup-agent"
            }
        ],
        "usersDeleted": []

Note that the `initPwd` is the clear-text (unhashed) password for the specified user.

#### Roles

MongoDB custom [roles](https://docs.mms.mongodb.com/reference/cluster-configuration/#roles) may also be defined.

    "roles": [
        {
            "db": "fruit",
            "role": "fruitInsertOnly",
            "privileges": [
                {
                    "resource": {
                        "db": "fruit",
                        "collection": "",
                        "cluster": null
                    },
                    "actions": [
                        "insert"
                    ]
                }
            ],
            "roles": null
        }
    ],

A full configuration with authentication is shown [here](https://github.com/10gen-labs/mms-api-examples/blob/master/automation/api_usage_example/configs/api_6_enable_auth.json)

## Automation Status

### Operations

* GET /api/public/v1.0/groups/GROUP-ID/automationStatus - Get the Automation status for a Group

#### GETting the Automation Status

This endpoint returns the status of every MongoDB process in the deployment, as viewed by the Automation Agent. 

    "goalVersion": 29,
    "processes": [
        {
            "hostname": "AGENT_HOSTNAME",
            "name": "blue_0",
            "lastGoalAchieved": 28,
            "plan": ["Download", "Start", "WaitRsInit"]
        },
        {
            "hostname": "AGENT_HOSTNAME",
            "name": "blue_1",
            "lastGoalAchieved": 29,
            "plan": []
        }
    ]

The `goalVersion` field corresponds to the `version` of the most recently submitted Automation Config.

For each process, the `hostname` indicates the full-qualified hostname (`hostname -f`) of the server on
which the Automation Agent and process are hosted.  The `name` maps to the process `name` as specified in the
Automation Config. `lastGoalAchieved` indicates the last version of the Automation Config with which this process
was fully in spec. If `lastGoalAchieved` is not equal to `goalVersion` than there will also be a `plan` on how this
process will move from its current state to the new goal state.

## Example Code

A full Python example can be found [here](https://github.com/10gen-labs/mms-api-examples/blob/master/automation/api_usage_example/test_automation_api.py).
This example gradually builds up a MongoDB deployment, going through the following phases:

1. Setting up the download base.
2. Defining MongoDB versions.
3. Defining a configuration for a Monitoring and Backup Agent.
4. Deploying a 3-member replica set on MongoDB 3.0.1.
5. Upgrading this replica set to MongoDB 3.0.2.
6. Converting this replica set to a single shard cluster.
7. Enabling authentication

The series of Automation Configs that are deployed can be found [here](https://github.com/10gen-labs/mms-api-examples/tree/master/automation/api_usage_example/configs).

This example requires installing the [requests](http://www.python-requests.org/) module.

To run the code:

    python test_automation_api.py MMS_BASE_URL AGENT_HOSTNAME GROUP_ID MMS_USER_ID MMS_USER_API_KEY
    
* MMS_BASE_URL is the base URL for your MMS deployment. For example, for MMS Cloud this would be https://mms.mongodb.com
* AGENT_HOSTNAME is the fully-qualified domain name (`hostname -f`) for the server on which you have installed an Automation Agent.
* GROUP_ID is the MMS Group ID
* MMS_USER_ID and MMS_USER_API_KEY are the credentials for the MMS API.  See [here](https://docs.mms.mongodb.com/tutorial/use-mms-public-api/) for how to set these up.

For example:

    python test_automation_api.py https://mms.mongodb.com mongo-1.example.com 54b5e4df9436322466a89a3e fred@example.com 063fc60e-c5eb-4426-85c1-1e650d6228c6
    
