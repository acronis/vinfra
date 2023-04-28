## Vinfra

`vinfra` - A command line tool used to manage Acronis Cyber Infrastructure (ACI) or Virtuozzo Hybrid Infrastructure (VHI).


> NOTE: Makefile uses python2 by default. If you want to use python3, run:
> make complete PYTHON=python3 > /etc/bash_completion.d/vinfra

*Install from the current sources*:

### Install from git:
```bash
cd local_git_clone_directory
pip install .
# Enable bash (if you use it) auto completion:
make complete > /etc/bash_completion.d/vinfra
chmod +x /etc/bash_completion.d/vinfra
source /etc/bash_completion.d/vinfra
```

#### Install from the yum repository:

```bash
# On HCI nodes, it is installed automatically with the vstorage-ui-client package.
# yum install vstorage-ui-client
```

### Usage:

*\*The client supports python2, as well as python3.*

*You can set up environment variables to make commands shorter:*

```bash
export VINFRA_PORTAL=portal
export VINFRA_USERNAME=username
export VINFRA_PASSWORD=password
```

*Examples:*

```bash
# vinfra node list
+--------------------------------------+---------------------------+------------+-----------+-------------+
| id                                   | host                      | is_primary | is_online | is_assigned |
+--------------------------------------+---------------------------+------------+-----------+-------------+
| b15f334a-c970-4eb8-9f66-84bb75bf3893 | hci1.vstoragedomain       | True       | True      | True        |
| 3cc0515c-fde3-4e49-b655-43849c17da6b | hci2.vstoragedomain       | False      | True      | True        |
+--------------------------------------+---------------------------+------------+-----------+-------------+
# vinfra node show 3cc0515c-fde3-4e49-b655-43849c17da6b
<cut>
# vinfra node add 3cc0515c-fde3-4e49-b655-43849c17da6b --wait --timeout 200

# vinfra node release 3cc0515c-fde3-4e49-b655-43849c17da6b
+---------+--------------------------------------+
| Field   | Value                                |
+---------+--------------------------------------+
| task_id | 20dd827c-a817-446b-9466-4bf95328574b |
+---------+--------------------------------------+
# vinfra task wait 20dd827c-a817-446b-9466-4bf95328574b
+---------+----------------------------------------+
| Field   | Value                                  |
+---------+----------------------------------------+
| state   | success                                |
| args    | - 3cc0515c-fde3-4e49-b655-43849c17da6b |
|         | - false                                |
| name    | backend.tasks.node.ReleaseNodeTask     |
| task_id | 20dd827c-a817-446b-9466-4bf95328574b   |
| kwargs  |                                        |
+---------+----------------------------------------+
#
```
