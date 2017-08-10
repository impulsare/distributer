impulsare/distributer
===============================

Overview
--------------------------
A queue manager based on ``rq`` and made for **impulsare**. It helps to :
- add items to a queue
- listen for a queue via a cli listener

See `tests/static/` for examples of configuration.



Installation / Usage
--------------------------
To install use pip:
```bash
$ pip install --upgrade impulsare-distributer
```


Configuration
--------------------------
You need to create/add to your configuration file:
```yaml
distributer:
    # Required, redis address
    host: 192.168.108.3

    # Optional
    port: 6379

# If a component needs to send data to a queue,
# define here where what is the queue's name (next one)
# used by impulsare-ruler to send to writer for example (ruler: {queue: writer})
testqueue:
    queue: my_test_queue

```


Listener
--------------------------
This is a simple implementation of ``rq's`` worker. If you need to listen for a queue,
no need to have a config file, run in cli:
```bash
$ queue-listener --host redis --queue my_test_queue
```

To be able to see the next example working, keep that opened in a separate window.


Queue Usage
-----------------------------
To use the queue manager, and send jobs to be processed:
```python
from impulsare_distributer import QueueManager
from mymodule import my_method


queue = QueueManager(config_file='tests/static/config_valid.yml', listener='testqueue')
queue.add(method=my_method, item='Hello World', job='test')
```


Development & Tests
--------------------------------
```bash
$ pip install -r requirements.txt
$ pip install -r requirements-dev.txt
$ py.test --cov-report html --cov=impulsare_distributer tests/
```
