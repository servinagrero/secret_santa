# Secret Santa

Python script to organize a Secret Santa.

# Usage

First edit the `config_template.toml` to create a `config.toml` with the sender information and the participants.

To perform a healthest on the connection:

```
$ python3 main.py -c config.toml -t  
```

To send the mails to all participants:

```
$ python3 main.py -c config.toml -s
```
