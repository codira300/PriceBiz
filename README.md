# PriceBiz

**Making prices more transparent across Africa.**

PriceBiz is a price intelligence platform designed to help consumers and businesses across Africa make informed pricing decisions through location-based price information for everyday products and services.

Starting in Nigeria, PriceBiz aims to make it easier to discover, compare, and validate prices across different markets and locations. By turning price observations into actionable insights, the platform seeks to help consumers understand prevailing market prices, help businesses assess their pricing decisions, and improve access to reliable local price information.

Our long-term vision is to build a trusted source of price intelligence that makes markets more transparent, empowers better purchasing decisions, and supports data-driven commerce across Africa.

## Table of Contents

- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [Objectives](#objectives)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Problem Statement

Prices for everyday products and services can vary significantly across markets, sellers, and geographical locations. However, reliable and accessible information about these differences is often difficult to obtain, particularly in markets where many transactions take place through informal channels and local retailers have limited online visibility.

This lack of accessible price information can make it difficult for consumers to determine whether a quoted price is reasonable and for businesses to evaluate their pricing decisions against prevailing market conditions.

PriceBiz aims to address this challenge by providing a platform for collecting, organizing, analyzing, and presenting location-based price information.

## Objectives

PriceBiz aims to:

- **Improve price transparency:** Make local price information easier to discover and understand.
- **Support informed purchasing:** Help consumers compare observed prices across locations.
- **Enable pricing decisions:** Give businesses insights into observed market prices.
- **Build local price intelligence:** Organize price observations into useful, location-specific information.
- **Support African markets:** Begin with Nigeria and build toward broader coverage across Africa.

## Key Features

PriceBiz is being developed around the following capabilities:

- **Product discovery:** Find products and their associated price information.
- **Location-based price information:** Explore observed prices across supported geographical areas.
- **Price analysis:** Generate insights from available price observations.
- **Community contributions:** Support the collection of price information from different sources.
- **Price discussions and feedback:** Provide mechanisms for users to engage with price-related information.
- **Data validation and moderation:** Help maintain the quality and reliability of submitted information.

Feature availability may vary as development progresses.

## Technology Stack

### Backend
- Python
- FastAPI
- MongoDB
- Pydantic
- `uv` for Python project and dependency management

### Frontend
- React
- TypeScript
- Vite
- Tailwind CSS

### Development Tools
- Git and GitHub for version control and source hosting
- Automated testing tools appropriate to the backend and frontend

## Project Structure

The project is organized into separate backend and frontend applications.

```text
PriceBiz/
├── backend/
│   ├── app/
│   │   ├── controllers/
│   │   ├── routes/
│   │   ├── services/
│   │   └── ...
│   ├── pyproject.toml
│   ├── requirements.txt
│   └── uv.lock
├── frontend/
│   ├── app/
│   ├── public/
│   ├── package.json
│   └── ...
├── .gitignore
└── README.md
```

The directory listing above is representative; individual files and directories may differ as the project evolves.

## Getting Started

### Prerequisites

Install the following tools before setting up PriceBiz:

- Python version supported by the backend configuration
- Node.js and npm
- MongoDB, either locally or through a managed deployment
- `uv` for Python dependency management
- Git

### Clone the Repository

```bash
git clone https://github.com/codira300/PriceBiz.git
cd PriceBiz
```

### Backend Setup

```bash
cd backend
uv sync
```

Configure the required environment variables before starting the backend.

### Frontend Setup

Open a separate terminal:

```bash
cd frontend
npm install
```

## Configuration

PriceBiz uses environment variables for configuration and sensitive settings.

Create the required local environment files based on the variables expected by each application. Keep credentials, database connection strings, signing keys, and other secrets out of version control.

**Important:** Never commit real `.env` files or expose backend secrets in frontend environment variables.

## Running the Application

Start the backend from the `backend` directory using the development command configured for the project. For example, if the FastAPI application is exposed as `app.main:app`:

```bash
uv run uvicorn app.main:app --reload
```

Start the frontend from the `frontend` directory:

```bash
npm run dev
```

Use the local URLs printed by each development server to access the application.

## API Documentation

PriceBiz uses FastAPI for its backend API. When the application is running, interactive API documentation is typically available at:

- Swagger UI: `/docs`
- ReDoc: `/redoc`

These endpoints depend on the application's FastAPI configuration and whether documentation has been enabled.

## Testing

Run the tests configured for each application before submitting changes.

For the backend, from the `backend` directory:

```bash
uv run pytest
```

For the frontend, check the available scripts in `frontend/package.json`:

```bash
npm run
```

Run the configured test, lint, and build scripts as appropriate. A successful application build does not, by itself, establish that all features and integrations work correctly.

## Contributing

Contributions that improve price-data quality, application reliability, security, accessibility, and user experience are welcome.

1. Fork the repository or create a feature branch.
2. Make a focused change.
3. Add or update tests where appropriate.
4. Run the relevant checks.
5. Submit a pull request describing the change and its purpose.

Please do not include credentials, private user data, or other sensitive information in commits or issue reports.

## License

The project's license has not yet been specified. Until a license is added to the repository, do not assume that the source code is available for unrestricted reuse or redistribution.