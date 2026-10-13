
"""
Utility functions for the UFC stats project, including URL building and data cleaning functions.

"""


# source: the list of objects to build urls for (e.g. fighters, events, etc.)
# url_skeleton: the base url with a placeholder for each object in source

def url_builder(source, url_skeleton):
    return [url_skeleton + str(item) for item in source]

