#!/usr/bin/env python

import watchgod
import fire
import requests
from os import path
import json
import pygments
from pygments import highlight, lexers, formatters
from datetime import datetime

def ppJson(data):
    return highlight(json.dumps(data, indent = 4),
        lexers.JsonLexer(),
        formatters.TerminalFormatter())

class timeContext:
    def __init__(self,contextName):
        self.contextName = contextName
    def __enter__(self,*args,**kwargs):
        self.t1 = datetime.now()
        print(f"Doing {self.contextName}...")
    def __exit__(self,*args,**kwargs):
        duration = datetime.now() - self.t1
        print(f"{self.contextName}: {duration.total_seconds()} seconds elapsed")

def handleQuery(change,url):
    print("\n"+("#" * 32))
    changetype, filepath = change.pop()
    print(f"Doing query {filepath}")
    with open(filepath) as f:
        query = f.read()
        payload = {
            "query": query
        }

        with timeContext("request"):
            r = requests.post(url, data = payload)
        if r.status_code == 200:
            dat = json.loads(r.content.decode())
            if "errors" in dat.keys():
                print("Errors!!")
                print(ppJson(dat))
            else: 
                with timeContext("parsing"):
                    jsonstring = ppJson(dat) 
                    jsonlines = jsonstring.split("\n")

                print(f"There were {len(jsonlines)} lines")
                print("\n".join(jsonlines[:25]))
                print("...")

        else:
            print(f"Request returned {r.status_code}")
            print(r.content.decode())

def watchQueries(folder = "queries", url = "http://0.0.0.0:8000"):
    print(f"Watching {path.abspath(folder)}")
    print(f"Dispatching to {url}")
    for c in watchgod.watch(folder):
        handleQuery(c,url)

if __name__ == "__main__":
    fire.Fire(watchQueries)
