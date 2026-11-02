#!/usr/bin/env python

import os
import sys

input1 = sys.argv[1] # Main settings file
input2 = sys.argv[2] # User's settings file
output = '/tmp/new_settings.py'

new = open(output, 'wb')

# First save the header, imports, etc
i = open(input1).read()
i2 = i[i.find("#!"):i.find("START CUSTOMIZE")-3]
new.write(i2 + '\n')

# First save the customize section to the new settings file
i = open(input2).read()
i2 = i[i.find("START CUSTOMIZE")-2:i.find("END CUSTOMIZE")+13]
new.write(i2 + '\n')

# Now fetch the new static section from me
i = open(input1).read()
i2 = i[i.find("# START STATIC"):i.find("END STATIC")+10]
new.write(i2 + '\n')

new.close()
