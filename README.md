This was part of a programming challenge I carried out as part of a job interview.
It is a python implementation of a port inclusion/exclusion rule.

The input is two lists, where the ports to include and exclude are in two-item
lists of their own, and the first member is always the low port and the second
is always the high. The output is also a list-of-lists, representing the minimized
result of implementing the include/exclude rules.

Example:
#input:
    #include_ports: [[80, 80], [22, 23], [8000, 9000]]
    #exclude_ports: [[1024, 1024], [8080, 8080]]
#output:
    #[[22, 23], [80, 80], [8000, 8079], [8081, 9000]]   

To accomplish this, I implemented a basic Binary Interval Search Tree in python,
along with some helper methods that are more specific to this task.

Note: This was developed in Python v. 3.6.0
