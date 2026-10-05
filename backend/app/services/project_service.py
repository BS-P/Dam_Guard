import uuid
import json
import os

class Project:
    def __init__(self, id: str, name: str, description: str, aoi_geojson: str):
        self.id = id
        self.name = name
        self.description = description
        self.aoi_geojson = aoi_geojson

_projects = {}

def create_project(name: str, description: str, aoi_geojson: str) -> Project:
    """Creates a new project."""
    project_id = str(uuid.uuid4())
    proj = Project(project_id, name, description, aoi_geojson)
    _projects[project_id] = proj
    return proj

def load_project(project_id: str) -> dict:
    """Loads full project state."""
    proj = _projects.get(project_id)
    if not proj:
        raise ValueError("Project not found.")
    return {
        "id": proj.id,
        "name": proj.name,
        "description": proj.description,
        "aoi": proj.aoi_geojson
    }

def save_project_state(project_id: str) -> None:
    """Saves project state (mock implementation)."""
    if project_id not in _projects:
        raise ValueError("Project not found.")
    # Here we would persist to DB or file
    pass
