# Event Management API

This API allows managing companies, events, and event registrations. It provides endpoints for listing, creating, updating, and deleting companies and events, as well as handling event registrations for participants, organizers, and admins.

## Features

- **Company Management**: CRUD operations for managing companies, including social media details.
- **Event Management**: CRUD operations for managing events, with functionality for organizers and admins.
- **Event Registration**: Create, list, and update event registrations based on user roles (admin, organizer, participant).

## Endpoints

### Companies

- `GET /companies/list/` - List all companies
- `POST /companies/create/` - Create a new company
- `GET /companies/{slug}/` - Retrieve a specific company by slug
- `PUT /companies/{slug}/` - Update a company by slug
- `PATCH /companies/{slug}/` - Partially update a company by slug
- `DELETE /companies/{slug}/` - Delete a company by slug

### Events

- `GET /events/` - List all events
- `POST /events/create/` - Create a new event
- `GET /events/{id}/` - Retrieve a specific event by ID
- `PUT /events/{id}/` - Update an event by ID
- `PATCH /events/{id}/` - Partially update an event by ID
- `DELETE /events/{id}/` - Delete an event by ID

### Event Registrations

- `GET /registrations/list/` - List all event registrations based on user role
- `POST /registrations/create/` - Create a new event registration
- `PUT /registrations/{id}/update/` - Update an event registration

## Authentication

The API requires authentication. Only authenticated users can perform actions like creating events, registering for events, or managing company data.

### Authentication Methods

- **JWT Token Authentication**: Users must pass an authentication token in the header for every request.
  
  Example:
  ```bash
  Authorization: Bearer <your-token>
  ```

## Permissions

The API uses custom permissions to manage access based on user roles. 

- **IsAdminOrReadOnly**: Only admins can create, update, or delete companies and events. All users can view.
- **IsEventOrganizerOrAdminUserOrReadOnly**: Only event organizers or admins can create, update, or delete events.
- **IsOrganizerOrAdminUser**: Only organizers or admins can update event registrations.
- **IsParticipantOrAdminUser**: Only participants or admins can create registrations.

## Custom Management Commands

The project includes custom management commands to quickly create data for testing or development purposes. These commands can be run using the `python manage.py` syntax.

### Available Commands

- `python manage.py create_topics` - Create predefined topics for events.
- `python manage.py create_users --count <num> --role participant` - Create users with the role of `participant`.
- `python manage.py create_users --count <num> --role organizer` - Create users with the role of `organizer`.
- `python manage.py create_companies --count <num>` - Create companies.
- `python manage.py create_events --count <num>` - Create events.
- `python manage.py create_event_registrations --count <num>` - Create event registrations.
- `python manage.py initialize_data` - Initialize all necessary data for development (calls the above commands).

These commands help set up a mock environment with sample data, making it easier to test the API during development.

## Usage with Docker

This project is configured to run with Docker, which simplifies the process of setting up the development environment. Below are the steps to run the project using Docker.

### Prerequisites

Make sure you have [Docker](https://www.docker.com/get-started) installed on your machine.

### Running the Project

1. Clone the repository to your local machine:
   ```bash
   git clone <repository-url>
   cd <project-folder>
   ```

2. Build and run the Docker containers:
   ```bash
   docker-compose up --build
   ```

   This command will build the Docker images and start the application, including:
   - The Django web application.
   - A PostgreSQL database.
   - Celery workers for asynchronous tasks.


## API Documentation

The API uses drf-spectacular for generating and serving OpenAPI schema documentation. You can view the auto-generated API docs at:

- `http://localhost:8000/schema/` `http://localhost:8000/api/schema/swagger-ui/` - OpenAPI schema documentation
