# GitHub Copilot Instructions for Mergington High School Activities

## Project Overview

This is a simple full-stack web application for managing high school extracurricular activities. It combines a FastAPI backend with a vanilla JavaScript frontend, demonstrating a basic REST API pattern with an in-memory database.

## Architecture

**Frontend** (`src/static/`)
- `index.html`: Contains form for activity signup and container for activities list
- `app.js`: Fetches activities from `/activities` endpoint and handles signup form submission to POST `/activities/{activity_name}/signup`
- `styles.css`: Minimal styling

**Backend** (`src/app.py`)
- FastAPI application with static file mounting
- `activities` dict: In-memory data store with activity details (description, schedule, max_participants, participants array)
- Root endpoint redirects to `/static/index.html`
- Two main REST endpoints:
  - `GET /activities`: Returns all activities as JSON
  - `POST /activities/{activity_name}/signup`: Appends email to activity's participants list (no validation for capacity or duplicate signups)

## Development Workflow

**Setup & Running:**
1. Install dependencies: `pip install -r requirements.txt` (FastAPI + Uvicorn)
2. From `src/` directory, run: `uvicorn app:app --reload`
3. Access application at `http://localhost:8000`

**Testing:** 
- Test framework configured in `pytest.ini`
- Test database behavior, API endpoints, and form submission flow

## Key Patterns & Conventions

1. **In-Memory Data Store**: The `activities` dict persists only during runtime; data resets on server restart. When adding features (filtering, validation), modify the data structure carefully.

2. **RESTful Design**: Activities are resources accessed via standard HTTP methods. New features should follow REST conventions.

3. **Direct DOM Manipulation**: Frontend uses vanilla JS with `document.getElementById/querySelector` patterns. Avoid introducing frameworks unless necessary.

4. **Error Handling Gap**: Signup endpoint doesn't validate capacity or prevent duplicate emails—improvements should maintain backward compatibility.

## Common Tasks

- **Add activity field**: Update dict structure in `activities` + add corresponding HTML/JS display logic
- **Enhance signup**: Add validation in POST handler and corresponding frontend feedback
- **Styling changes**: Modify `src/static/styles.css` directly
- **New endpoints**: Follow FastAPI pattern in `app.py` (decorator + function)
