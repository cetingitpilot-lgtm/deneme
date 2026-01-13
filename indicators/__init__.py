import os
current_dir = os.path.dirname(__file__)
indicator_list = [
    f[:-3] for f in os.listdir(current_dir) 
    if f.endswith('.py') and f != '__init__.py'
]
