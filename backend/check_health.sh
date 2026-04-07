#!/bin/bash

# Quick health check
sleep 3
curl -s http://localhost:8000/health | python3 -m json.tool
