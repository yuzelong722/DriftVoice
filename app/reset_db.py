#!/usr/bin/env python3
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from app import app, db
with app.app_context():
    db.drop_all()
    db.create_all()
    print("DB reset done")
